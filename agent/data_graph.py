#!/usr/bin/env python
# coding: utf-8
# @File    :   data_graph.py
# @Time    :   2025/06/03 15:34:28
# @Author  :   toddlerya
# @Desc    :   None


import json
import uuid
from copy import deepcopy

from langchain_core.messages import ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.dg_api_client import create_dg_task, query_dg_task_status, save_task_info2db
from agent.dg_configs import DG_FIELD_CATEGORY_CONFIG as BASE_DG_FIELD_CATEGORY_CONFIG
from agent.dg_rule_processor import dg_rule_processor
from agent.llm import chat_llm
from agent.prompt import data_intent_prompt
from agent.state import (
    DataGenState,
    DataGenUserIntentSchema,
    PydanticDataGeniusCategoryRecommendation,
    TableMetadataSchema,
    init_dg_category_config,
)
from config import DG_PLAN_PATH, PROJECT_PATH
from cruds.pangu import (
    query_dict_items_info_by_dict_category,
    query_dict_items_info_by_dictkey,
)
from cruds.table_metadata import table_metadata_query
from database_models.schema import RecommendPanGuDictSchema, TableRawFieldSchema
from utils.db_manager import DatabaseManager
from utils.file import save_dict2jl


def detect_input_type(state: DataGenState):
    """
    判断用户输入的是结构化任务参数还是自然语言任务需求
    :param state:
    :return:
    """

    user_intent: DataGenUserIntentSchema = state.get("user_intent")
    if user_intent:
        return "query_table_raw_field_info"
    else:
        return "analyze_intent"


def analyze_data_intent(state: DataGenState) -> DataGenState:
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {user_input} "
        f"human_intent_feedback: {human_intent_feedback}"
    )
    structured_llm = chat_llm.with_structured_output(DataGenUserIntentSchema)
    chat_prompt = data_intent_prompt.format_messages(
        user_input=user_input, human_intent_feedback=human_intent_feedback
    )
    logger.trace(f"analyze_intent chat_prompt: {chat_prompt}")
    user_intent = structured_llm.invoke(chat_prompt)
    logger.info(f"user_intent: {user_intent} type: {type(user_intent)}")
    if isinstance(user_intent, DataGenUserIntentSchema):
        state["user_intent"] = user_intent
    state["mode"] = 1
    return state


def data_intent_human_feedback_node(state: DataGenState):
    """No-op node that should be interrupted on"""
    return state


