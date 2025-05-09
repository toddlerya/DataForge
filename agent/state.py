#!/usr/bin/env python
# coding: utf-8
# @File    :   state.py
# @Time    :   2025/05/08 15:43:55
# @Author  :   toddlerya
# @Desc    :   None


from typing import Dict, List

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field


class UserIntentSchema(BaseModel):
    table_en_names: List[str] = Field(description="表英文名称", default=[])
    table_conditions: Dict[str, str] = Field(description="表字段的约束条件", default={})
    table_data_count: Dict[str, int] = Field(
        description="表期望生成的数据条数", default={}
    )


class TableRawFieldSchema(BaseModel):
    cn_name: str = Field(description="字段中文名称", default="")
    en_name: str = Field(description="字段英文名称", default="")
    desc: str = Field(description="字段描述", default="")
    field_type: str = Field(description="字段类型", default="")


class TableMetadataSchema(BaseModel):
    table_en_name: str = Field(
        description="表英文名称", alias="table_en_name", default=""
    )
    table_cn_name: str = Field(
        description="表中文名称", alias="table_cn_name", default=""
    )
    raw_fields_info: List[TableRawFieldSchema] = Field(
        description="原始字段信息", alias="raw_fields_info", default=[]
    )
    output_fields: List[str] = Field(
        description="输出字段信息", alias="output_fields", default=[]
    )
    map_tool_fields_info: List[Dict[str, str]] = Field(
        description="映射生成工具字段信息", alias="map_fields_info", default=[]
    )
    mapping_confirmed: bool = Field(
        description="映射是否完成", default=False, alias="mapping_confirmed"
    )
    map_count: int = Field(description="映射字段个数", default=-1, alias="map_count")
    no_map_count: int = Field(
        description="未映射字段个数", default=-1, alias="no_map_count"
    )
    human_update_count: int = Field(
        description="人工修正映射字段个数", default=-1, alias="human_update_count"
    )


class DataForgeState(MessagesState):
    user_input: str
    user_intent: UserIntentSchema
    table_metadata: List[TableMetadataSchema]
    confirmed: bool
