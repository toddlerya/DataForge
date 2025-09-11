#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/16 10:48
# @Author   : guoqun X2590
# @FileName : table_metadata.py
# @Project  : DataForge

from typing import Tuple

from database_models.models import TableMetaDataInfo
from utils.db_manager import DatabaseManager, GenericUpsert


def table_metadata_query_by_entity_id(
    entity_id: str, db_manager: DatabaseManager
) -> Tuple[bool, str, TableMetaDataInfo | None]:
    """
    查询表元数据信息
    Args:
        entity_id:
        db_handler:

    Returns:

    """
    try:
        result = (
            db_manager.get_session()
            .query(TableMetaDataInfo)
            .filter(TableMetaDataInfo.remark == entity_id)
            .one_or_none()
        )
    except Exception as err:
        message = f"数据库读操作异常: {err}"
        return False, message, None
    else:
        return True, "ok", result


def table_metadata_save(record: dict, db_manager: DatabaseManager) -> Tuple[bool, str]:
    """
    存储数据
    Args:
        record:
        db_handler:

    Returns:

    """
    try:
        GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(), model_class=TableMetaDataInfo, data=record
        )
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"数据库写操作异常: {err}"
        return False, message
    else:
        db_manager.get_session().commit()
        return True, "ok"


def table_metadata_query(
    table_en_name: str, db_manager: DatabaseManager
) -> Tuple[bool, str, TableMetaDataInfo | None]:
    """
    查询数据
    Args:
        table_en_name:
        db_handler:

    Returns:

    """
    try:
        result = (
            db_manager.get_session()
            .query(TableMetaDataInfo)
            .filter(TableMetaDataInfo.table_en_name.like(table_en_name))
            .one_or_none()
        )
    except Exception as err:
        message = f"数据库查询异常: {err}"
        return False, message, None
    else:
        return True, "ok", result


if __name__ == "__main__":
    table_en_name = "massdata.adm_labelatt_rlt"
    inner_db_manager = DatabaseManager()
    query_status, query_message, query_result = table_metadata_query(
        table_en_name=table_en_name, db_manager=inner_db_manager
    )
    print(query_status)
    print(query_message)
    inner_db_manager.get_session().close()