def should_data_intent_continue(state: DataGenState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确" or human_intent_feedback == "Y":
        return "query_table_raw_field_info"

    # Otherwise proceed to create table info
    return "analyze_intent"


def should_table_raw_field_info_continue(state: DataGenState):
    table_metadata_error = state.get("table_metadata_error", [])
    if len(table_metadata_error) >= 1:
        logger.error(f"存在table_metadata_error: {' '.join(table_metadata_error)}")
        return END
    else:
        return "rag_sql_table_filed_info"


def query_table_raw_field_info(state: DataGenState) -> DataGenState:
    if "table_metadata_info" not in state:
        state["table_metadata_error"] = []

    table_en_name = state.get("user_intent", {}).table_en_name
    # 查询知识库获取表的字段配置信息

    table_metadata = TableMetadataSchema(table_en_name=table_en_name)
    db_manager = DatabaseManager()
    query_status, query_message, query_result = table_metadata_query(
        table_en_name=table_en_name, db_manager=db_manager
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
        # 重要：从 ORM 对象中提取字段值，而不是直接传 ColumnElement
        raw_fields_data = []
        for field_dict in query_result.table_fields:
            if not isinstance(field_dict, dict):
                continue
            # table_fields 是 JSON 字段，里面存储的是 dict，不是 ORM 对象！
            try:
                # 保证字段是基础类型，不是 ColumnElement
                raw_field = TableRawFieldSchema(
                    en_name=field_dict.get("en_name", ""),
                    cn_name=field_dict.get("cn_name", ""),
                    desc=field_dict.get("desc", ""),
                    field_type=field_dict.get("field_type", ""),
                    is_require=int(field_dict.get("is_require", 0)),
                    dict_key=field_dict.get("dict_key", ""),
                    dict_name=field_dict.get("dict_name", ""),
                    example=field_dict.get("example", ""),
                )
                raw_fields_data.append(raw_field)
            except Exception as e:
                logger.warning(f"解析字段数据失败: {field_dict}, 错误: {e}")
                raw_fields_data.append(TableRawFieldSchema())

    table_metadata.raw_fields_info = raw_fields_data

    state["table_metadata_info"] = table_metadata
    db_manager.close()
    return state


def rag_sql_table_filed_info(state: DataGenState) -> DataGenState:
    """
    根据字段知识库增强字段信息
    :param state:
    :return:
    """
    global dict_result
    logger.info("RAG增强字段属性信息")
    DG_FIELD_CATEGORY_CONFIG = deepcopy(BASE_DG_FIELD_CATEGORY_CONFIG)
    table_metadata = state["table_metadata_info"]
    if not table_metadata:
        logger.error("未查询到表元数据，无法进行字段字典RAG增强推荐")
        state["error_message"].append(
            ToolMessage("未查询到表元数据，无法进行字段字典RAG增强推荐")
        )
        return state
    table_dictkey_slice: list[str] = []
    table_dict_category_code_map: dict[str, str] = {}
    table_dictkey_map: dict[str, list[RecommendPanGuDictSchema]] = {}
    db_manager = DatabaseManager()
    for _, each_field in enumerate(table_metadata.raw_fields_info):
        if each_field.dict_key:
            # 数据域页面获取的表元数据没有dict_name，只有dict_key，
            # 且dict_key是没有nlevel的，需要补上, 默认2
            dict_key_with_nlevel = each_field.dict_key + ":2"
            table_dictkey_slice.append(dict_key_with_nlevel)
            dict_status, dict_message, dict_result = query_dict_items_info_by_dictkey(
                db_manager=db_manager, dictkey_with_nlevel=dict_key_with_nlevel
            )
            if dict_status is False:
                logger.error(f"获取盘古字典异常: {dict_message}")
        elif each_field.dict_name:
            # 盘古页面获取的表元数据没有dict_key，只有dict_name，
            # 对应RecommendPanGuDictSchema.dict_category
            dict_status, dict_message, dict_result = (
                query_dict_items_info_by_dict_category(
                    db_manager=db_manager, dict_category=each_field.dict_name
                )
            )
        else:
            # 都没有就跳过
            continue
        if dict_result:
            one_dict = dict_result[0]
            category = one_dict.dict_category
            if category not in table_dict_category_code_map:
                table_dict_category_code_map[category] = one_dict.dictkey_with_nlevel
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
            # 补充字典类别名称
            each_field.dict_name = category
            each_field.dict_key = one_dict.dictkey_with_nlevel
    state["table_metadata_info"] = table_metadata
    state["table_dict_category_code_map"] = table_dict_category_code_map
    state["table_dictkey_map"] = table_dictkey_map
    state["DG_FIELD_CATEGORY_CONFIG"] = DG_FIELD_CATEGORY_CONFIG
    # 动态更新配置
    init_dg_category_config.DG_FIELD_CATEGORY_CONFIG = DG_FIELD_CATEGORY_CONFIG
    # 如果已经生成过实例了，需要清空缓存更新
    PydanticDataGeniusCategoryRecommendation.reset_allowed_categories()
    db_manager.close()
    return state


def save_dg_plan2json(state: DataGenState):
    """
    存储DG执行计划任务配置
    Args:
        state:

    Returns:

    """
    logger.info("存储DataGenius任务规则")
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    table_metadata = state.get("table_metadata_info")
    if pydantic_data_genius_plan:
        data = pydantic_data_genius_plan.model_dump()
        save_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}.json"
        ).absolute()
        save_dict2jl(json_data=data, save_path=str(save_json_path))
    if table_metadata:
        table_metadata_data = table_metadata.model_dump()
        table_metadata_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}_table_metadata.json"
        )

        save_dict2jl(json_data=table_metadata_data, save_path=table_metadata_json_path)
    return state


def is_pre_heat_dg_rule_mode(state: DataGenState):
    """
    如果是预热字段推荐DG规则模式则不创建DG任务
    Args:
        state:

    Returns:

    """
    pre_heat_mode = state.get("pre_heat_mode", False)
    if pre_heat_mode is True:
        return END
    else:
        return "save_dg_plan2json"


