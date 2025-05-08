#!/usr/bin/env python
# coding: utf-8
# @File    :   gen_faker_data_agent.py
# @Time    :   2025/05/08 16:33:12
# @Author  :   toddlerya
# @Desc    :   None

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import chat_llm
from agent.state import DataForgeState


def gen_faker_data_agent(state: DataForgeState) -> dict:
    user_intent = state.get("user_intent", {})
    table_en_names = user_intent.get("table_en_names", [])
    table_conditions = user_intent.get("table_conditions", {})
    table_data_count = user_intent.get("table_data_count", {})
    table_metadata = state.get("table_metadata", [])
