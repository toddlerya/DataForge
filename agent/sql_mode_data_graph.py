#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/9 16:54
# @Author   : guoqun X2590
# @FileName : sql_mode_data_graph.py
# @Project  : DataForge


import json
import uuid
from copy import deepcopy

from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.dg_api_client import create_dg_task, query_dg_task_status
from agent.dg_configs import DG_FIELD_CATEGORY_CONFIG as BASE_DG_FIELD_CATEGORY_CONFIG
from agent.dg_rule_processor import dg_rule_processor
from agent.llm import chat_llm
from agent.prompt import sql_mode_data_intent_prompt
from agent.sql_parser import parse_simple_select
from agent.state import (
    DataGenSQLModeUserIntentSchema,
    PydanticDataGeniusCategoryRecommendation,
    SQLModeDataGenState,
    SQLModeTableInfoSchema,
    TableMetadataSchema,
    TableRawFieldSchema,
    init_dg_category_config,
)
from config import DG_PLAN_PATH
from cruds.pangu import (
    query_dict_items_info_by_dictkey,
    query_field_recommend_info_by_ename,
)
from database_models.schema import RecommendPanGuDictSchema
from utils.db import Database
from utils.file import save_dict2jl


def detect_input_type(state: SQLModeDataGenState):
    """
    判断用户输入的是结构化任务参数还是自然语言任务需求
    :param state:
    :return:
    """
    user_intent: DataGenSQLModeUserIntentSchema = state.get("user_intent")
    if user_intent:
        return "sql_parse_to_table_info"
    else:
        return "analyze_intent"


