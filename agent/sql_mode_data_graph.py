#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/9 16:54 
# @Author   : guoqun X2590
# @FileName : sql_mode_data_graph.py
# @Project  : DataForge


import json
import time
import uuid
from urllib.parse import urljoin

import httpx
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from config import DG_PLAN_PATH, DG_PAYLOAD_PATH
from agent.llm import chat_llm
from agent.prompt import dg_category_prompt, sql_mode_data_intent_prompt
from agent.state import (
    DataGenState,
    PydanticDataGeniusCategoryRecommendation,
    PydanticDataGeniusPlan,
    PydanticDataGeniusRule,
    TableMetadataSchema,
    DataGenSQLModeUserIntentSchema,
    SQLModeDataGenState,
    SQLModeFieldSchema,
    SQLModeTableInfoSchema
)
from agent.sql_parser import advanced_column_lineage_parser
from config import DG_PLAN_CONFIG_PREFIX, PROJECT_PATH
from cruds.table_metadata import table_metadata_query
from database_models.schema import TableRawFieldSchema
from agent.dg_configs import (
    DG_FIELD_CATEGORY_CONFIG,
    DG_STORAGE_PATH,
    DG_SERVER_BASE_URL,
    DG_TASK_ADD_URL,
    DG_TASK_HISTORY,
    DG_NEW_TASK,
)
from utils.db import Database
from utils.file import save_dict2jl


def analyze_data_intent(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    解析用户意图，SQL模式
    :param state:
    :return:
    """
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {user_input} human_intent_feedback: {human_intent_feedback}"
    )
    structured_llm = chat_llm.with_structured_output(DataGenSQLModeUserIntentSchema)
    chat_prompt = sql_mode_data_intent_prompt.format_messages(
        user_input=user_input, human_intent_feedback=human_intent_feedback
    )
    logger.trace(f"analyze_intent chat_prompt: {chat_prompt}")
    user_intent = structured_llm.invoke(chat_prompt)
    state["user_intent"] = user_intent
    logger.debug(f"user_intent: {user_intent}")
    return state


def data_intent_human_feedback_node():
    """No-op node that should be interrupted on"""
    pass


def should_data_intent_continue(state: SQLModeDataGenState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确":
        return "sql_parse_to_table_info"

    # Otherwise proceed to create table info
    return "analyze_intent"


def sql_parse_to_table_info(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    解析SQL为表结构JSON
    :param state:
    :return:
    """
    user_intent = state.get("user_intent")
    result, error = advanced_column_lineage_parser(user_intent.sql)
    logger.error(error)
    logger.info("result", result)
    if error:
        table_info_error = f"解析SQL异常: {error}"
        state["table_info_error"] = table_info_error
        return state
    try:
        table_info = SQLModeTableInfoSchema(**result)
        logger.info(f"table_info: {table_info.model_dump_json()}")
        state["table_info_data"] = table_info
    except Exception as err:
        table_info_error = f"SQL生成表结构化信息异常: {err}"
        state["table_info_error"] = table_info_error
        return state
    return state


sql_mode_data_gen_builder = StateGraph(SQLModeDataGenState)
sql_mode_data_gen_builder.add_node("analyze_intent", analyze_data_intent)
sql_mode_data_gen_builder.add_node("intent_human_feedback_node", data_intent_human_feedback_node)
sql_mode_data_gen_builder.add_node("sql_parse_to_table_info", sql_parse_to_table_info)

sql_mode_data_gen_builder.add_edge(START, "analyze_intent")
sql_mode_data_gen_builder.add_edge("analyze_intent", "intent_human_feedback_node")
sql_mode_data_gen_builder.add_conditional_edges(
    "intent_human_feedback_node",
    should_data_intent_continue,
    ["analyze_intent", "sql_parse_to_table_info"],
)

sql_mode_data_gen_builder.add_edge("sql_parse_to_table_info", END)

memory = MemorySaver()
sql_mode_data_gen_graph = sql_mode_data_gen_builder.compile(
    interrupt_before=["intent_human_feedback_node"], checkpointer=memory
)

if __name__ == '__main__':
    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH

    from utils.log import LogManager

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="DataForgeSQLModeDataGenApp.log",
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))
    init_env()

    print(sql_mode_data_gen_graph.get_graph(xray=True).draw_mermaid())
    user_input = """SQL内容(必填): select	F859 as F2079, F860 as F2085, F861 as F2091, F862 as F2097, STR_SRC_IP as F2103, F863 as F2109, STR_DST_IP as F2115, F864 as F2121, F865 as F2127, F866 as F2133, F867 as F2139, F868 as F2145, F869 as F2151, F870 as F2157, F871 as F2163, F872 as F2169, F873 as F2175, F874 as F2181, F875 as F2187, F876 as F2193, F877 as F2199, PASSWORD as F2205, TITLE as F2211, ARTICLE_ID as F2217, CONTENT_S as F2223, F878 as F2229, F879 as F2235	massdata.NB_MASS_RESOURCE_REGISTER	as node_1
    期望生成数据条数(必填): 100"""
    session_id = "12345"
    thread = {"configurable": {"thread_id": session_id}}
    init_state = {
        "user_input": user_input,
        "max_retries": 5,
        "client_ip": "10.0.23.57",
        "session_id": session_id
    }
    for event in sql_mode_data_gen_graph.stream(init_state, thread, stream_mode="values"):
        user_intent: DataGenSQLModeUserIntentSchema = event.get("user_intent")
        if user_intent:
            logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")
    # 模拟用户意图识别的研判反馈
    sql_mode_data_gen_graph.update_state(thread, {"human_intent_feedback": "正确"}, as_node="intent_human_feedback_node")
    for event in sql_mode_data_gen_graph.stream(None, thread, stream_mode="values"):
        # Review
        human_intent_feedback = event.get("human_intent_feedback")
        if human_intent_feedback:
            logger.info(f"human_intent_feedback: {human_intent_feedback}")

        if event.get("table_info_error"):
            logger.info("table_info_error", event["table_info_error"])

        if event.get("table_info_data"):
            logger.info("table_info_data", event["table_info_data"])
