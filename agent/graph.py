#!/usr/bin/env python
# coding: utf-8
# @File    :   graph.py
# @Time    :   2025/06/03 15:34:28
# @Author  :   toddlerya
# @Desc    :   None


import json

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.llm import chat_llm, ollama_llm
from agent.prompt import (
    dg_category_prompt,
    faker_plan_prompt,
    intent_prompt,
    prompt_gen_faker_data,
)
from agent.state import (
    DataForgeState,
    PydanticDataGeniusCategoryRecommendation,
    PydanticFakerPlan,
    TableMetadataSchema,
    UserIntentSchema,
)
from agent.utils import build_main_model, create_table_model
from cruds.table_metadata import table_metadata_query
from database_models.schema import TableRawFieldSchema
from faker_utils.dg_configs import DG_FIELD_CATEGORY_CONFIG
from faker_utils.faker_cn_idcard import doc as faker_cn_idcard_doc
from utils.db import Database


def analyze_intent(state: DataForgeState) -> DataForgeState:
    messages = state.get("messages", [])
    user_input = messages[-1]
    state["user_input"] = user_input
    logger.debug(f"user_input: {user_input} messages: {messages}")
    structured_llm = chat_llm.with_structured_output(UserIntentSchema)

    chat_prompt = intent_prompt.format_messages(
        user_input=user_input, messages=messages
    )
    logger.debug(f"analyze_intent chat_prompt: {chat_prompt}")
    user_intent = structured_llm.invoke(chat_prompt)
    state["messages"].append(user_input)
    state["user_intent"] = user_intent
    logger.debug(f"user_intent: {user_intent}")
    return state


def confirm(state: DataForgeState):
    """Confirm node that sets default confirmed=False if not set"""
    if "confirmed" not in state:
        state["confirmed"] = False


def should_continue(state: DataForgeState):
    """Return the next node to execute"""

    # Check if human feedback
    confirmed = state.get("confirmed", False)
    if confirmed:
        return "analyze_intent"

    # Otherwise proceed to create table info
    return "create_table_raw_field_info"


def create_table_raw_field_info(state: DataForgeState) -> DataForgeState:
    if "table_metadata_array" not in state:
        state["table_metadata_array"] = []

    intent_table_en_names = state.get("user_intent", {}).table_en_names
    # 查询知识库获取表的字段配置信息

    for table_en_name in intent_table_en_names:
        table_metadata = TableMetadataSchema(table_en_name=table_en_name)
        query_status, query_message, query_result = table_metadata_query(
            table_en_name=table_en_name, db_handler=Database()
        )
        if query_status is False:
            logger.error(f"查询{table_en_name}元数据异常: {query_result}")
            state["table_metadata_error"].append(
                f"查询{table_en_name}元数据异常: {query_message}"
            )
            raw_fields_data = [TableRawFieldSchema()]
        elif query_result is None:
            logger.error(f"未查询到{table_en_name}元数据!")
            state["table_metadata_error"].append(f"未查询到{table_en_name}元数据!")
            raw_fields_data = [TableRawFieldSchema()]
        else:
            raw_fields_data = [
                TableRawFieldSchema(**ele)
                for ele in query_result.table_fields
                if isinstance(ele, dict)
            ]

        table_metadata.raw_fields_info = raw_fields_data

        state["table_metadata_array"].append(table_metadata)
    return state


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


def dg_planner(state: DataForgeState) -> DataForgeState:
    """
    数据生成规划器节点
    Args:
        state:

    Returns:

    """
    logger.info("数据生成规划器开始执行")
    table_metadata_array = state["table_metadata_array"]
    # user_intent = state["user_intent"]
    table_metadata = table_metadata_array[0] if table_metadata_array else None
    if not table_metadata:
        logger.error("未查询到表元数据，无法进行数据生成规划")
        state["error_message"] = "未查询到表元数据，无法进行数据生成规划"
        return state
    structured_llm = ollama_llm.with_structured_output(
        PydanticDataGeniusCategoryRecommendation
    )
    for field_info in table_metadata.raw_fields_info:
        chat_prompt = dg_category_prompt.format_messages(
            cn_name=field_info.cn_name,
            en_name=field_info.en_name,
            field_type=field_info.field_type,
            desc=field_info.desc,
            sample_value=field_info.example,
            dict_name=field_info.dict_name,
            dg_category_config_data=DG_FIELD_CATEGORY_CONFIG,
        )
        logger.debug(f"llm_dg_field_category_recommendation chat_prompt: {chat_prompt}")
        llm_dg_field_category_recommendation = structured_llm.invoke(chat_prompt)
        logger.debug(
            f"llm_dg_field_category_recommendation.model_dump_json(): {llm_dg_field_category_recommendation.model_dump_json()}"
        )
    # state["llm_faker_plan"] = llm_faker_plan
    return state


def faker_planner(state: DataForgeState) -> DataForgeState:
    """
    LLM规划器节点
    Args:
        state:

    Returns:

    """
    logger.info("Faker计划配置生成器开始执行")
    table_metadata_array = state["table_metadata_array"]
    user_intent = state["user_intent"]
    structured_llm = ollama_llm.with_structured_output(PydanticFakerPlan)
    chat_prompt = dg_category_prompt.format_messages(
        table_name=user_intent.table_en_names,
        table_schema=[ele.model_dump() for ele in table_metadata_array],
        user_conditions=user_intent.table_conditions,
        num_rows=user_intent.table_data_count,
        dg_category_config_data=[faker_cn_idcard_doc],
    )
    logger.debug(f"faker_planner chat_prompt: {chat_prompt}")
    llm_faker_plan = structured_llm.invoke(chat_prompt)
    logger.debug(
        f"llm_faker_plan.model_dump_json(): {llm_faker_plan.model_dump_json()}"
    )
    state["llm_faker_plan"] = llm_faker_plan
    return state


data_forge_builder = StateGraph(DataForgeState)
data_forge_builder.add_node("analyze_intent", analyze_intent)
data_forge_builder.add_node("confirm", confirm)
data_forge_builder.add_node("create_table_raw_field_info", create_table_raw_field_info)
data_forge_builder.add_node("dg_planner", dg_planner)
# data_forge_builder.add_node("gen_fake_data", gen_fake_data)
# data_forge_builder.add_node("handle_retry", handle_retry)


data_forge_builder.add_edge(START, "analyze_intent")
data_forge_builder.add_edge("analyze_intent", "confirm")
data_forge_builder.add_conditional_edges(
    "confirm", should_continue, ["analyze_intent", "create_table_raw_field_info"]
)
data_forge_builder.add_edge("create_table_raw_field_info", "dg_planner")
# data_forge_builder.add_conditional_edges(
#     "gen_fake_data",
#     should_continue_gen,
#     {
#         "again": "gen_fake_data",
#         "max_retries_reached": "handle_retry",
#         "finished": END,
#     },
# )
# data_forge_builder.add_conditional_edges(
#     "handle_retry",
#     should_continue_gen,
#     {"again": "gen_fake_data", "max_retries_reached": END, "finished": END},
# )
data_forge_builder.add_edge("dg_planner", END)

# memory = MemorySaver()
graph = data_forge_builder.compile(interrupt_before=["confirm"])


if __name__ == "__main__":
    print(graph.get_graph(xray=True).draw_mermaid())
