#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/11 15:05 
# @Author   : guoqun X2590
# @FileName : dg_rule_lru.py
# @Project  : DataForge


from sqlalchemy import and_
from sqlalchemy.orm import Session
from typing import Tuple, Optional

from utils.db import Database
from database_models.models import FieldDGRuleCache
from database_models.schema import FieldDGRuleCacheSchema


def save_field_dg_rule(db_handler: Database, field_dg_rule_cache_data: dict) -> tuple[bool, str]:
    """
    存储字段的DG规则
    Args:
        db_handler:
        field_dg_rule_cache_data:
    Returns:

    """
    try:
        db_handler.insert_or_update(FieldDGRuleCache, **field_dg_rule_cache_data)
    except Exception as err:
        db_handler.session.rollback()
        message = f"数据库写操作错误: {err}"
        return False, message
    return True, "ok"


def query_field_dg_rule(
        db_handler: Database,
        ename: str,
        cname: str = "",
        field_type_name: str = ""
) -> Tuple[bool, str, Optional[FieldDGRuleCache]]:
    """
    根据字段英文名查询字段的DG规则缓存
    Args:
        db_handler: SQLAlchemy 的 Session 实例
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
        query = db_handler.session.query(FieldDGRuleCache).filter_by(ename=ename)
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


