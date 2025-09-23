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
        entity_id = str(entity_id)
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
        db_manager.get_session().commit()
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"数据库写操作异常: {err}"
        return False, message
    else:
        return True, "ok"


def table_metadata_query(
    table_en_name: str, env_name: str, db_manager: DatabaseManager
) -> Tuple[bool, str, TableMetaDataInfo | None]:
    """
    查询数据
    Args:
        table_en_name:
        env_name:
        db_handler:

    Returns:

    """
    try:
        query = db_manager.get_session().query(TableMetaDataInfo)
        # 添加 table_en_name 条件
        query = query.filter(TableMetaDataInfo.table_en_name == table_en_name)
        if env_name and env_name.strip():
            # 如果 env_name 不为空字符串，则添加 env_name 条件
            query = query.filter(TableMetaDataInfo.env_name == env_name.strip())
        result = query.one_or_none()
    except Exception as err:
        message = f"数据库读操作异常: {err}"
        return False, message, None
    else:
        return True, "ok", result


def table_metadata_fuzzy_query(
    table_name: str, env_name: str, db_manager: DatabaseManager
) -> tuple[bool, str, list[TableMetaDataInfo]]:
    """模糊查询表名称

    Args:
        table_name (str): _description_
        env_name (str): _description_
        db_manager (DatabaseManager): _description_

    Returns:
        tuple[bool,str, list[TableMetaDataInfo]]: _description_
    """
    try:
        query = db_manager.get_session().query(TableMetaDataInfo)
        env_name = env_name.strip()
        if env_name:
            # 如果 env_name 不为空字符串，则添加 env_name 条件
            query = query.filter(TableMetaDataInfo.env_name == env_name)

        # 模糊查询条件：支持表英文名或中文名的模糊匹配
        table_name = table_name.strip()
        if table_name:
            # 构造模糊查询条件：table_en_name 或 table_cn_name 包含 table_name
            like_condition = TableMetaDataInfo.table_en_name.ilike(
                f"%{table_name}%"
            ) | TableMetaDataInfo.table_cn_name.ilike(f"%{table_name}%")
            query = query.filter(like_condition)
        # 执行查询
        results = query.all()
    except Exception as err:
        message = f"数据库读操作异常: {err}"
        return False, message, []
    else:
        return True, "ok", results


if __name__ == "__main__":
    table_en_name = "massdata.ODS_SOC_WEGH_USER_ELECO_INFO"
    env_name = "测试部仿真测试环境"
    inner_db_manager = DatabaseManager()
    query_status, query_message, query_result = table_metadata_query(
        table_en_name=table_en_name, env_name=env_name, db_manager=inner_db_manager
    )
    print(f"inner_db_manager: {inner_db_manager.db._engine}")
    print(f"query_status: {query_status}")
    print(f"query_message: {query_message}")
    print(f"query_result: {query_result.to_dict() if query_result else {}}")
    inner_db_manager.get_session().close()
