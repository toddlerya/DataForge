#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/16 17:34
# @Author   : guoqun X2590
# @Desc     : 任务录入和查询接口


from fastapi import APIRouter, Depends

from server.api.depends import get_db_manager
from server.api.schemas.base_schema import ResponseBaseSchema
from server.api.schemas.task_schema import TaskSchmea
from utils.db_manager import DatabaseManager

router = APIRouter(
    prefix="/task",
    tags=["任务管理"],
    responses={404: {"description": "Not Found"}},
)


@router.post("/add", response_model=ResponseBaseSchema)
def add_task_info(
    task_data: TaskSchmea, db_manager: DatabaseManager = Depends(get_db_manager)
):
    resp_data = ResponseBaseSchema(description="新增任务信息")

    return resp_data.model_dump()
