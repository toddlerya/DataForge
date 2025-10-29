#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/16 17:34
# @Author   : guoqun X2590
# @Desc     : 任务录入和查询接口

import json
import pathlib
import uuid
from copy import deepcopy

from fastapi import APIRouter, Depends
from loguru import logger

from cruds.task import query_task_info_by_cnodition, save_task_info
from database_models.schema import PydanticDataGeniusRule, TaskDataSchema
from server.api.depends import get_db_manager
from server.api.schemas.base_schema import ResponseBaseSchema
from utils.db_manager import DatabaseManager
from utils.err_code import error_code

router = APIRouter(
    prefix="/task",
    tags=["任务管理"],
    responses={404: {"description": "Not Found"}},
)


dg_task_status_message_map = {0: "成功", 1: "异常", -1: "未知"}


def compare_task_rule(
    left_rule_array: list[dict], right_rule_array: list[dict]
) -> tuple[bool, str, dict[str, list[dict]]]:
    """分析比对两个规则的变更内容

    Args:
        left_rule_array (list[dict]): _description_
        right_rule_array (list[dict]): _description_

    Returns:
        _type_: _description_
    """
    result = {}
    # 先校验格式
    try:
        left_rule_data = [PydanticDataGeniusRule(**ele) for ele in left_rule_array]
    except Exception as err:
        message = f"左侧规则数组格式校验不通过: {err}"
        return False, message, result
    try:
        right_rule_data = [PydanticDataGeniusRule(**ele) for ele in right_rule_array]
    except Exception as err:
        message = f"右侧规则数组格式校验不通过: {err}"
        return False, message, result
    # 比对变化策略, 按照 ename为参照, 比对删, 改, 增
    # 这他妈不是莱文斯坦编辑距离么...先简单点吧
    # 先看看改了哪些
    modify_group: list[dict[str, dict[str, dict]]] = []
    add_group: list[dict] = []
    del_group: list[dict] = []
    # 用于记录右侧规则中哪些已被匹配（避免重复）
    matched_right_ename = set()
    for left_element in left_rule_data:
        right_matched_elements = [
            ele for ele in right_rule_data if ele.ename == left_element.ename
        ]
        if right_matched_elements:
            if len(right_matched_elements) == 1:
                right_element = right_matched_elements[0]
                if (
                    # 规则类别修改了
                    left_element.category != right_element.category
                    # 规则参数修改了
                    or left_element.args != right_element.args
                    # 规则名称修改了
                    or left_element.name != right_element.name
                ):
                    matched_element = {
                        left_element.ename: {
                            "before": left_element.model_dump(),
                            "after": right_element.model_dump(),
                            "change": {
                                "category": {
                                    "before": left_element.category,
                                    "after": right_element.category,
                                },
                                "args": {
                                    "before": left_element.args,
                                    "after": right_element.args,
                                },
                                "name": {
                                    "before": left_element.name,
                                    "after": right_element.name,
                                },
                            },
                        }
                    }
                    modify_group.append(matched_element)
                # 标记已匹配
                matched_right_ename.add(left_element.ename)
            else:
                logger.warning(
                    f"左侧字段规则匹配中多个右侧字段规则: "
                    f"left_element={left_element.model_dump()}"
                    f"right_matched_elements="
                    f"{[ele.model_dump() for ele in right_matched_elements]}"
                )
        else:
            # 计算右侧比左侧新增了哪些字段规则，存入add_group
            # 左侧有，右侧无 → 删除
            del_group.append(left_element.model_dump())

    # 计算右侧比左侧删除了哪些字段规则，存入del_group
    # 遍历右侧规则，找出未被匹配的（即新增）
    for right_element in right_rule_data:
        if right_element.ename not in matched_right_ename:
            add_group.append(right_element.model_dump())

    result["modify_group"] = modify_group
    result["add_group"] = add_group
    result["del_group"] = del_group
    if result["add_group"] == result["del_group"] == result["modify_group"] == []:
        # 没有变化置为空
        result = {}
    logger.debug(f"result={json.dumps(result, ensure_ascii=False)}")
    return True, "ok", result


