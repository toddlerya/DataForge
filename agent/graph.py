#!/usr/bin/env python
# coding: utf-8
# @File    :   graph.py
# @Time    :   2025/06/03 15:34:28
# @Author  :   toddlerya
# @Desc    :   None


import json
import pathlib
import uuid

from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt, Command
from loguru import logger

from agent.llm import chat_llm, ollama_llm
from agent.prompt import dg_category_prompt, intent_prompt
from agent.state import (
    DataForgeState,
    PydanticDataGeniusCategoryRecommendation,
    PydanticDataGeniusPlan,
    PydanticDataGeniusRule,
    TableMetadataSchema,
    UserIntentSchema,
)
from agent.utils import build_main_model, create_table_model
from cruds.table_metadata import table_metadata_query
from database_models.schema import TableRawFieldSchema
from faker_utils.dg_configs import DG_FIELD_CATEGORY_CONFIG, DG_STORAGE_PATH
from utils.db import Database
from utils.file import save_dict2jl


def analyze_intent(state: DataForgeState) -> DataForgeState:
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(f"user_input: {user_input} human_intent_feedback: {human_intent_feedback}")
    structured_llm = chat_llm.with_structured_output(UserIntentSchema)
    chat_prompt = intent_prompt.format_messages(
        user_input=user_input, human_intent_feedback=human_intent_feedback
    )
    logger.debug(f"analyze_intent chat_prompt: {chat_prompt}")
    user_intent = structured_llm.invoke(chat_prompt)
    state["user_intent"] = user_intent
    logger.debug(f"user_intent: {user_intent}")
    return state


def intent_human_feedback(state: DataForgeState):
    """No-op node that should be interrupted on"""
    pass


