#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/16 17:38
# @Author   : guoqun X2590
# @Desc     : 任务信息结构


from pydantic import BaseModel, ConfigDict, Field


class TaskSchmea(BaseModel):
    """
    任务信息定义
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    task_uuid: str = Field(
        ..., description="任务唯一ID, 与session_uuid, trace_uuid一致"
    )
    table_en_name: str = Field(..., description="表英文名称")
    data_row_count: int = Field(default=0, description="任务生成的数据条数")
