#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/10/15 15:31
# @Author   : guoqun X2590
# @Desc     :

import asyncio
import pathlib
from typing import Optional

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from loguru import logger

from agent.state import (
    ChainLitFileInfoSchema,
    PrepareTREFilesStatusSchema,
    TREExportFileSchema,
    TSMLState,
    TSMLUserIntentSchema,
)
from agent.tre_service_api_client import (
    tre_service_run,
    tre_service_status,
    tre_service_upload_file,
)


def validate_tsml_input_args(state: TSMLState):
    """校验tsml图的输入信息,若没有提示用户提供所需内容"""
    tre_export_file_info: Optional[TREExportFileSchema] = state.get(
        "tre_export_file_info"
    )
    logger.trace(f"tre_export_file_info={tre_export_file_info}")
    if (
        tre_export_file_info.tre_sql_file_info
        and tre_export_file_info.tre_tsml_file_info
    ):
        logger.debug(f"tre_export_file_info={tre_export_file_info.model_dump_json()} ")
        return "analyze_tsml_intent"
    else:
        logger.warning("用户未上传TRE导出的运行配置文件")
        return "wait_human_upload_tre_file"


def wait_human_upload_tre_file(state: TSMLState):
    tre_export_file_info = interrupt("请上传TRE导出的tsml文件和sql文件")
    state["tre_export_file_info"] = tre_export_file_info
    return state


def analyze_tsml_intent(state: TSMLState) -> TSMLState:
    """分析tsml意图

    Args:
        state (ExploreState): _description_

    Returns:
        ExploreState: _description_
    """
    messages = state["messages"]
    last_message = messages[-1]
    tre_export_file_info = state.get("tre_export_file_info")
    logger.debug(
        f"last_message: {type(last_message)} {last_message} "
        f"tre_export_file_info={tre_export_file_info}"
    )
    if tre_export_file_info:
        state["messages"].append(
            AIMessage(content=f"已收到TRE导出的文件: {tre_export_file_info}")
        )
        state["tsml_user_intent"] = TSMLUserIntentSchema(
            tre_export_file_info=tre_export_file_info,
            plans=[
                "1. 上传TRE导出的TSML文件和SQL文件给TRE_Test_Service处理",
                "2. 文件元数据解析",
                "3. 模型数据清洗",
                "4. TSML转换存储",
                "5. AI数据仿真",
                "6. 提交jenkins执行",
                "7. 获取执行结果",
            ],
        )
    return state


def upload_tre_files_node(state: TSMLState) -> TSMLState:
    """上传TRE运行所需文件"""
    logger.info("上传TRE文件")
    task_id = state.get("session_id")
    tre_export_file_info = state.get("tre_export_file_info")
    if not tre_export_file_info:
        logger.error("未获取需要上传的TRE文件")
        return state
    upload_file_info_slice: list[ChainLitFileInfoSchema] = []
    # 构建上传的TSML文件和SQL文件的数组
    if tre_tsml_file_info := tre_export_file_info.tre_tsml_file_info:
        upload_file_info_slice.append(tre_tsml_file_info)
    if tre_sql_file_info := tre_export_file_info.tre_sql_file_info:
        upload_file_info_slice.append(tre_sql_file_info)
    # 上传
    for each_file_info in upload_file_info_slice:
        upload_message, upload_resp_data = tre_service_upload_file(
            file_name=each_file_info.name,
            file_path=pathlib.Path(each_file_info.path),
            task_id=task_id,
        )
        if upload_message != "ok":
            state["messages"].append(AIMessage(content=upload_message))
        if upload_resp_data:
            state["prepare_tre_files_status"] = PrepareTREFilesStatusSchema(
                **upload_resp_data.get("files_status", {})
            )
            state["tre_task_id"] = upload_resp_data.get("task_id")
    return state


def should_call_tre_run(state: TSMLState):
    """是否文件齐全可以调用run接口"""
    prepare_tre_files_status = state.get("prepare_tre_files_status")
    if prepare_tre_files_status and prepare_tre_files_status.ready_to_run:
        return "call_tre_service_run"
    else:
        return "wait_human_upload_tre_file"


