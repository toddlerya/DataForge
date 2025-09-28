#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/24 10:01
# @Author   : guoqun X2590
# @Desc     : 主图

import uuid

from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from loguru import logger

from agent.dg_graph import process_dg_graph
from agent.explore_graph import expolore_graph
from agent.llm import chat_llm
from agent.meta_mode_data_graph import meta_mode_data_gen_graph
from agent.prompt import main_intent_prompt
from agent.sql_mode_data_graph import sql_mode_data_gen_graph
from agent.state import AppUserIntentSchema, MainAppState


def analyze_intent(state: MainAppState) -> MainAppState:
    messages = state.get("messages")
    logger.trace(f"messages: {messages}")
    last_message = messages[-1]
    if last_message and isinstance(last_message, HumanMessage):
        logger.debug(f"latest human message: content={last_message.content}")
        structured_llm = chat_llm.with_structured_output(AppUserIntentSchema)
        chat_promt = main_intent_prompt.format_messages(user_input=last_message)
        logger.trace(f"analyze_intent chat_prompt: {chat_promt}")
        try:
            main_user_intent = structured_llm.invoke(chat_promt)
        except Exception as err:
            err_message = f"意图解析异常: {err}"
            logger.error(err_message)
            messages.append(AIMessage(err_message))
        else:
            logger.info(
                f"last_message: {last_message} main_user_intent: {main_user_intent}"
            )
            if isinstance(main_user_intent, AppUserIntentSchema):
                state["next_sub_graph_name"] = main_user_intent.sub_graph_name
                state["user_input"] = main_user_intent.user_input
    return state


def clear_main_state(
    state: MainAppState,
) -> MainAppState:
    if subgraph_control := state.get("subgraph_control", {}):
        if not subgraph_control.get("clear_main_state"):
            # 不需要清理
            return state
    # 需要保留的跨任务的状态
    persistent_data = {
        "session_id": state.get("session_id"),
        "client_ip": state.get("client_ip"),
        "max_retries": state.get("max_retries", 5),
        # 只保留最新的消息
        "messages": state.get("messages", [])[-1:],
    }
    clean_state: MainAppState = {
        **persistent_data,
        "user_intent": None,  # type: ignore
        "next_sub_graph_name": "",
        "user_input": "",
        "human_intent_feedback": "",
        "dont_run_dg_task": False,
    }
    return clean_state


# def invoke_expolore_graph(state: MainAppState):
#     return expolore_graph.invoke(state)


# def invoke_meta_mode_data_gen_graph(state: MainAppState):
#     return meta_mode_data_gen_graph.invoke(state)


# def invoke_sql_mode_data_gen_graph(state: MainAppState):
#     return sql_mode_data_gen_graph.invoke(state)


# def invoke_process_dg_graph(state: MainAppState):
#     return process_dg_graph.invoke(state)


def sub_graph_route(state: MainAppState):
    """子图路由器

    Args:
        state (MainAppState): _description_
    """
    if next_sub_graph_name := state.get("next_sub_graph_name").strip():
        if next_sub_graph_name == "expolore_graph":
            return "expolore_graph"
        elif next_sub_graph_name == "meta_mode_data_gen_graph":
            return "meta_mode_data_gen_graph"
        elif next_sub_graph_name == "sql_mode_data_gen_graph":
            return "sql_mode_data_gen_graph"
        else:
            return END
    else:
        return END


main_builder = StateGraph(MainAppState)
main_builder.add_node("clear_main_state", clear_main_state)
main_builder.add_node("analyze_intent", analyze_intent)
main_builder.add_node("expolore_graph", expolore_graph)
main_builder.add_node("meta_mode_data_gen_graph", meta_mode_data_gen_graph)
main_builder.add_node("sql_mode_data_gen_graph", sql_mode_data_gen_graph)
main_builder.add_node("process_dg_graph", process_dg_graph)


main_builder.add_edge(START, "clear_main_state")
main_builder.add_edge("clear_main_state", "analyze_intent")
main_builder.add_conditional_edges(
    "analyze_intent",
    sub_graph_route,
    [
        "expolore_graph",
        "meta_mode_data_gen_graph",
        "sql_mode_data_gen_graph",
        END,
    ],
)
main_builder.add_edge("meta_mode_data_gen_graph", "process_dg_graph")
main_builder.add_edge("sql_mode_data_gen_graph", "process_dg_graph")
main_builder.add_edge("process_dg_graph", END)

memory = InMemorySaver()
main_graph = main_builder.compile(checkpointer=memory)


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
    print(main_graph.get_graph(xray=True).draw_mermaid())

    session_id = uuid.uuid4().hex

    traced_logger = TracedLogger()
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        traced_logger.set_trace_uuid(session_id)

    run_config: RunnableConfig = {"configurable": {"thread_id": session_id}}

    meta_data_gen_input = "生成10条massdata.ADM_REL_MOBILE表的测试数据"
    sql_data_gen_input = "select MD_ID from massdata.ADM_REL_MOBILE, 生成100条数据"

    init_state = {
        "messages": HumanMessage(content=sql_data_gen_input),
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    # 先流式执行到中断点
    for event in main_graph.stream(init_state, run_config, stream_mode="values"):
        logger.info(f"before interupt event: {event}")

    # 更新用户反馈
    resume_map = {"human_intent_feedback": "Y"}

    # 继续运行
    main_graph.invoke(Command(resume=resume_map), config=run_config)
