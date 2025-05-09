#!/usr/bin/env python
# coding: utf-8
# @File    :   gen_faker_data_agent.py
# @Time    :   2025/05/08 16:33:12
# @Author  :   toddlerya
# @Desc    :   None

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.llm import chat_llm
from agent.prompt import prompt_gen_faker_data
from agent.state import DataForgeState, UserIntentSchema


def gen_faker_data_agent(state: DataForgeState) -> dict:
    user_intent = state.get("user_intent", UserIntentSchema())
    table_en_names = user_intent.table_en_names
    table_conditions = user_intent.table_conditions
    table_data_count = user_intent.table_data_count
    table_metadata = state.get("table_metadata", [])

    logger.debug(f"table_en_names: {table_en_names}")
    logger.debug(f"table_conditions: {table_conditions}")
    logger.debug(f"table_data_count: {table_data_count}")
    logger.debug(f"table_metadata: {table_metadata}")

    # 生成测试数据
    # structured_llm = chat_llm.with_structured_output(dict)
    system_message = prompt_gen_faker_data.format(
        table_en_name_array=table_en_names,
        table_field_info_array=table_metadata,
        table_conditions_array=table_conditions,
        table_data_count_array=table_data_count,
    )
    logger.debug(f"system_message: {system_message}")
    faker_data = chat_llm.invoke(
        [
            system_message,
            "请根据表字段信息生成测试数据",
        ]
    )
    logger.debug(f"faker_data: {faker_data}")
    return {"faker_data": faker_data}


gen_faker_data_builder = StateGraph(DataForgeState)
gen_faker_data_builder.add_node("gen_faker_data_agent", gen_faker_data_agent)

gen_faker_data_builder.add_edge(START, "gen_faker_data_agent")
gen_faker_data_builder.add_edge("gen_faker_data_agent", END)

memory = MemorySaver()
gen_faker_data_graph = gen_faker_data_builder.compile(checkpointer=memory)
