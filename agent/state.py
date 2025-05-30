#!/usr/bin/env python
# coding: utf-8
# @File    :   state.py
# @Time    :   2025/05/08 15:43:55
# @Author  :   toddlerya
# @Desc    :   None


from typing import Annotated, Dict, List, Optional, TypedDict, Union

from langchain_core.messages import ToolMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from database_models.schema import TableRawFieldSchema


class UserIntentSchema(BaseModel):
    table_en_names: List[str] = Field(..., description="表英文名称, 不可为空")
    table_conditions: Dict[str, str] = Field(description="表字段的约束条件", default={})
    table_data_count: Dict[str, int] = Field(
        ..., description="表期望生成的数据条数，不可为空"
    )


class TableFieldDefintion(TypedDict):
    en_name: str
    cn_name: str
    # 字段类型, e.g., "INT", "VARCHAR", "DATE", "BOOLEAN"
    field_type: str
    # 字段样例值
    sample_value: str
    # 字段约束条件列表, e.g., ["age > 18", "name is not null"]
    constraints: List[str]


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
    # output_fields: dict = Field(
    #     description="输出字段信息", alias="output_fields", default={}
    # )
    # map_tool_fields_info: List[Dict[str, str]] = Field(
    #     description="映射生成工具字段信息", alias="map_fields_info", default=[]
    # )
    # mapping_confirmed: bool = Field(
    #     description="映射是否完成", default=False, alias="mapping_confirmed"
    # )
    # map_count: int = Field(description="映射字段个数", default=-1, alias="map_count")
    # no_map_count: int = Field(
    #     description="未映射字段个数", default=-1, alias="no_map_count"
    # )
    # human_update_count: int = Field(
    #     description="人工修正映射字段个数", default=-1, alias="human_update_count"
    # )


class OutputDataStructureSchema(BaseModel):
    data: Union[BaseModel]


class DataForgeState(MessagesState):
    user_input: str
    user_intent: UserIntentSchema
    confirmed: bool
    table_metadata_array: list[TableMetadataSchema]
    table_metadata_error: list[str]
    fake_data: dict[str, list]
    current_retries: int
    max_retries: int


if __name__ == "__main__":
    print(UserIntentSchema().__annotations__)
