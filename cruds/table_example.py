#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/23 16:36
# @Author   : guoqun X2590
# @FileName : table_example.py
# @Project  : DataForge


from loguru import logger
from typing import Union, Tuple

from database_models.models import TableExampleDataInfo
from utils.db import Database


def table_example_save(record: dict, db_handler: Database) -> Tuple[bool, str]:
    """
    存储数据
    Args:
        record:
        db_handler:

    Returns:

    """
    try:
        db_handler.insert_or_update(TableExampleDataInfo, **record)
    except Exception as err:
        db_handler.session.rollback()
        message = f"数据库写操作异常: {err}"
        return False, message
    else:
        db_handler.session.commit()
        return True, "ok"
