#!/usr/bin/env python
# coding: utf-8
# @Time     : 2024/11/20 17:22
# @Author   : guoqun X2590
# @FileName : dynamic_query.py
# @Project  : HETUTaskChecker

from typing import Any, Dict, List, Tuple

from fastapi.encoders import jsonable_encoder
from sqlalchemy import text

from utils.db_manager import DatabaseManager


def query_safe_check(sql: str) -> Tuple[bool, list]:
    """
    SQL安全检查
    Args:
        sql:

    Returns:

    """
    status = True
    forbid_key_words = (
        "DELETE",
        "UPDATE",
        "INSERT",
        "CREATE",
        "DROP",
        "GRAND",
        "ALTER",
    )
    format_sql_list = sql.upper().strip().split()
    forbid_result = []
    for each in format_sql_list:
        if each in forbid_key_words:
            forbid_result.append(each)
            status = False
    return status, forbid_result


def query_sql(
    db_manager: DatabaseManager, sql_text: str, max_count: int = 9999999999999
) -> tuple[bool, str, List[Dict[str, Any]]]:
    """
    动态查询SQL
    Args:
        sql_text:
        max_count:
        db:

    Returns:

    """
    try:
        result = db_manager.get_session().execute(text(sql_text))
    except Exception as err:
        message = f"动态查询SQL执行错误! SQL: {sql_text}, 错误信息: {err}"
        return False, message, []
    else:
        rows = [dict(zip(result.keys(), row)) for row in result.fetchall()[:max_count]]
        return True, "ok", jsonable_encoder(rows)


if __name__ == "__main__":
    import time

    sql = "SELECT * FROM recommend_pangu_field_info WHERE dictkey IS NOT null limit 10;"
    with DatabaseManager() as db_manager:
        status, msg, data = query_sql(sql_text=sql, max_count=5, db_manager=db_manager)
        print(status)
        print(msg)
        print(data)

    time.sleep(30)
