#!/usr/bin/env python
# coding: utf-8
# @File    :   data_graph.py
# @Time    :   2025/06/03 15:34:28
# @Author  :   toddlerya
# @Desc    :   None


import json
import pathlib
import time
import uuid

import httpx
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.llm import chat_llm
from agent.prompt import dg_category_prompt, data_intent_prompt
from agent.state import (
    DataGenState,
    PydanticDataGeniusCategoryRecommendation,
    PydanticDataGeniusPlan,
    PydanticDataGeniusRule,
    TableMetadataSchema,
    DataGenUserIntentSchema,
)
from config import DG_PLAN_CONFIG_PREFIX
from cruds.table_metadata import table_metadata_query
from database_models.schema import TableRawFieldSchema
from faker_utils.dg_configs import (
    DG_FIELD_CATEGORY_CONFIG,
    DG_STORAGE_PATH,
    DG_SERVER_BASE_URL,
    DG_TASK_ADD_URL,
    DG_TASK_HISTORY,
    DG_NEW_TASK,
)
from utils.db import Database
from utils.file import save_dict2jl


def analyze_data_intent(state: DataGenState) -> DataGenState:
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {user_input} human_intent_feedback: {human_intent_feedback}"
    )
    structured_llm = chat_llm.with_structured_output(DataGenUserIntentSchema)
    chat_prompt = data_intent_prompt.format_messages(
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


def should_data_intent_continue(state: DataGenState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确":
        return "query_table_raw_field_info"

    # Otherwise proceed to create table info
    return "analyze_intent"


def should_table_raw_field_info_continue(state: DataGenState):
    table_metadata_error = state.get("table_metadata_error", [])
    if len(table_metadata_error) >= 1:
        logger.error(f"存在table_metadata_error: {' '.join(table_metadata_error)}")
        return END
    else:
        return "dg_category_recommend"


def query_table_raw_field_info(state: DataGenState) -> DataGenState:
    if "table_metadata_array" not in state:
        state["table_metadata_array"] = []
        state["table_metadata_error"] = []

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


def dg_category_recommend(state: DataGenState) -> DataGenState:
    """
    DataGenius字段分类推荐节点
    Args:
        state:

    Returns:

    """
    logger.info("DataGenius字段分类推荐")
    table_metadata_array = state["table_metadata_array"]
    user_intent = state["user_intent"]
    table_en_name = user_intent.table_en_names[0]
    row_count = user_intent.table_data_count.get(table_en_name, 1000)
    table_metadata = table_metadata_array[0] if table_metadata_array else None
    if not table_metadata:
        logger.error("未查询到表元数据，无法进行数据字段分类推荐")
        state["error_message"].append("未查询到表元数据，无法进行数据字段分类推荐")
        return state
    logger.trace(f"table_metadata: {table_metadata.model_dump_json()}")
    structured_llm = chat_llm.with_structured_output(
        PydanticDataGeniusCategoryRecommendation
    )

    # 如果类别推荐错误，记录错误信息，补充到提示词不要再次生成错误的类别推荐，重试N次
    last_error_message = ""
    field_index = 0
    retry_count = 0
    # 设置最大重试次数
    max_retries = state["max_retries"]
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
            logger.trace(
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
                f"llm_dg_field_category_recommendation.model_dump_json(): "
                f"{llm_dg_field_category_recommendation.model_dump_json()}"
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
                preview=f"score: {llm_dg_field_category_recommendation.score}, "
                f"reason: {llm_dg_field_category_recommendation.reason}",
                value=field_info.example,
            )
            logger.trace(
                f"pydantic_data_genius_rule: {pydantic_data_genius_rule.model_dump_json()}"
            )
            rules.append(pydantic_data_genius_rule)
            field_index += 1
            # 清空字段重试次数，开始下一个字段的推荐
            retry_count = 0
    rule_uuid = str(uuid.uuid4())
    pydantic_data_genius_plan = PydanticDataGeniusPlan(
        rule_name=f"{DG_PLAN_CONFIG_PREFIX}{rule_uuid}.json",
        type_="规则",
        rows=row_count,
        separator="\t",
        rules=rules,
        output=f"{DG_STORAGE_PATH}/output/10.0.23.57/{rule_uuid}",
        model=f"{DG_STORAGE_PATH}/models/10.0.23.57/{table_en_name}",
        cols=len(table_metadata.raw_fields_info),
    )
    state["pydantic_data_genius_plan"] = pydantic_data_genius_plan
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
    if pydantic_data_genius_plan:
        data = pydantic_data_genius_plan.model_dump()
        save_json_path = (
            pathlib.Path(r"F:\GITLAB\DataForge\data\dg_plans")
            .joinpath(f"{pydantic_data_genius_plan.rule_name}")
            .absolute()
        )
        save_dict2jl(json_data=data, save_path=str(save_json_path))
    return state


def create_dg_task(state: DataGenState) -> DataGenState:
    """
    创建人DataGenius任务
    Args:
        state:

    Returns:

    """
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    user_intent = state["user_intent"]
    table_en_name = user_intent.table_en_names[0]
    logger.info(f"创建DataGenius任务, 任务名称: {pydantic_data_genius_plan.rule_name}")
    pydantic_data_genius_plan_dict = pydantic_data_genius_plan.model_dump()
    payload = {
        "task": json.dumps(
            {
                "step": "2",
                "name": pydantic_data_genius_plan.rule_name,
                "type_": pydantic_data_genius_plan.type_,
                "modelName": table_en_name,
                "mode": "create",
                "task_id": "None",
                "duration": None,
                "output_filesize": None,
            }
        ),
        "rules": json.dumps(pydantic_data_genius_plan_dict["rules"]),
        "separator": pydantic_data_genius_plan.separator,
        "rows": pydantic_data_genius_plan.rows,
        "cols": pydantic_data_genius_plan.cols,
        "send": json.dumps(
            {
                "send_type": 1,
                "id": None,
                "tip": "无配置，点击刷新或添加。",
                "connect_test": False,
                "connect_test_tip": "",
                "table_name": "",
                "table_test": False,
                "table_test_tip": "",
                "table_columns": [],
                "schemas": "public",
            }
        ),
        "saveRuleFile": False,
        "blockSize": 100000,
        "source": "",
        "alam": json.dumps({"isRule": "1", "rule": "", "name": ""}),
    }

    save_json_path = (
        pathlib.Path(r"F:\GITLAB\DataForge\data\dg_payload")
        .joinpath(f"payload_{pydantic_data_genius_plan.rule_name}")
        .absolute()
    )
    save_dict2jl(json_data=payload, save_path=str(save_json_path))
    create_task_url = f"{DG_SERVER_BASE_URL}/{DG_TASK_ADD_URL}"

    with httpx.Client() as client:
        response = client.post(create_task_url, data=payload)
    if response.status_code != 200:
        logger.error(f"请求{create_task_url}异常, status_code: {response.status_code}")
        state["create_data_genius_task_error"] = (
            f"请求{create_task_url}异常, status_code: {response.status_code}"
        )
        logger.debug(
            f"state.create_data_genius_task_error: {state['create_data_genius_task_error']}"
        )
    return state


def query_dg_task_status(state: DataGenState) -> DataGenState:
    """
    查询当前任务状态
    Args:
        state:

    Returns:

    """
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    logger.info(f"查询DataGenius进度, 任务名称: {pydantic_data_genius_plan.rule_name}")
    query_task_url = f"{DG_SERVER_BASE_URL}/{DG_TASK_HISTORY}"
    payload = {"limit": 10}
    with httpx.Client() as client:
        for _ in range(60):
            response = client.get(query_task_url, params=payload)
            if response.status_code != 200:
                logger.error(
                    f"请求{query_task_url}异常, status_code: {response.status_code}"
                )
                state["query_data_genius_task_error"] = (
                    f"请求{query_task_url}异常, status_code: {response.status_code}"
                )
                return state
            resp_json = response.json()
            for result in resp_json.get("results", [{}]):
                if result.get("name", "") == pydantic_data_genius_plan.rule_name:
                    if result.get("status_name") == "成功":
                        logger.trace(f"matched result: {result}")
                        task_id = result.get("task_id", "not_found_task_id")
                        duration = result.get("duration_", "not_found_duration")
                        output_url = f"{DG_SERVER_BASE_URL}/{result.get('output', 'not_found_output_url')}"
                        output_filesize = result.get(
                            "output_filesize", "not_found_output_filesize"
                        )
                        data_genius_plan_edit_url = (
                            f"{DG_SERVER_BASE_URL}/{DG_NEW_TASK}?"
                            f"step=2&"
                            f"name={pydantic_data_genius_plan.rule_name}&"
                            f"type_={pydantic_data_genius_plan.type_}&"
                            f"modelName={pydantic_data_genius_plan.model}&"
                            f"mode=edit&"
                            f"task_id={task_id}"
                        )
                        logger.debug(
                            f"duration: {duration}\n output_url: {output_url}\n "
                            f"output_filesize: {output_filesize}\n"
                            f"data_genius_plan_edit_url: {data_genius_plan_edit_url}"
                        )
                        state["data_genius_plan_task_id"] = task_id
                        state["data_genius_plan_run_duration"] = duration
                        state["data_genius_plan_output_url"] = output_url
                        state["data_genius_plan_output_filesize"] = output_filesize
                        state["data_genius_plan_edit_url"] = data_genius_plan_edit_url
                        return state
            time.sleep(2)
    return state


data_gen_builder = StateGraph(DataGenState)
data_gen_builder.add_node("analyze_intent", analyze_data_intent)
data_gen_builder.add_node("intent_human_feedback_node", data_intent_human_feedback_node)
data_gen_builder.add_node("query_table_raw_field_info", query_table_raw_field_info)
data_gen_builder.add_node("dg_category_recommend", dg_category_recommend)
data_gen_builder.add_node("save_dg_plan2json", save_dg_plan2json)
data_gen_builder.add_node("create_dg_task", create_dg_task)
data_gen_builder.add_node("query_dg_task_status", query_dg_task_status)

data_gen_builder.add_edge(START, "analyze_intent")
data_gen_builder.add_edge("analyze_intent", "intent_human_feedback_node")
data_gen_builder.add_conditional_edges(
    "intent_human_feedback_node",
    should_data_intent_continue,
    ["analyze_intent", "query_table_raw_field_info"],
)
data_gen_builder.add_conditional_edges(
    "query_table_raw_field_info",
    should_table_raw_field_info_continue,
    ["dg_category_recommend", END],
)
# data_forge_builder.add_edge("query_table_raw_field_info", "dg_category_recommend")
data_gen_builder.add_edge("dg_category_recommend", "save_dg_plan2json")
data_gen_builder.add_edge("save_dg_plan2json", "create_dg_task")
data_gen_builder.add_edge("create_dg_task", "query_dg_task_status")
data_gen_builder.add_edge("query_dg_task_status", END)

memory = MemorySaver()
data_gen_graph = data_gen_builder.compile(
    interrupt_before=["intent_human_feedback_node"], checkpointer=memory
)

if __name__ == "__main__":
    print(data_gen_graph.get_graph(xray=True).draw_mermaid())
#     user_input = """数据库表名称:
# massdata.ADM_REL_MOBILE
# 期望生成数据条数:
# massdata.ADM_REL_MOBILE: 5"""
#     thread = {"configurable": {"thread_id": "123"}}
#
#     init_state = {
#         "user_input": user_input,
#         "max_retries": 5,
#     }
#
#     for event in data_gen_graph.stream(init_state, thread, stream_mode="values"):
#         # Review
#         user_intent: DataGenUserIntentSchema = event.get("user_intent")
#         if user_intent:
#             logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")
#
#     # 模拟用户意图识别的研判反馈
#     data_forge_graph.update_state(thread, {"human_intent_feedback": "正确"}, as_node="intent_human_feedback_node")
#
#     for event in data_gen_graph.stream(None, thread, stream_mode="values"):
#         # Review
#         human_intent_feedback = event.get("human_intent_feedback")
#         if human_intent_feedback:
#             logger.info(f"human_intent_feedback: {human_intent_feedback}")
#
#         if event.get("create_data_genius_task_error"):
#             logger.info("create_data_genius_task_error", event["create_data_genius_task_error"])
#
#         if event.get("query_data_genius_task_error"):
#             logger.info("query_data_genius_task_error", event["query_data_genius_task_error"])
#
#         if event.get("data_genius_plan_run_duration"):
#             logger.info("data_genius_plan_run_duration", event["data_genius_plan_run_duration"])
#
#         if event.get("data_genius_plan_output_url"):
#             logger.info("data_genius_plan_output_url", event["data_genius_plan_output_url"])
#
#         if event.get("data_genius_plan_output_filesize"):
#             logger.info("data_genius_plan_output_filesize", event["data_genius_plan_output_filesize"])
