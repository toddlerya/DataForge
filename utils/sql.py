#!/usr/bin/env python
# coding: utf-8
# @File    :   sql.py
# @Time    :   2024/4/2 11:01
# @Author  :   guo qun X2590
# @Desc    :   None


from typing import  Tuple


def query_safe_check(sql: str) -> Tuple[bool, list]:
    """
    SQL安全检查
    Args:
        sql:

    Returns:

    """
    status = True
    forbid_key_words = ("DELETE", "UPDATE", "INSERT", "CREATE", "DROP", "GRAND", "ALTER")
    format_sql_list = sql.upper().strip().split()
    forbid_result = list()
    for each in format_sql_list:
        if each in forbid_key_words:
            forbid_result.append(each)
            status = False
    return status, forbid_result
