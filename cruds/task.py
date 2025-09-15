#!/usr/bin/env python
# coding: utf-8
# @File    :   task.py
# @Time    :   2025/09/02 17:18:34
# @Author  :   toddlerya
# @Desc    :   None


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
