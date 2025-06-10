#!/usr/bin/env python
# coding: utf-8
# @File    :   gen_faker_data_agent.py
# @Time    :   2025/05/08 16:33:12
# @Author  :   toddlerya
# @Desc    :   None

from typing import Literal
import json

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.llm import chat_llm
from agent.prompt import prompt_gen_faker_data
from agent.state import (
    DataForgeState,
)
from agent.utils import create_table_model, build_main_model


def handle_retry(state: DataForgeState) -> DataForgeState:
    """
    处理重试逻辑
    Args:
        state:

    Returns:

    """
    current_retries = state["current_retries"]
    max_retries = state["max_retries"]
    if current_retries >= max_retries:
        logger.warning(f"当前已到达最大重试次数: {max_retries}")
        state["current_retries"] = 0
        return state
    else:
        logger.warning(f"当前重试次数: {current_retries}")
        return state


def gen_fake_data(state: DataForgeState) -> DataForgeState:
    user_intent = state.get("user_intent")
    table_en_names = user_intent.table_en_names
    table_conditions = user_intent.table_conditions
    table_data_count = user_intent.table_data_count
    table_metadata_array = state.get("table_metadata_array", [])

    logger.debug(f"table_en_names: {table_en_names}")
    logger.debug(f"table_conditions: {table_conditions}")
    logger.debug(f"table_data_count: {table_data_count}")
    logger.debug(f"max_retries: {state.get('max_retries', 3)}")
    logger.debug(f"current_retries: {state.get('current_retries', 0)}")

    # 生成测试数据
    output_table_metadata_slice = list()
    for table_metadata in table_metadata_array:
        each_table_output_metadata = {
            "table_name": table_metadata.table_en_name,
            "fields": [ele.model_dump() for ele in table_metadata.raw_fields_info],
        }
        logger.trace(each_table_output_metadata)
        output_table_metadata_slice.append(each_table_output_metadata)
    output_table_models = {
        table.get("table_name"): create_table_model(
            table_name=table.get("table_name"), fields=table.get("fields")
        )
        for table in output_table_metadata_slice
    }
    output_data_schema = build_main_model(output_table_models)
    logger.trace(
        f"output_data_schema: {output_data_schema}  {json.dumps(output_data_schema.model_json_schema())}"
    )
    structured_llm = chat_llm.with_structured_output(output_data_schema)
    system_message = prompt_gen_faker_data.format(
        table_en_name_array=table_en_names,
        table_field_info_array=[ele.model_dump() for ele in table_metadata_array],
        table_conditions_array=table_conditions,
        table_data_count_array=table_data_count,
    )
    logger.trace(f"gen_fake_data system_message: {system_message}")
    try:
        fake_data = structured_llm.invoke(
            [
                system_message,
                "请根据表字段信息生成测试数据",
            ]
        )
    except Exception as err:
        logger.error(f"gen_fake_data structured_llm.invoke error: {err}")
        state["current_retries"] = state["current_retries"] + 1
        return state
    else:
        logger.debug(f"fake_data.model_dump_json: {fake_data.model_dump_json()}")
        # 追加数据
        last_fake_data = state.get("fake_data", {})
        logger.debug(f"current last_fake_data: {last_fake_data}")
        for k, v in fake_data.model_dump().items():
            if k in last_fake_data:
                last_fake_data[k].extend(v)
            else:
                last_fake_data[k] = v
        state["fake_data"] = last_fake_data
        state["current_retries"] = 0
        # return {"fake_data": last_fake_data}
        return state


def should_continue_gen(state: DataForgeState):
    """Return the next node to execute"""
    # logger.debug(f"should_continue_gen state: {state}")
    if state["current_retries"] >= state["max_retries"]:
        return "max_retries_reached"
    user_intent = state.get("user_intent")
    fake_data = state.get("fake_data", {})
    for table_en_name, except_data_count in user_intent.table_data_count.items():
        actual_gen_count = len(fake_data.get(table_en_name, []))
        logger.debug(
            f"should_continue_gen=> table_en_name={table_en_name} "
            f"except_data_count={except_data_count} actual_gen_count={actual_gen_count}"
        )
        if actual_gen_count < except_data_count:
            return "again"
    # Otherwise end
    return "finished"


gen_fake_data_builder = StateGraph(DataForgeState)
gen_fake_data_builder.add_node("gen_fake_data", gen_fake_data)
gen_fake_data_builder.add_node("handle_retry", handle_retry)

gen_fake_data_builder.add_edge(START, "gen_fake_data")
gen_fake_data_builder.add_conditional_edges(
    "gen_fake_data",
    should_continue_gen,
    {"again": "gen_fake_data", "max_retries_reached": "handle_retry", "finished": END},
)
gen_fake_data_builder.add_conditional_edges(
    "handle_retry",
    should_continue_gen,
    {"again": "gen_fake_data", "max_retries_reached": END, "finished": END},
)

memory = MemorySaver()
gen_fake_data_graph = gen_fake_data_builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print(gen_fake_data_graph.get_graph(xray=True).draw_mermaid())
