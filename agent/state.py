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
    table_en_names: List[str] = Field(description="表英文名称")
    table_conditions: Dict[str, str] = Field(description="表字段的约束条件")
    table_data_count: Dict[str, int] = Field(description="表期望生成的数据条数")


class TableRawFiled(BaseModel):
    cn_name: str = Field(description="字段中文名称", default="")
    en_name: str = Field(description="字段英文名称", default="")
    desc: str = Field(description="字段描述", default="")
    field_type: str = Field(description="字段类型", default="")


class DataForgeState(MessagesState):
    user_input: str
    user_intent: UserIntentSchema
    table_metadata: List[TableRawFiled]
    confirmed: bool


class TableFieldMapping(BaseModel):
    table_name: str = Field(description="表名称", alias="table_name")
    raw_fields_info: List[TableRawFiled] = Field(
        description="原始字段信息", alias="raw_fields_info"
    )
    output_fields: List[str] = Field(description="输出字段信息", alias="output_fields")
    map_tool_fields_info: List[Dict[str, str]] = Field(
        description="映射生成工具字段信息", alias="map_fields_info"
    )
    map_count: int = Field(description="映射字段个数", default=-1, alias="map_count")
    no_map_count: int = Field(
        description="未映射字段个数", default=-1, alias="no_map_count"
    )
    human_update_count: int = Field(
        description="人工修正映射字段个数", default=-1, alias="human_update_count"
    )


class TableFieldFillData(BaseModel):
    table_name: str = Field(description="表名称", alias="table_name")


class FieldMappingState(MessagesState):
    table_en_name: str
    table_cn_name: str
    raw_fields_info: List[TableRawFiled]
    output_fields: List[str]
    map_tool_fields_info: List[Dict[str, str]]
    # 人工判断反馈的内容
    human_mapping_feedback: str
    # 映射是否完成
    status: bool
    # 表的字段映射关系
    table_field_mapping: TableFieldMapping
