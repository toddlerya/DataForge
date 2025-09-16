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
    user_intent: dict = Field(default={}, description="用户意图")
    mode: int = Field(
        default=0, description="任务模式[0:未知 1: 元数据模式 2: SQL解析模式]"
    )
    client_ip: str = Field(default="127.0.0.1", description="客户端IP")
    task_payload: dict = Field(default={}, description="创建任务请求的请求体JSON")
    rule_name: str = Field(default="", description="任务规则名称")
    task_rule: dict = Field(default={}, description="任务规则配置JSON")
    dg_task_status: int = Field(
        default=-1, description="DG任务状态: 0正常,1异常,-1未知"
    )
    dg_task_message: str = Field(default="", description="DG任务状态信息")
    dg_task_id: str = Field(default="", description="DG的任务ID")
    dg_task_edit_url: str = Field(default="", description="DG任务的编辑URL")
    dg_task_rule_data_preview: list[dict] = Field(
        default=[{}], description="DG规则的预览数据"
    )
    dg_task_duration: str = Field(default="", description="DG任务耗时")
    user_modified_rules: dict = Field(default={}, description="用户修改的字段规则")
    env_name: str = Field(default="", description="环境名称")