def call_tre_service_run(state: TSMLState):
    """调用run接口"""
    if task_id := state.get("tre_task_id"):
        logger.info(f"task_id={task_id}")
        run_message, run_resp_data = tre_service_run(task_id=task_id)
        logger.trace(f"run_message={run_message} run_resp_data={run_resp_data}")
        if run_message != "ok":
            # TODO: 此处还需要考虑重复提交任务的情况的
            state["messages"].append(AIMessage(content=run_message))
        if run_resp_data:
            state["status_url"] = run_resp_data.get("status_url")
    else:
        logger.error(f"没有获取到task_id: {task_id}")
    return state


def should_call_tre_status(state: TSMLState):
    status_url = state.get("status_url")
    if status_url:
        return "call_tre_service_status"
    else:
        return END


async def call_tre_service_status(state: TSMLState):
    """调用run接口"""
    if task_id := state.get("tre_task_id"):
        logger.info(f"task_id={task_id}")
        status_message, status_resp_data = await tre_service_status(task_id=task_id)
        logger.trace(
            f"status_message={status_message} status_resp_data={status_resp_data}"
        )
        if status_message != "ok":
            state["messages"].append(AIMessage(content=status_message))
        if status_resp_data:
            state["task_status"] = status_resp_data.get("task_status", "")
            state["now_step"] = status_resp_data.get("now_step", "")
            state["step_info"] = status_resp_data.get("step_info", {})
            state["completed"] = status_resp_data.get("completed", False)
            state["task_error"] = status_resp_data.get("error", "")
    else:
        logger.error(f"没有获取到task_id: {task_id}")
    state["wait_loop_count"] = 0
    return state


async def wait_done_route(state: TSMLState):
    wait_loop_count = state.get("wait_loop_count", 0)
    completed = state.get("completed", False)
    task_status = state.get("task_status", "")
    if task_status != "failed" and completed:
        return "finished"
    if task_status == "failed":
        return "error_exit"
    else:
        await asyncio.sleep(30)
        if wait_loop_count >= 10:
            return "error_exit"
        state["wait_loop_count"] += 1
        return "call_tre_service_status"


def error_exit(state: TSMLState):
    return state


def finished(state: TSMLState):
    step_info = state.get("step_info", {})
    step7_data = step_info.get("step7", {})
    if step7_data.get("status") == "已完成":
        result = step7_data.get("result", {})
        state["job_result_status"] = result.get("job_info", {}).get("job_result_status")
        state["report_url"] = result.get("job_info", {}).get("report_url")
    return state


tsml_builder = StateGraph(TSMLState)
tsml_builder.add_node("wait_human_upload_tre_file", wait_human_upload_tre_file)
tsml_builder.add_node("analyze_tsml_intent", analyze_tsml_intent)
tsml_builder.add_node("upload_tre_files_node", upload_tre_files_node)
tsml_builder.add_node("call_tre_service_run", call_tre_service_run)
tsml_builder.add_node("call_tre_service_status", call_tre_service_status)
tsml_builder.add_node("error_exit", error_exit)
tsml_builder.add_node("finished", finished)

tsml_builder.add_conditional_edges(
    START,
    validate_tsml_input_args,
    ["analyze_tsml_intent", "wait_human_upload_tre_file"],
)
tsml_builder.add_edge("wait_human_upload_tre_file", "analyze_tsml_intent")
tsml_builder.add_edge("analyze_tsml_intent", "upload_tre_files_node")
tsml_builder.add_conditional_edges(
    "upload_tre_files_node",
    should_call_tre_run,
    ["call_tre_service_run", "wait_human_upload_tre_file"],
)
tsml_builder.add_conditional_edges(
    "call_tre_service_run",
    should_call_tre_status,
    ["call_tre_service_status", END],
)
tsml_builder.add_conditional_edges(
    "call_tre_service_status",
    wait_done_route,
    ["error_exit", "finished", "call_tre_service_status"],
)
tsml_builder.add_edge("error_exit", END)
tsml_builder.add_edge("finished", END)

memory = InMemorySaver()
tsml_graph = tsml_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import pathlib

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager

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
    print(tsml_graph.get_graph(xray=True).draw_mermaid())
