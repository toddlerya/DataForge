#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/16 17:34
# @Author   : guoqun X2590
# @Desc     : 任务录入和查询接口


from typing import Any, cast

from fastapi import APIRouter, Depends
from loguru import logger

from cruds.task import query_task_info_by_cnodition, save_task_info
from database_models.schema import PydanticDataGeniusRule
from server.api.depends import get_db_manager
from server.api.schemas.base_schema import ResponseBaseSchema
from server.api.schemas.task_schema import TaskPayloadSchmea
from utils.db_manager import DatabaseManager
from utils.err_code import error_code

router = APIRouter(
    prefix="/task",
    tags=["任务管理"],
    responses={404: {"description": "Not Found"}},
)


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
                matched_element = {
                    left_element.ename: {
                        "befor": left_element.model_dump(),
                        "after": right_element.model_dump(),
                        "change": {
                            "category": {
                                "befor": left_element.category,
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
                logger.debug(f"modify_group.matched_element: {matched_element}")
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
    return True, "ok", result


@router.post("/add", response_model=ResponseBaseSchema)
async def add_task_info(
    task_data: TaskPayloadSchmea, db_manager: DatabaseManager = Depends(get_db_manager)
):
    resp_data = ResponseBaseSchema(description="新增任务信息")
    task_type_data = {"task_type": "HUMAN-CREATE"}
    logger.debug(f"task.add ==> task_data: {task_data.model_dump()}")
    # TODO: 需要根据DG修改来调整服务接口了,
    # 只有在DG第一次创建任务是时生成唯一dg_task_id, 后续修改任务规则此dg_task_id不会改变
    if task_data.parent_dg_task_id and task_data.parent_rule_name:
        # 这两个字段有值说明是AI-DG任务经过人工修改后新建的任务
        task_type_data = {"task_type": "AI-HUMAN-MODIFIED"}
        query_status, query_message, parent_task_data = query_task_info_by_cnodition(
            db_manager=db_manager,
            dg_task_id=task_data.parent_dg_task_id,
            rule_name=task_data.rule_name,
        )
        if query_status is False:
            logger.error(f"查询当前任务的父任务信息异常: {query_message}")
        else:
            # 分析对比改动的规则内容
            if parent_task_data and parent_task_data.task_rule is not None:
                logger.info(
                    f"找到父任务信息, "
                    f"parent_dg_task_id={task_data.parent_dg_task_id} "
                    f"parent_rule_name={task_data.parent_rule_name} "
                    f"开始分析人工修改规则内容, 当前task_uuid={task_data.task_uuid}"
                )
                # Column[Any] 转换为 list[dict]
                parent_task_rule = cast(
                    list[dict[str, Any]], parent_task_data.task_rule
                )
                compare_status, compare_message, compare_result = compare_task_rule(
                    left_rule_array=parent_task_rule,
                    right_rule_array=task_data.task_rule,
                )
                if compare_status is False:
                    logger.error(
                        f"规则比对异常! 当前task_uuid={task_data.task_uuid} "
                        f"parent_dg_task_id={task_data.parent_dg_task_id} "
                        f"parent_rule_name={task_data.parent_rule_name} "
                        f"ERROR: {compare_message}"
                    )
                else:
                    task_data.user_modified_rules = compare_result
    logger.info(
        f"{task_type_data} ==> client_ip={task_data.client_ip} "
        f"task_uuid={task_data.task_uuid}"
        f"dg_task_edit_url={task_data.dg_task_edit_url}"
        f"user_modified_rules={task_data.user_modified_rules}"
    )
    # 入库存储
    task_info_data = task_data.model_dump()
    task_info_data.pop("parent_dg_task_id")
    task_info_data.pop("parent_rule_name")
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
