#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/15 16:43
# @Author   : guoqun X2590
# @Desc     : 动态查询数据库服务

from fastapi import APIRouter, Depends
from loguru import logger

from cruds.dynamic_query import query_safe_check, query_sql
from server.api.depends import get_db_manager
from server.api.schemas.base_schema import ResponseBaseSchema
from server.api.schemas.dynamic_query import DynamicQuery
from utils.db_manager import DatabaseManager
from utils.err_code import error_code

router = APIRouter(
    prefix="/db",
    tags=["数据库查询"],
    responses={404: {"description": "Not Found"}},
)


@router.post("/dynamic_query", response_model=ResponseBaseSchema, tags=["dynamic"])
def dynamic_query(
    data: DynamicQuery, db_manager: DatabaseManager = Depends(get_db_manager)
):
    resp_data = ResponseBaseSchema(description="动态查询")
    logger.debug(
        f"router.dynamic_query ==> sql: {data.sql} max_count: {data.max_count}"
    )
    check_status, check_result = query_safe_check(sql=data.sql)
    if not check_status:
        resp_data.code = error_code.DB_SAFE_CHECK_ERROR.get("code")
        message: str = (
            "请检查SQL语句, 动态查询API禁止以下操作: "
            f"{' '.join(check_result)}, 非法SQL: {data.sql}"
        )
        resp_data.message = message
        logger.warning(message)
    else:
        db_status, db_message, db_result = query_sql(
            sql_text=data.sql, max_count=data.max_count, db_manager=db_manager
        )
        if db_status is False:
            db_message = f"动态查询SQL执行错误: {data.sql}, 错误信息: {db_message}"
            logger.error(db_message)
            resp_data.code = error_code.DB_SQL_EXECUTE_ERROR.get("code")
            resp_data.message = (
                error_code.DB_SQL_EXECUTE_ERROR.get("description", "")
                + " "
                + db_message
            )
        resp_data.data = db_result
    return resp_data.dict()
