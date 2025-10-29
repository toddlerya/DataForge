#!/usr/bin/env python
# coding: utf-8
# @File    :   task.py
# @Time    :   2025/09/02 17:18:34
# @Author  :   toddlerya
# @Desc    :   None

from typing import Optional

from loguru import logger

from database_models.models import TaskInfo
from utils.db_manager import DatabaseManager, GenericUpsert


def save_task_info(
    db_manager: DatabaseManager, task_info_data: dict
) -> tuple[bool, str]:
    """
    存储任务信息
    Args:
        db_handler:
        field_dg_rule_cache_data:
    Returns:

    """
    try:
        GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(),
            model_class=TaskInfo,
            data=task_info_data,
            auto_commit=True,
        )
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"数据库写操作异常: {err}"
        return False, message
    else:
        return True, "ok"


def query_task_info_by_cnodition(
    db_manager: DatabaseManager,
    task_uuid: str = "",
    dg_task_id: str = "",
    rule_name: str = "",
) -> tuple[bool, str, Optional[TaskInfo]]:
    """根据task_uuid或者rule_name查询任务信息

    Args:
        db_manager (DatabaseManager): _description_
        task_uuid (str, optional): _description_. Defaults to "".
        dg_task_id (str, optional): _description_. Defaults to "".
        rule_name (str, optional): _description_. Defaults to "".

    Returns:
        tuple[bool, str, TaskInfo|None]: _description_
    """
    try:
        logger.trace(
            "query_task_info_by_task_uuid_or_rule_name("
            f"task_uuid={task_uuid}, dg_task_id={dg_task_id}, rule_name={rule_name})"
        )
        # 校验：至少一个参数不能为空
        if not task_uuid.strip() and not dg_task_id.strip() and not rule_name.strip():
            message = (
                "查询任务信息异常! "
                "task_uuid, dg_task_id, rule_name 均为空，至少需要提供一个非空值。"
            )
            return False, message, None
        query = db_manager.get_session().query(TaskInfo)
        if task_uuid and task_uuid.strip():
            query = query.filter(TaskInfo.task_uuid == task_uuid.strip())
        if dg_task_id and dg_task_id.strip():
            query = query.filter(TaskInfo.dg_task_id == dg_task_id.strip())
        if rule_name and rule_name.strip():
            query = query.filter(TaskInfo.rule_name == rule_name.strip())
        result = query.one_or_none()
    except Exception as err:
        message = (
            "查询任务信息异常! 查询条件: "
            f"task_uuid={task_uuid}, dg_task_id={dg_task_id}, rule_name={rule_name} "
            f"ERROR: {err}"
        )
        return False, message, None
    else:
        return True, "ok", result


if __name__ == "__main__":
    s, m, r = query_task_info_by_cnodition(
        db_manager=DatabaseManager(),
        task_uuid="de35d50b89da4bf5ab5fa58839f015c9",
        # dg_task_id="3de29d1c-ef6f-4530-b698-3269a139d0fb",
    )
    print(s)
    print(m)
    print(r)