@router.post("/add", response_model=ResponseBaseSchema)
async def add_task_info(
    task_data_json: dict, db_manager: DatabaseManager = Depends(get_db_manager)
):
    resp_data = ResponseBaseSchema(description="新增任务信息")
    task_type_data = {"task_type": "HUMAN-CREATE"}
    logger.debug(
        f"task.add ==> task_data_json: {json.dumps(task_data_json, ensure_ascii=False)}"
    )
    rule_url_path = task_data_json.get("rule_url_path", "")
    rule_name = pathlib.Path(rule_url_path).name.split(".json")[0]
    ai_task_id = task_data_json.get("third_ai_task_id", "")
    dg_task_id = task_data_json.get("task_id", "")
    data_row_count = task_data_json.get("rows", 0)
    client_ip = task_data_json.get("ip", "127.0.0.1")
    current_task_rule = task_data_json.get("rules", [{}])
    dg_task_status = task_data_json.get("code", -1)
    dg_task_message = dg_task_status_message_map.get(dg_task_status, "")
    dg_task_type = task_data_json.get("type_", "")
    dg_task_duration = task_data_json.get("duration", "") or ""
    # 只有在DG第一次创建任务是时生成唯一dg_task_id, 后续修改任务规则此dg_task_id不会改变
    if rule_name and "dg_task_plan_" in rule_name:
        # dg_task_plan_存在说明说明是AI-DG任务经过人工修改后的DG回调更新的任务
        task_type_data = {"task_type": "AI-HUMAN-MODIFIED"}
    if ai_task_id:
        # 存在ai_task_id说明是AI-DG创建的规则，可能人工修改过
        task_type_data = {"task_type": "AI-HUMAN-MODIFIED"}
    # 查询数据库中此dg任务id是否存在
    query_condition = {}
    if ai_task_id:
        query_condition = {"task_uuid": ai_task_id}
    else:
        query_condition = {"dg_task_id": dg_task_id}
    query_status, query_message, lastest_task_data = query_task_info_by_cnodition(
        db_manager=db_manager, **query_condition
    )
    if query_status is False:
        logger.error(f"查询当前任务历史记录信息异常: {query_message}")
    else:
        if lastest_task_data and lastest_task_data.task_rule is not None:
            # 更新模式
            # 以上一次的任务为基准，来更新任务信息入库
            # 需要更新的是task_rule和user_modified_rules信息
            # 但是上一次任务的last_task_data是ORM类型，需要注意处理
            lastest_task_data_dict = deepcopy(lastest_task_data).to_dict()
            # 移除数据库的一些字段构建TaskDataSchema对象
            lastest_task_data_dict.pop("id")
            lastest_task_data_dict.pop("remark")
            lastest_task_data_dict.pop("create_time")
            lastest_task_data_dict.pop("update_time")
            lastest_task_data_dict["dg_task_type"] = dg_task_type
            lastest_task_data_dict["update_task_rule"] = current_task_rule
            task_data = TaskDataSchema(**lastest_task_data_dict)
            # 更新下client_ip
            task_data.client_ip = client_ip
            task_data.data_row_count = data_row_count
            task_data.dg_task_id = dg_task_id
            task_data.dg_task_message = dg_task_message
            logger.info(
                f"找到已有的任务信息, 更新模式 "
                f"task_uuid={task_data.task_uuid} "
                f"dg_task_id={task_data.dg_task_id} "
                f"开始分析人工修改规则内容"
            )
            # 分析对比改动的规则内容
            compare_status, compare_message, compare_result = compare_task_rule(
                left_rule_array=task_data.task_rule,
                right_rule_array=task_data.update_task_rule,
            )
            if compare_status is False:
                logger.error(
                    f"规则比对异常! 当前task_uuid={task_data.task_uuid} "
                    f"dg_task_id={task_data.dg_task_id} "
                    f"ERROR: {compare_message}"
                )
            else:
                task_data.user_modified_rules = compare_result
            logger.info(
                f"{task_type_data} ==> client_ip={task_data.client_ip} "
                f"task_uuid={task_data.task_uuid} "
                f"dg_task_id={task_data.dg_task_id} "
                f"dg_task_edit_url={task_data.dg_task_edit_url} "
                f"user_modified_rules={task_data.user_modified_rules}"
            )
        else:
            # 新增模式的
            task_uuid = uuid.uuid4().hex
            logger.info(
                f"新增任务记录模式 task_uuid={task_uuid} dg_task_id={dg_task_id} "
            )
            task_data = TaskDataSchema(
                task_uuid=task_uuid,
                table_en_name=task_data_json.get("modelName", "").replace(
                    "测试部仿真测试环境-", ""
                ),
                data_row_count=data_row_count,
                client_ip=client_ip,
                rule_name=rule_name,
                task_rule=current_task_rule,
                dg_task_status=dg_task_status,
                dg_task_message=dg_task_message,
                dg_task_id=dg_task_id,
                dg_task_duration=dg_task_duration,
                dg_task_type=dg_task_type,
            )
        # 入库存储
        task_info_data = task_data.model_dump()
        logger.debug(f"save to db task_info_data={task_data.model_dump_json()}")
        save_status, save_message = save_task_info(
            db_manager=db_manager, task_info_data=task_info_data
        )
        if save_status is False:
            logger.error(save_message)
            resp_data.code = error_code.DB_INSERT_OR_UPDATE_ERROR.get("code")
            resp_data.message = (
                error_code.DB_INSERT_OR_UPDATE_ERROR.get("description", "")
                + " "
                + save_message
            )
    resp_data.data = task_type_data
    return resp_data.model_dump()
