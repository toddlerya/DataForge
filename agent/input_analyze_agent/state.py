# coding: utf-8
# @Time:     2025/5/8 11:06
# @Author:   toddlerya
# @FileName: state.py
# @Project:  DataForge

from typing import List, Dict

from pydantic import BaseModel, Field
from langgraph.graph import MessagesState


class UserIntentSchema(BaseModel):
    table_en_names: List[str] = Field(description="表英文名称")
    table_conditions: Dict[str, str] = Field(description="表字段的约束条件")
    table_data_count: Dict[str, int] = Field(description="表期望生成的数据条数")


class UserIntentState(MessagesState):
    user_input: str
    user_intent: UserIntentSchema
    confirmed: bool
