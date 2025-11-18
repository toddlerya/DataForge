#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/28 17:16
# @Author   : guoqun X2590
# @Desc     : 单独运行SQL生成模式


from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from loguru import logger

from agent.dg_graph import process_dg_graph
from agent.sql_mode_data_graph import sql_mode_data_gen_graph
from agent.state import SQLModeDataGenState

standalone_sql_gen_builder = StateGraph(SQLModeDataGenState)

standalone_sql_gen_builder.add_node("sql_mode_data_gen_graph", sql_mode_data_gen_graph)
standalone_sql_gen_builder.add_node("process_dg_graph", process_dg_graph)


standalone_sql_gen_builder.add_edge(START, "sql_mode_data_gen_graph")
standalone_sql_gen_builder.add_edge("sql_mode_data_gen_graph", "process_dg_graph")
standalone_sql_gen_builder.add_edge("process_dg_graph", END)


memory = InMemorySaver()
standalone_sql_gen_graph = standalone_sql_gen_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import pathlib
    import uuid

    from langchain_core.runnables.config import RunnableConfig

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
    graph_mermaid = standalone_sql_gen_graph.get_graph(xray=True).draw_mermaid()
    print(graph_mermaid)
    logger.info("\n" + graph_mermaid)

    session_id = uuid.uuid4().hex

    traced_logger = TracedLogger()
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        traced_logger.set_trace_uuid(session_id)

    user_input = """SQL内容(必填): select MD_ID, ACCOUNTNAME, USERNUM
     from XY_BF_ACCOUNT
    期望生成数据条数(必填): 100"""
    run_config: RunnableConfig = {"configurable": {"thread_id": session_id}}

    init_state = {
        "user_input": user_input,
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    logger.info("===== 步骤1  先执行到中断")
    # 1. 先流式执行到中断点
    for event in standalone_sql_gen_graph.stream(
        init_state, run_config, stream_mode="updates"
    ):
        logger.info(f"standalone_sql_gen_graph event: {event}")

    logger.info("===== 步骤2  更新用户反馈状态")
    # 更新用户反馈
    resume_map = {"human_intent_feedback": "Y"}

    # 继续运行
    standalone_sql_gen_graph.invoke(Command(resume=resume_map), config=run_config)
