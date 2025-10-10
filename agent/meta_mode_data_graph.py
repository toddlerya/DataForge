#!/usr/bin/env python
# coding: utf-8
# @File    :   data_graph.py
# @Time    :   2025/06/03 15:34:28
# @Author  :   toddlerya
# @Desc    :   None


import json
import uuid
from copy import deepcopy
from typing import cast

from langchain_core.messages import FunctionMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from loguru import logger

from agent.dg_configs import DG_FIELD_CATEGORY_CONFIG as BASE_DG_FIELD_CATEGORY_CONFIG
from agent.llm import chat_llm
from agent.prompt import data_intent_prompt
from agent.state import (
    DataGenUserIntentSchema,
    MetaModeDataGenState,
    PydanticDataGeniusCategoryRecommendation,
    TableMetadataSchema,
    init_dg_category_config,
)
from config import PROJECT_PATH
from cruds.pangu import (
    query_dict_items_info_by_dict_category,
    query_dict_items_info_by_dictkey,
)
from cruds.table_metadata import table_metadata_fuzzy_query, table_metadata_query
from database_models.schema import RecommendPanGuDictSchema, TableRawFieldSchema
from utils.db_manager import DatabaseManager


def detect_input_type(state: MetaModeDataGenState):
    """
    判断用户输入的是结构化任务参数还是自然语言任务需求
    :param state:
    :return:
    """

    user_intent = state.get("user_intent")

    if user_intent:
        return "query_table_raw_field_info"
    else:
        return "analyze_meta_intent"


def analyze_meta_intent(state: MetaModeDataGenState) -> MetaModeDataGenState:
    user_input = state.get("user_input", "").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_meta_intent => user_input: {user_input} "
        f"human_intent_feedback: {human_intent_feedback}"
    )
    if user_input:
        structured_llm = chat_llm.with_structured_output(DataGenUserIntentSchema)
        chat_prompt = data_intent_prompt.format_messages(
            user_input=user_input, human_intent_feedback=human_intent_feedback
        )
        logger.trace(f"analyze_meta_intent chat_prompt: {chat_prompt}")
        user_intent = structured_llm.invoke(chat_prompt)
        logger.info(f"user_input: {user_input} user_intent: {user_intent}")
        if isinstance(user_intent, DataGenUserIntentSchema):
            state["user_intent"] = user_intent
            state["env_name"] = user_intent.env_name
            state["dont_run_dg_task"] = user_intent.dont_run_dg_task
    return state


def meta_intent_human_feedback_node(state: MetaModeDataGenState):
    feedback: dict = interrupt("意图正确吗?")
    logger.info(f"resume feedback: {feedback}")
    human_intent_feedback = feedback.get("human_intent_feedback", "").strip().upper()
    state["human_intent_feedback"] = human_intent_feedback
    return state


def should_intent_continue(state: MetaModeDataGenState):
    """Return the next node to execute"""

    # Check if human feedback

    logger.info(f"should_intent_continue: {state}")
    human_intent_feedback = state.get("human_intent_feedback", "").strip().upper()
    if human_intent_feedback in ("正确", "Y", "OK"):
        logger.info(
            "should_intent_continue -> query_table_raw_field_info "
            f"human_intent_feedback: {human_intent_feedback}"
        )
        return "query_table_raw_field_info"
    else:
        logger.info("should_intent_continue -> END")
        # 重新开始意图识别
        logger.info("用户反馈意图错误, END")
        return END


def should_table_raw_field_info_continue(state: MetaModeDataGenState):
    logger.info("should_table_raw_field_info_continue start")
    table_metadata_error = state.get("table_metadata_error", [])
    if len(table_metadata_error) >= 1:
        logger.error(f"存在table_metadata_error: {' '.join(table_metadata_error)}")
        logger.info("查询元数据错误, END")
        return END
    else:
        return "rag_table_field_info"


def query_table_raw_field_info(state: MetaModeDataGenState) -> MetaModeDataGenState:  # noqa: C901
    logger.info("query_table_raw_field_info start")
    state["mode"] = 1
    if "table_metadata_info" not in state:
        state["table_metadata_error"] = []
    if user_intent := state.get("user_intent"):
        if not isinstance(user_intent, DataGenUserIntentSchema):
            state["table_metadata_error"].append(
                f"用户意图不是元数据构造意图: {user_intent.model_dump()}"
            )
            return state
    else:
        user_intent = cast(DataGenUserIntentSchema, user_intent)
    logger.info(f"user_intent: {user_intent}")
    env_name = user_intent.env_name
    state["env_name"] = env_name
    table_en_name = user_intent.table_en_name
    # 查询知识库获取表的字段配置信息
    table_metadata = TableMetadataSchema(table_en_name=table_en_name)
    db_manager = DatabaseManager()
    query_status, query_message, query_result = table_metadata_query(
        table_en_name=table_en_name, env_name=env_name, db_manager=db_manager
    )
    if "table_metadata_error" not in state:
        state["table_metadata_error"] = []
    if query_status is False:
        logger.error(f"查询{table_en_name}元数据异常: {query_message}")
        state["table_metadata_error"].append(
            f"查询{table_en_name}元数据异常: {query_message}"
        )
        raw_fields_data = [TableRawFieldSchema()]
    elif query_result is None:
        logger.warning(f"未查询到{table_en_name}元数据!")
        state["table_metadata_error"].append(f"未查询到{table_en_name}元数据!")
        logger.info(
            f"尝试模糊查询, 提供更好的错误信息, input table_en_name: {table_en_name}"
        )
        # 预处理table_en_name，去除数据库作用域
        if "." in table_en_name:
            table_en_name = table_en_name.split(".")[1]
        fuzzy_status, fuzzy_message, fuzzy_result = table_metadata_fuzzy_query(
            table_name=table_en_name, env_name=env_name, db_manager=db_manager
        )
        if fuzzy_status is False:
            logger.error(f"模糊查询表元数据异常: {fuzzy_message}")
        else:
            fuzzy_table_en_name_list = [
                str(ele.table_en_name) for ele in fuzzy_result if fuzzy_result
            ]
            if fuzzy_table_en_name_list:
                state["table_metadata_error"].append(
                    f"您想要查询的表可能是:\n {'\n'.join(fuzzy_table_en_name_list)}"
                )
            else:
                logger.warning(
                    f"input table_en_name: {table_en_name}"
                    f"模糊查询结果为空: fuzzy_result={fuzzy_result}"
                )
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
    table_metadata.source = str(query_result.source) if query_result else ""

    state["table_metadata_info"] = table_metadata
    db_manager.close()
    return state