data_gen_builder = StateGraph(DataGenState)
data_gen_builder.add_node("analyze_intent", analyze_data_intent)
data_gen_builder.add_node("intent_human_feedback_node", data_intent_human_feedback_node)
data_gen_builder.add_node("query_table_raw_field_info", query_table_raw_field_info)
data_gen_builder.add_node("rag_sql_table_filed_info", rag_sql_table_filed_info)
data_gen_builder.add_node("dg_category_recommend", dg_rule_processor)
data_gen_builder.add_node("save_dg_plan2json", save_dg_plan2json)
data_gen_builder.add_node("create_dg_task", create_dg_task)
data_gen_builder.add_node("query_dg_task_status", query_dg_task_status)
data_gen_builder.add_node("save_task_info2db", save_task_info2db)

data_gen_builder.add_conditional_edges(
    START, detect_input_type, ["query_table_raw_field_info", "analyze_intent"]
)
data_gen_builder.add_edge("analyze_intent", "intent_human_feedback_node")
data_gen_builder.add_conditional_edges(
    "intent_human_feedback_node",
    should_data_intent_continue,
    ["analyze_intent", "query_table_raw_field_info"],
)
data_gen_builder.add_conditional_edges(
    "query_table_raw_field_info",
    should_table_raw_field_info_continue,
    ["rag_sql_table_filed_info", END],
)
data_gen_builder.add_edge("rag_sql_table_filed_info", "dg_category_recommend")
data_gen_builder.add_conditional_edges(
    "dg_category_recommend", is_pre_heat_dg_rule_mode, ["save_dg_plan2json", END]
)
data_gen_builder.add_edge("save_dg_plan2json", "create_dg_task")
data_gen_builder.add_edge("create_dg_task", "query_dg_task_status")
data_gen_builder.add_edge("query_dg_task_status", "save_task_info2db")
data_gen_builder.add_edge("save_task_info2db", END)

memory = MemorySaver()
data_gen_graph = data_gen_builder.compile(
    interrupt_before=["intent_human_feedback_node"], checkpointer=memory
)

if __name__ == "__main__":
    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="DataForgeDataGenApp.log",
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))

    init_env()
    print(data_gen_graph.get_graph(xray=True).draw_mermaid())

    session_id = uuid.uuid4().hex

    traced_logger = TracedLogger()
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        traced_logger.set_trace_uuid(session_id)

    user_input = """数据库表名称：
fmdbmeta.DWD_BEH_TRANS_ENTRY
期望生成数据条数：
fmdbmeta.DWD_BEH_TRANS_ENTRY：100"""
    thread: RunnableConfig = {"configurable": {"thread_id": session_id}}

    init_state = {
        # "DG_FIELD_CATEGORY_CONFIG": DG_FIELD_CATEGORY_CONFIG,
        "user_input": user_input,
        "user_intent": DataGenUserIntentSchema(
            **{
                "table_en_names": ["fmdbmeta.DWD_BEH_TRANS_ENTRY"],
                "table_data_count": {"fmdbmeta.DWD_BEH_TRANS_ENTRY": 100},
            }
        ),
        "human_intent_feedback": "正确",
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    for event in data_gen_graph.stream(init_state, thread, stream_mode="values"):
        # Review
        # user_intent: DataGenUserIntentSchema = event.get("user_intent")
        # if user_intent:
        #     logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")

        # 模拟用户意图识别的研判反馈
        # data_gen_graph.update_state(thread,
        # {"human_intent_feedback": "正确"}, as_node="intent_human_feedback_node")

        # for event in data_gen_graph.stream(None, thread, stream_mode="values"):
        # Review
        # human_intent_feedback = event.get("human_intent_feedback")
        # if human_intent_feedback:
        #     logger.info(f"human_intent_feedback: {human_intent_feedback}")
        table_dict_category_code_map = event.get("table_dict_category_code_map")
        if table_dict_category_code_map:
            logger.info(f"table_dict_category_code_map: {table_dict_category_code_map}")

        create_data_genius_task_error = event.get("create_data_genius_task_error")
        if create_data_genius_task_error:
            logger.info("create_data_genius_task_error", create_data_genius_task_error)

        query_data_genius_task_error = event.get("query_data_genius_task_error")
        if query_data_genius_task_error:
            logger.info("query_data_genius_task_error", query_data_genius_task_error)

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
