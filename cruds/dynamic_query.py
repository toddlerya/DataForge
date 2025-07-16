#!/usr/bin/env python
# coding: utf-8
# @Time     : 2024/11/20 17:22 
# @Author   : guoqun X2590
# @FileName : dynamic_query.py
# @Project  : HETUTaskChecker

from typing import Any, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import text

from utils.db import Database


def query_sql(db: Database, sql_text: str, max_count: int = 9999999999999) -> tuple[bool, str, None] | tuple[
    bool, str, Any]:
    """
    动态查询SQL
    Args:
        sql_text:
        max_count:
        db:

    Returns:

    """
    try:
        result = db.session.execute(text(sql_text))
    except Exception as err:
        db.session.rollback()
        message = f"动态查询SQL执行错误! SQL: {sql_text}, 错误信息: {err}"
        return False, message, None
    else:
        rows = [dict(zip(result.keys(), row)) for row in result.fetchall()[:max_count]]
        return True, "ok", jsonable_encoder(rows)


if __name__ == '__main__':
    # sql = "SELECT * FROM health_check_system_case_status_info"
    sql = "SELECT * FROM health_check_system_case_status_info WHERE task_id = '1712025699iCBffgV4zBog35XYzx4dpD'"
    status, msg, data = query_sql(sql_text=sql, max_count=5, db=Database())
    print(status)
    print(msg)
    print(data)