def should_intent_continue(state: DataForgeState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确":
        return "create_table_raw_field_info"

    # Otherwise proceed to create table info
    return "analyze_intent"


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


def dg_category_recommend(state: DataForgeState) -> DataForgeState:
    """
    DataGenius字段分类推荐节点
    Args:
        state:

    Returns:

    """
    logger.info("DataGenius字段分类推荐节点")
    table_metadata_array = state["table_metadata_array"]
    user_intent = state["user_intent"]
    table_en_name = user_intent.table_en_names[0]
    row_count = user_intent.table_data_count.get(table_en_name, 1000)
    table_metadata = table_metadata_array[0] if table_metadata_array else None
    if not table_metadata:
        logger.error("未查询到表元数据，无法进行数据字段分类推荐")
        state["error_message"] = "未查询到表元数据，无法进行数据字段分类推荐"
        return state
    logger.debug(f"table_metadata: {table_metadata.model_dump_json()}")
    structured_llm = chat_llm.with_structured_output(
        PydanticDataGeniusCategoryRecommendation
    )

    # 如果类别推荐错误，记录错误信息，补充到提示词不要再次生成错误的类别推荐，重试N次
    last_error_message = ""
    field_index = 0
    retry_count = 0
    # 设置最大重试次数
    max_retries = 3
    stop_flag = False
    rules: list[PydanticDataGeniusRule] = []
    while True:
        if field_index >= len(table_metadata.raw_fields_info):
            stop_flag = True
        if stop_flag:
            logger.info("所有字段已处理完毕，结束DataGenius分类推荐")
            break
        field_info = table_metadata.raw_fields_info[field_index]
        if retry_count >= max_retries:
            llm_dg_field_category_recommendation = (
                PydanticDataGeniusCategoryRecommendation(
                    category="数字串",
                    score=0,
                    reason="未能识别字段类型, 填充数字串分类",
                )
            )
            logger.warning(
                f"已达到最大推荐重试次数 {max_retries}，自动填充默认DataGenius分类推荐"
            )
            logger.debug(
                f"llm_dg_field_category_recommendation: {llm_dg_field_category_recommendation.model_dump_json()}"
            )
            # 构建该字段的DataGenius规则参数
            pydantic_data_genius_rule = PydanticDataGeniusRule(
                col=field_index + 1,
                category=llm_dg_field_category_recommendation.category,
                name="",
                ename=field_info.en_name,
                cname=field_info.cn_name,
                preview=f"{llm_dg_field_category_recommendation.model_dump_json()}",
                value=field_info.example,
            )
            rules.append(pydantic_data_genius_rule)
            field_index += 1
            # 清空字段重试次数，开始下一个字段的推荐
            retry_count = 0
            continue
        chat_prompt = dg_category_prompt.format_messages(
            cn_name=field_info.cn_name,
            en_name=field_info.en_name,
            field_type=field_info.field_type,
            desc=field_info.desc,
            sample_value=field_info.example,
            dict_name=field_info.dict_name,
            dg_category_config_data=DG_FIELD_CATEGORY_CONFIG,
            last_error_message=last_error_message,
        )
        logger.trace(f"llm_dg_field_category_recommendation chat_prompt: {chat_prompt}")
        try:
            llm_dg_field_category_recommendation = structured_llm.invoke(chat_prompt)
            logger.trace(
                f"llm_dg_field_category_recommendation.model_dump_json(): {llm_dg_field_category_recommendation.model_dump_json()}"
            )
        except Exception as e:
            logger.error(f"llm_dg_field_category_recommendation error: {e}")
            last_error_message = str(e)
            retry_count += 1
        else:
            last_error_message = ""
            # 构建该字段的DataGenius规则参数
            pydantic_data_genius_rule = PydanticDataGeniusRule(
                col=field_index + 1,
                category=llm_dg_field_category_recommendation.category,
                name="",
                ename=field_info.en_name,
                cname=field_info.cn_name,
                preview=f"{llm_dg_field_category_recommendation.model_dump_json()}",
                value=field_info.example,
            )
            logger.debug(
                f"pydantic_data_genius_rule: {pydantic_data_genius_rule.model_dump_json()}"
            )
            rules.append(pydantic_data_genius_rule)
            field_index += 1
            # 清空字段重试次数，开始下一个字段的推荐
            retry_count = 0
    rule_uuid = str(uuid.uuid4())
    pydantic_data_genius_plan = PydanticDataGeniusPlan(
        rule_name=f"{rule_uuid}.json",
        type_="模型",
        rows=row_count,
        separator="\t",
        rules=rules,
        output=f"{DG_STORAGE_PATH}/output/10.0.23.57/{rule_uuid}",
        model=f"{DG_STORAGE_PATH}/models/10.0.23.57/{table_en_name}",
        cols=len(table_metadata.raw_fields_info),
    )
    logger.info(
        f"PydanticDataGeniusPlan: {pydantic_data_genius_plan.model_dump_json()}"
    )
    state["pydantic_data_genius_plan"] = pydantic_data_genius_plan
    return state


def save_dg_plan2json(state: DataForgeState):
    """
    存储DG执行计划任务配置
    Args:
        state:

    Returns:

    """
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    if pydantic_data_genius_plan:
        data = pydantic_data_genius_plan.model_dump()
        save_json_path = pathlib.Path(r"F:\GITLAB\DataForge\data\dg_plans").joinpath(
            f"dg_task_plan_{pydantic_data_genius_plan.rule_name}"
        ).absolute()
        save_dict2jl(json_data=data, save_path=str(save_json_path))


data_forge_builder = StateGraph(DataForgeState)
data_forge_builder.add_node("analyze_intent", analyze_intent)
data_forge_builder.add_node("intent_human_feedback", intent_human_feedback)
data_forge_builder.add_node("create_table_raw_field_info", create_table_raw_field_info)
data_forge_builder.add_node("dg_category_recommend", dg_category_recommend)
data_forge_builder.add_node("save_dg_plan2json", save_dg_plan2json)

data_forge_builder.add_edge(START, "analyze_intent")
data_forge_builder.add_edge("analyze_intent", "intent_human_feedback")
data_forge_builder.add_conditional_edges(
    "intent_human_feedback", should_intent_continue, ["analyze_intent", "create_table_raw_field_info"]
)
data_forge_builder.add_edge("create_table_raw_field_info", "dg_category_recommend")
data_forge_builder.add_edge("dg_category_recommend", "save_dg_plan2json")
data_forge_builder.add_edge("save_dg_plan2json", END)

memory = MemorySaver()
data_forge_graph = data_forge_builder.compile(interrupt_before=["intent_human_feedback"], checkpointer=memory)

if __name__ == "__main__":
    print(data_forge_graph.get_graph(xray=True).draw_mermaid())
    user_input = """数据库表名称:
    fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE
    期望生成数据条数:
    fmdbmeta.NB_APP_EVIDENCE_EMAILRELATE: 5"""
    thread = {"configurable": {"thread_id": "123"}}

    for event in data_forge_graph.stream({"user_input": user_input}, thread, stream_mode="values"):
        # Review
        user_intent: UserIntentSchema = event.get("user_intent")
        if user_intent:
            logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")

    __state = data_forge_graph.get_state(thread)
    logger.info(f"下一个节点: {__state.next}")

    # 模拟用户意图识别的研判反馈
    data_forge_graph.update_state(thread, {"human_intent_feedback": "正确"}, as_node="intent_human_feedback")
    __state = data_forge_graph.get_state(thread)
    logger.info(f"用户意图识别反馈后，下一个节点: {__state.next}")

    for event in data_forge_graph.stream(None, thread, stream_mode="values"):
        # Review
        intent_human_feedback = event.get("intent_human_feedback")
        if intent_human_feedback:
            logger.info(f"intent_human_feedback: {intent_human_feedback}")