def rag_table_field_info(state: MetaModeDataGenState) -> MetaModeDataGenState:
    """
    根据字段知识库增强字段信息
    :param state:
    :return:
    """
    global dict_result
    logger.info("RAG增强字段属性信息")
    DG_FIELD_CATEGORY_CONFIG = deepcopy(BASE_DG_FIELD_CATEGORY_CONFIG)
    table_metadata = state.get("table_metadata_info")
    if not table_metadata:
        table_metadata_error = "未查询到表元数据, 无法进行字段字典RAG增强推荐"
        logger.error(table_metadata_error)
        state["error_messages"].append(
            FunctionMessage(content=table_metadata_error, name="rag_table_field_info")
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
    state["rag_done"] = True
    logger.info(f"完成RAG增强: {state.get('rag_done')}")
    # 动态更新配置
    init_dg_category_config.DG_FIELD_CATEGORY_CONFIG = DG_FIELD_CATEGORY_CONFIG
    # 如果已经生成过实例了，需要清空缓存更新
    PydanticDataGeniusCategoryRecommendation.reset_allowed_categories()
    db_manager.close()
    return state


meta_mode_data_gen_builder = StateGraph(MetaModeDataGenState)
meta_mode_data_gen_builder.add_node("analyze_meta_intent", analyze_meta_intent)
meta_mode_data_gen_builder.add_node(
    "meta_intent_human_feedback_node", meta_intent_human_feedback_node
)
meta_mode_data_gen_builder.add_node(
    "query_table_raw_field_info", query_table_raw_field_info
)
meta_mode_data_gen_builder.add_node("rag_table_field_info", rag_table_field_info)


meta_mode_data_gen_builder.add_conditional_edges(
    START, detect_input_type, ["query_table_raw_field_info", "analyze_meta_intent"]
)
meta_mode_data_gen_builder.add_edge(
    "analyze_meta_intent", "meta_intent_human_feedback_node"
)
meta_mode_data_gen_builder.add_conditional_edges(
    "meta_intent_human_feedback_node",
    should_intent_continue,
    ["query_table_raw_field_info", END],
)
meta_mode_data_gen_builder.add_conditional_edges(
    "query_table_raw_field_info",
    should_table_raw_field_info_continue,
    ["rag_table_field_info", END],
)
meta_mode_data_gen_builder.add_edge("rag_table_field_info", END)


memory = InMemorySaver()
meta_mode_data_gen_graph = meta_mode_data_gen_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import pathlib

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    current_file_path = pathlib.Path(__file__)
    current_log_name = (
        f"{current_file_path.name.replace(current_file_path.suffix, '')}.log"
    )

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name=current_log_name,
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))

    init_env()
    print(meta_mode_data_gen_graph.get_graph(xray=True).draw_mermaid())
    logger.info("\n" + meta_mode_data_gen_graph.get_graph(xray=True).draw_mermaid())

    session_id = uuid.uuid4().hex

    traced_logger = TracedLogger()
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        traced_logger.set_trace_uuid(session_id)

    user_input = """数据库表名称: fmdbmeta.DWD_BEH_TRANS_ENTRY 期望生成数据条数： 100"""
    run_config = RunnableConfig(configurable={"thread_id": session_id})

    init_state = {
        "user_input": user_input,
        # "user_intent": DataGenUserIntentSchema(
        #     **{
        #         "table_en_name": "fmdbmeta.DWD_BEH_TRANS_ENTRY",
        #         "data_count": 100,
        #     }
        # ),
        # "human_intent_feedback": "正确",
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
        # "dont_run_dg_task": True,
    }

    # 1. 先流式执行到中断点
    for event in meta_mode_data_gen_graph.stream(
        init_state, run_config, stream_mode="values"
    ):
        # Review
        # user_intent: DataGenUserIntentSchema = event.get("user_intent")
        # if user_intent:
        #     logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")

        # for event in data_gen_graph.stream(None, thread, stream_mode="values"):
        # Review
        # human_intent_feedback = event.get("human_intent_feedback")
        # if human_intent_feedback:
        #     logger.info(f"human_intent_feedback: {human_intent_feedback}")
        logger.info(f"event: {event}")

    # 2. 模拟用户意图识别的研判反馈
    meta_mode_data_gen_graph.update_state(
        run_config,
        {"human_intent_feedback": "正确"},
        as_node="intent_human_feedback_node",
    )

    # 3. 从中断点继续执行
    for event in meta_mode_data_gen_graph.stream(
        None, run_config, stream_mode="values"
    ):
        table_dict_category_code_map = event.get("table_dict_category_code_map")
        if table_dict_category_code_map:
            logger.info(f"table_dict_category_code_map: {table_dict_category_code_map}")
