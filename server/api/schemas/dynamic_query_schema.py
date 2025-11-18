#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/15 16:45
# @Author   : guoqun X2590
# @Desc     :


from pydantic import BaseModel, ConfigDict, Field


class DynamicQuerySchema(BaseModel):
    """
    工具任务运行结果概览信息定义
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    sql: str = Field(..., description="执行查询的SQL语句")
    max_count: int = Field(default=20, gt=0, description="工具任务执行检测数据")