def analyze_data_intent(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    解析用户意图，SQL模式
    :param state:
    :return:
    """
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {user_input} "
        f"human_intent_feedback: {human_intent_feedback}"
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
    if human_intent_feedback == "正确" or human_intent_feedback == "Y":
        return "sql_parse_to_table_info"

    # Otherwise proceed to create table info
    return "analyze_intent"


def sql_parse_to_table_info(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    解析SQL为表结构JSON
    :param state:
    :return:
    """
    logger.info("[+] 解析SQL为表结构JSON")
    user_intent = state.get("user_intent")
    user_sql = user_intent.sql
    logger.info(f"用户提供的SQL: {user_sql}")
    status, error, result = parse_simple_select(user_sql)
    if status is False or not result:
        table_info_error = f"解析SQL异常! error={error} result={result}"
        logger.error(table_info_error)
        state["table_info_error"] = table_info_error
        return state
    try:
        logger.debug(f"sql parse result: {result}")
        table_info = SQLModeTableInfoSchema(
            table_en_name=list(result.keys())[0],
            fields_info=result[(list(result.keys())[0])],
        )
        logger.debug(f"table_info: {table_info.model_dump_json()}")
        state["table_info_data"] = table_info
    except Exception as err:
        table_info_error = f"SQL生成表结构化信息异常: {err}"
        logger.error(table_info_error)
        state["table_info_error"] = table_info_error
        return state
    return state


def rag_sql_table_filed_info(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    根据字段知识库增强字段信息
    :param state:
    :return:
    """
    logger.info("RAG增强字段属性信息")
    table_info_data: SQLModeTableInfoSchema = state["table_info_data"]
    DG_FIELD_CATEGORY_CONFIG = deepcopy(BASE_DG_FIELD_CATEGORY_CONFIG)
    table_metadata_info = TableMetadataSchema(
        table_en_name=table_info_data.table_en_name
    )
    table_metadata_error: list[str] = []
    table_dict_category_code_map: dict[str, str] = {}
    table_dictkey_map: dict[str, list[RecommendPanGuDictSchema]] = {}
    db_handler = Database()
    for each_field in table_info_data.fields_info:
        status, message, recommend_data = query_field_recommend_info_by_ename(
            db_handler=db_handler, field_en_name=each_field.en_name
        )
        if status is False:
            err_message = (
                f"RAG增强字段属性异常: table_en_name={table_info_data.table_en_name} "
                f"field_en_name={each_field.en_name} ERROR: {message}"
            )
            logger.error(err_message)
            table_metadata_error.append(err_message)
        if recommend_data is None:
            raw_field_data = TableRawFieldSchema(en_name=each_field.en_name)
            table_metadata_info.raw_fields_info.append(raw_field_data)
        else:
            raw_field_data = TableRawFieldSchema(
                en_name=each_field.en_name,
                cn_name=recommend_data.cname,
                desc=[recommend_data.description if recommend_data.description else ""][
                    0
                ],
                field_type=recommend_data.field_type_name,
                is_require=recommend_data.is_required,
                dict_key=[recommend_data.dictkey if recommend_data.dictkey else ""][0],
            )
            if recommend_data.dictkey:
                dict_status, dict_message, dict_result = (
                    query_dict_items_info_by_dictkey(
                        db_handler=db_handler,
                        dictkey_with_nlevel=recommend_data.dictkey,
                    )
                )
                if dict_status is False:
                    logger.error(f"获取盘古字典异常: {dict_message}")
                elif dict_result:
                    one_dict = dict_result[0]
                    category = one_dict.dict_category
                    if category not in table_dict_category_code_map:
                        table_dict_category_code_map[category] = (
                            one_dict.dictkey_with_nlevel
                        )
                        value = one_dict.model_dump()
                        value.pop("uuid")
                        value.pop("dictkey_with_nlevel")
                        value.pop("dict_category_code")
                        value.pop("dict_category")
                        logger.info(f"将盘古字典添加到DG规则配置中: {category}")
                        config_value = {
                            "category": category,
                            "value": json.dumps(value, ensure_ascii=False),
                        }
                        DG_FIELD_CATEGORY_CONFIG.append(config_value)
                        table_dictkey_map[category] = dict_result
                        raw_field_data.dict_name = category
            table_metadata_info.raw_fields_info.append(raw_field_data)
    state["table_metadata_info"] = table_metadata_info
    state["table_metadata_error"] = table_metadata_error
    state["table_dict_category_code_map"] = table_dict_category_code_map
    state["table_dictkey_map"] = table_dictkey_map
    state["DG_FIELD_CATEGORY_CONFIG"] = DG_FIELD_CATEGORY_CONFIG
    # 动态更新配置
    init_dg_category_config.DG_FIELD_CATEGORY_CONFIG = DG_FIELD_CATEGORY_CONFIG
    # 如果已经生成过实例了，需要清空缓存更新
    PydanticDataGeniusCategoryRecommendation.reset_allowed_categories()
    return state


def save_dg_plan2json(state: SQLModeDataGenState):
    """
    存储DG执行计划任务配置
    Args:
        state:

    Returns:

    """
    logger.info("存储DataGenius任务规则")
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    table_metadata_info: TableMetadataSchema = state.get("table_metadata_info")
    if pydantic_data_genius_plan:
        data = pydantic_data_genius_plan.model_dump()
        save_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}.json"
        ).absolute()
        save_dict2jl(json_data=data, save_path=str(save_json_path))
    if table_metadata_info:
        table_metadata_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}_table_metadata.json"
        )
        save_dict2jl(
            json_data=table_metadata_info.model_dump(),
            save_path=table_metadata_json_path,
        )
    return state


sql_mode_data_gen_builder = StateGraph(SQLModeDataGenState)
sql_mode_data_gen_builder.add_node("analyze_intent", analyze_data_intent)
sql_mode_data_gen_builder.add_node(
    "intent_human_feedback_node", data_intent_human_feedback_node
)
sql_mode_data_gen_builder.add_node("sql_parse_to_table_info", sql_parse_to_table_info)
sql_mode_data_gen_builder.add_node("rag_sql_table_filed_info", rag_sql_table_filed_info)
sql_mode_data_gen_builder.add_node("dg_category_recommend", dg_rule_processor)
sql_mode_data_gen_builder.add_node("save_dg_plan2json", save_dg_plan2json)
sql_mode_data_gen_builder.add_node("create_dg_task", create_dg_task)
sql_mode_data_gen_builder.add_node("query_dg_task_status", query_dg_task_status)

sql_mode_data_gen_builder.add_conditional_edges(
    START, detect_input_type, ["sql_parse_to_table_info", "analyze_intent"]
)
sql_mode_data_gen_builder.add_edge("analyze_intent", "intent_human_feedback_node")
sql_mode_data_gen_builder.add_conditional_edges(
    "intent_human_feedback_node",
    should_data_intent_continue,
    ["analyze_intent", "sql_parse_to_table_info"],
)
sql_mode_data_gen_builder.add_edge(
    "sql_parse_to_table_info", "rag_sql_table_filed_info"
)
sql_mode_data_gen_builder.add_edge("rag_sql_table_filed_info", "dg_category_recommend")
sql_mode_data_gen_builder.add_edge("dg_category_recommend", "save_dg_plan2json")
sql_mode_data_gen_builder.add_edge("save_dg_plan2json", "create_dg_task")
sql_mode_data_gen_builder.add_edge("create_dg_task", "query_dg_task_status")
sql_mode_data_gen_builder.add_edge("query_dg_task_status", END)

memory = MemorySaver()
sql_mode_data_gen_graph = sql_mode_data_gen_builder.compile(
    interrupt_before=["intent_human_feedback_node"], checkpointer=memory
)

if __name__ == "__main__":
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
    user_input = """SQL内容(必填): select MD_ID, ACCOUNTNAME, USERNUM, USERID, MOBILE,
     NICKNAME, REGIS_TIME, REGISIP, REGISIPID, REGISIP_LOCATION, REGISIPPORT,
     REGISIP_PROVINCIAL_CODE, REGISIP_CITY_CODE, REGISIP_COUNTRY_CODE,
     REGISIP_REGIONAL_CODE, PACKAGENAME, CAPTURE_TIME, ACTIONTYPE, ACTIONTIME
     from XY_BF_ACCOUNT
    期望生成数据条数(必填): 100"""
    session_id = uuid.uuid4().hex
    thread: RunnableConfig = {"configurable": {"thread_id": session_id}}
    init_state = {
        "user_input": user_input,
        "user_intent": DataGenSQLModeUserIntentSchema(
            **{
                "sql": """select MD_ID, ACCOUNTNAME, USERNUM, USERID, MOBILE, NICKNAME,
                 REGIS_TIME, REGISIP, REGISIPID, REGISIP_LOCATION, REGISIPPORT,
                 REGISIP_PROVINCIAL_CODE, REGISIP_CITY_CODE, REGISIP_COUNTRY_CODE,
                 REGISIP_REGIONAL_CODE, PACKAGENAME, CAPTURE_TIME, ACTIONTYPE,
                 ACTIONTIME from XY_BF_ACCOUNT""",
                "data_count": 100,
            }
        ),
        "human_intent_feedback": "正确",
        "max_retries": 5,
        "client_ip": "10.0.23.57",
        "session_id": session_id,
    }
    for event in sql_mode_data_gen_graph.stream(
        init_state, thread, stream_mode="values"
    ):
        user_intent: DataGenSQLModeUserIntentSchema = event.get("user_intent")
        if user_intent:
            logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")
        # Review
        human_intent_feedback = event.get("human_intent_feedback")
        if human_intent_feedback:
            logger.info(f"human_intent_feedback: {human_intent_feedback}")
        table_info_error = event.get("table_info_error")
        if table_info_error:
            logger.info(f"table_info_error: {table_info_error}")

        table_info_data: SQLModeTableInfoSchema = event.get("table_info_data")
        if table_info_data:
            logger.info(f"table_info_data: {table_info_data.model_dump_json()}")

        table_metadata_info = event.get("table_metadata_info")
        if table_metadata_info:
            logger.info(f"table_metadata_info: {table_metadata_info.model_dump_json()}")

        table_metadata_error = event.get("table_metadata_error")
        if table_metadata_error:
            logger.info(f"table_metadata_error: {table_metadata_error}")

        table_dict_category_code_map = event.get("table_dict_category_code_map")
        if table_dict_category_code_map:
            logger.info(f"table_dict_category_code_map: {table_dict_category_code_map}")

        create_data_genius_task_error = event.get("create_data_genius_task_error")
        if create_data_genius_task_error:
            logger.info(
                f"create_data_genius_task_error: {create_data_genius_task_error}"
            )

        query_data_genius_task_error = event.get("query_data_genius_task_error")
        if query_data_genius_task_error:
            logger.info(f"query_data_genius_task_error: {query_data_genius_task_error}")

        data_genius_plan_run_duration = event.get("data_genius_plan_run_duration")
        if data_genius_plan_run_duration:
            logger.info(
                f"data_genius_plan_run_duration: {data_genius_plan_run_duration}"
            )

        data_genius_plan_output_url = event.get("data_genius_plan_output_url")
        if data_genius_plan_output_url:
            logger.info(f"data_genius_plan_output_url: {data_genius_plan_output_url}")

        data_genius_plan_output_filesize = event.get("data_genius_plan_output_filesize")
        if data_genius_plan_output_filesize:
            logger.info(
                f"data_genius_plan_output_filesize: {data_genius_plan_output_filesize}"
            )
