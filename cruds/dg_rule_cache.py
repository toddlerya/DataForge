#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/11 15:05
# @Author   : guoqun X2590
# @FileName : dg_rule_lru.py
# @Project  : DataForge


from typing import Optional, Tuple

from database_models.models import FieldDGRuleCache
from utils.db_manager import DatabaseManager, GenericUpsert


def save_field_dg_rule(
    db_manager: DatabaseManager,
    field_dg_rule_cache_data: dict,
) -> tuple[bool, str]:
    """
    存储字段的DG规则
    Args:
        db_manager:
        field_dg_rule_cache_data:
    Returns:

    """
    try:
        GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(),
            model_class=FieldDGRuleCache,
            data=field_dg_rule_cache_data,
        )
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"数据库写操作错误: {err}"
        return False, message
    return True, "ok"


def query_field_dg_rule(
    db_manager: DatabaseManager, ename: str, cname: str = "", field_type_name: str = ""
) -> Tuple[bool, str, Optional[FieldDGRuleCache]]:
    """
    根据字段英文名查询字段的DG规则缓存
    Args:
        db_manager:
        ename: 字段英文名称（必填）
        cname: 字段出现次数最多的中文名称（可选）
        field_type_name: 字段类型（可选）
    Returns:
        Tuple[bool, str, Optional[FieldDGRuleCache]]:
            - 第一个元素：查询是否成功（True/False）
            - 第二个元素：错误信息或成功信息
            - 第三个元素：查询到的 FieldDGRuleCache 实例或 None
    """
    try:
        # 基础查询
        query = db_manager.get_session().query(FieldDGRuleCache).filter_by(ename=ename)
        # 可选条件判断
        if cname:
            query = query.filter_by(cname=cname)
        if field_type_name:
            query = query.filter_by(field_type_name=field_type_name)
        # 执行查询
        result = query.first()
        return True, "ok", result
    except Exception as e:
        return False, f"查询失败: {str(e)}", None


if __name__ == "__main__":
    db_manager = DatabaseManager()
    query_status, query_message, query_result = query_field_dg_rule(
        db_manager=db_manager, ename="GROUPID", cname="群号", field_type_name="string"
    )
    print(query_status)
    print(query_message)
    print(query_result)
    db_manager.close()
