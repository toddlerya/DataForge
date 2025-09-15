#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 11:04
# @Author   : guoqun X2590
# @FileName : agent_data_gen.py
# @Project  : DataForge

import json

from fastapi import APIRouter, Depends, Request
from langchain_core.runnables.config import RunnableConfig

from agent.data_graph import data_gen_graph
from agent.state import DataGenUserIntentSchema
from server.api.depends import get_transaction_logger
from server.api.schemas.agent_data_gen import (
    HumanIntentFeedBackSchema,
    InitDataGenSchema,
)
from server.api.schemas.base_schema import ResponseBaseSchema
from server.api.utils import extract_client_ip
from utils.err_code import error_code
from utils.log import logger

router = APIRouter(
    prefix="/data_gen_agent",
    tags=["数据生成"],
    responses={404: {"description": "Not Found"}},
)


@router.post("/set_intent", response_model=ResponseBaseSchema)
async def init_data_gen_graph(
    init_data_gen: InitDataGenSchema,
    request: Request,
    traced_logger=Depends(get_transaction_logger),
):
    """
    设置用户意图，初始化图
    :param init_data_gen:
    :param request
    :param traced_logger
    :return:
    """
    # session_id = uuid.uuid4().hex
    session_id = traced_logger.get_trace_uuid()
    client_ip = extract_client_ip(request)
    logger.info(
        f"[数据生成Graph] 初始化, client_ip={client_ip}, 分析用户意图: "
        f"init_data_gen={init_data_gen.model_dump_json()}"
    )
    resp_data = ResponseBaseSchema(description="[数据生成Graph] 初始化，分析用户意图")
    resp_data.session_id = session_id
    init_state = {
        "user_input": init_data_gen.user_input,
        "max_retries": init_data_gen.max_retries,
        "session_id": session_id,
        "client_ip": client_ip,
    }

    thread: RunnableConfig = {"configurable": {"thread_id": session_id}}
    event = await data_gen_graph.ainvoke(init_state, thread, stream_mode="values")
    user_intent: DataGenUserIntentSchema | None = event.get("user_intent")

    if user_intent:
        resp_data.data = user_intent.model_dump()
        logger.info(
            f"[数据生成Graph] 用户意图分析完成，"
            f"session_id={session_id} "
            f"user_intent={user_intent.model_dump_json()}"
        )
    return resp_data.model_dump()


@router.post("/human_intent_feedback", response_model=ResponseBaseSchema)
async def set_human_intent_feedback(
    feedback_data: HumanIntentFeedBackSchema,
    traced_logger=Depends(get_transaction_logger),
):
    """
    用户反馈确认
    :param feedback_data:
    :param traced_logger:
    :return:
    """
    traced_logger.set_trace_uuid(trace_uuid=feedback_data.session_id)
    logger.info(f"[数据生成Graph] 用户反馈: {feedback_data.model_dump_json()}")
    resp_data = ResponseBaseSchema(
        description="[数据生成Graph] 确认用户反馈并开始生成数据"
    )
    resp_data.session_id = feedback_data.session_id
    thread: RunnableConfig = {"configurable": {"thread_id": feedback_data.session_id}}
    state_snapshot = data_gen_graph.get_state(thread)
    if not state_snapshot.next:
        logger.debug(f"[数据生成Graph] state_snapshot: {state_snapshot}")
        message = (
            f"[数据生成Graph] 用户提供的session_id={feedback_data.session_id}错误，"
            "没有初始化的Graph应用."
        )
        logger.error(message)
        resp_data.message = message
        resp_data.code = error_code.ARGS_VALUE_ERROR.get("code", "")
        return resp_data.dict()
    if feedback_data.human_intent_feedback.strip() != "正确":
        message = (
            f"用户反馈: {feedback_data.human_intent_feedback} "
            f"{error_code.FEEDBACK_STOP_GRAPH.get('description')}, "
            "若用户反馈human_intent_feedback=正确, Graph将继续运行。"
        )
        logger.warning(f"[数据生成Graph] {message}")
        resp_data.message = message
        resp_data.code = error_code.FEEDBACK_STOP_GRAPH.get("code")
        return resp_data.model_dump()

    data_gen_graph.update_state(
        thread,
        {"human_intent_feedback": feedback_data.human_intent_feedback.strip()},
        as_node="intent_human_feedback_node",
    )
    event = await data_gen_graph.ainvoke(None, thread, stream_mode="values")
    for error in [
        "table_metadata_error",
        "create_data_genius_task_error",
        "query_data_genius_task_error",
    ]:
        if event.get(error):
            logger.error(f"[数据生成Graph] {error}: {event.get(error)}")
            resp_data.data = event
            resp_data.message = (
                f"{error_code.GRAPH_NODE_ERROR.get('description')} {event.get(error)}"
            )
            resp_data.code = error_code.GRAPH_NODE_ERROR.get("code")
            return resp_data.model_dump()
    if event.get("data_genius_plan_output_url"):
        if table_metadata_info := event.get("table_metadata_info"):
            table_metadata_info_data = table_metadata_info.model_dump()
        else:
            table_metadata_info_data = {}
        result = {
            "table_metadata_info": table_metadata_info_data,
            "data_genius_plan_task_id": event["data_genius_plan_task_id"],
            "data_genius_plan_run_duration": event["data_genius_plan_run_duration"],
            "data_genius_plan_output_url": event["data_genius_plan_output_url"],
            "data_genius_plan_output_filesize": event[
                "data_genius_plan_output_filesize"
            ],
            "data_genius_plan_edit_url": event["data_genius_plan_edit_url"],
        }
        logger.info(f"[数据生成Graph] 结果: {json.dumps(result)}")
        resp_data.data = event
    return resp_data.model_dump()


