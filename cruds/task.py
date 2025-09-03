#!/usr/bin/env python
# coding: utf-8
# @File    :   task.py
# @Time    :   2025/09/02 17:18:34
# @Author  :   toddlerya
# @Desc    :   None


from database_models.models import TaskInfo
from utils.db import Database, insert_or_update


def save_task_info(db_handler: Database, task_info_data: dict) -> tuple[bool, str]:
    """
    存储任务信息
    Args:
        db_handler:
        field_dg_rule_cache_data:
    Returns:

    """
    return insert_or_update(db=db_handler, model_name=TaskInfo, record=task_info_data)
