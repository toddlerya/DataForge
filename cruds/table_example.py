#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/23 16:36
# @Author   : guoqun X2590
# @FileName : table_example.py
# @Project  : DataForge


from typing import Tuple

from database_models.models import TableExampleDataInfo
from utils.db_manager import DatabaseManager, GenericUpsert


def table_example_save(record: dict, db_manager: DatabaseManager) -> Tuple[bool, str]:
    """
    存储数据
    Args:
        record:
        db_manager:

    Returns:

    """
    try:
        GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(),
            model_class=TableExampleDataInfo,
            data=record,
        )
    except Exception as err:
        message = f"数据库写操作异常: {err}"
        return False, message
    else:
        return True, "ok"