@router.post("/run", response_model=ResponseBaseSchema)
async def run_graph(
    user_intent: DataGenUserIntentSchema,
    request: Request,
    traced_logger=Depends(get_transaction_logger),
):
    """
    用户反馈确认
    :param user_intent:
    :param request
    :param traced_logger
    :return:
    """
    session_id = traced_logger.get_trace_uuid()
    logger.info(f"[数据生成Graph] 初始化图并运行: {user_intent.model_dump_json()}")
    resp_data = ResponseBaseSchema(description="[数据生成Graph] 初始化图并运行")
    client_ip = extract_client_ip(request)
    resp_data.session_id = session_id
    init_state = {
        "user_input": user_intent.model_dump_json(),
        "user_intent": user_intent,
        "human_intent_feedback": "正确",
        "max_retries": 3,
        "session_id": session_id,
        "client_ip": client_ip,
        "mode": 1,
    }

    thread: RunnableConfig = {"configurable": {"thread_id": session_id}}
    event = await data_gen_graph.ainvoke(init_state, thread, stream_mode="values")
    for error in [
        "table_metadata_error",
        "create_data_genius_task_error",
        "query_data_genius_task_error",
    ]:
        if event.get(error):
            logger.error(f"[数据生成Graph] {error}: {event.get(error)}")
            resp_data.data = event
            resp_data.message = (
                f"{error_code.GRAPH_NODE_ERROR.get('description')} {event.get(error)}"
            )
            resp_data.code = error_code.GRAPH_NODE_ERROR.get("code")
            return resp_data.model_dump()
    if event.get("data_genius_plan_output_url"):
        if table_metadata_info := event.get("table_metadata_info"):
            table_metadata_info_data = table_metadata_info.model_dump()
        else:
            table_metadata_info_data = {}
        result = {
            "table_metadata_info": table_metadata_info_data,
            "data_genius_plan_task_id": event["data_genius_plan_task_id"],
            "data_genius_plan_run_duration": event["data_genius_plan_run_duration"],
            "data_genius_plan_output_url": event["data_genius_plan_output_url"],
            "data_genius_plan_output_filesize": event[
                "data_genius_plan_output_filesize"
            ],
            "data_genius_plan_edit_url": event["data_genius_plan_edit_url"],
        }
        logger.info(f"[数据生成Graph] 结果: {json.dumps(result)}")
        resp_data.data = event
    return resp_data.model_dump()
