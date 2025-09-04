#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/12 16:58
# @Author   : guoqun X2590
# @FileName : pre_heat_llm_dg_rule_cache.py
# @Project  : DataForge

import uuid

from agent.data_graph import data_gen_graph
from agent.state import DataGenUserIntentSchema
from config import PRESET_FIXED_PANGU_DG_RULE_PATH
from cruds.dynamic_query import query_sql
from utils.db import Database
from utils.file import load_yaml_from_file
from utils.log import logger


def preset_fixed_dg_rule(db_handler: Database):
    """
    初始化预置固化的字段DG规则
    Args:
        db_handler:

    Returns:

    """
    for yaml_file in [PRESET_FIXED_PANGU_DG_RULE_PATH]:
        load_message, yaml_data = load_yaml_from_file(yaml_file_path=yaml_file)
        if load_message != "ok":
            logger.error(f"读取数据异常! yaml_file={yaml_file} error: {load_message}")
            continue
        logger.info(yaml_data)
    # cache_dg_rule(db_handler=db_handler)


async def pre_heat_llm_recommendation_dg_rule(db_handler: Database):
    """
    预热盘古字段的LLM推荐DG规则
    Args:
        db_handler:

    Returns:

    """
    logger.info("根据盘古元数据预热字段")
    query_dict_field_status, query_dict_field_message, dict_field_en_name_slice = (
        query_sql(
            db=db_handler, sql_text="SELECT table_en_name FROM table_meta_data_info"
        )
    )
    if query_dict_field_status is False:
        logger.error(f"获取有表英文名异常: {query_dict_field_message}")
        return False
    for dict_field_en_name in dict_field_en_name_slice:
        logger.info(f"当前预热表信息: {dict_field_en_name}")
        table_en_name = dict_field_en_name["table_en_name"]
        user_intent = DataGenUserIntentSchema(
            table_en_names=[table_en_name], table_data_count={table_en_name: 1}
        )

        session_id = uuid.uuid4().hex
        init_state = {
            "user_input": user_intent.model_dump_json(),
            "user_intent": user_intent,
            "human_intent_feedback": "正确",
            "max_retries": 2,
            "session_id": session_id,
            "client_ip": "0.0.0.0",
            "pre_heat_mode": True,
        }
        thread = {"configurable": {"thread_id": session_id}}
        event = await data_gen_graph.ainvoke(init_state, thread, stream_mode="values")


def run_data_graph_preheat():
    import asyncio

    asyncio.run(pre_heat_llm_recommendation_dg_rule(db_handler=Database()))


if __name__ == "__main__":
    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="DataForgePreHeatDGRules.log",
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))

    init_env()

    session_id = uuid.uuid4().hex

    traced_logger = TracedLogger()
    # 如果没有初始化trace_uuid则初始化trace_token
    token = traced_logger.set_trace_uuid(session_id)

    run_data_graph_preheat()

    traced_logger.reset_trace_uuid(token)
