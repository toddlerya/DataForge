#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/24 10:01
# @Author   : guoqun X2590
# @Desc     : 主图


from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.explore_graph import expolore_graph
from agent.llm import chat_llm
from agent.prompt import main_intent_prompt
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
            user_intent = structured_llm.invoke(chat_promt)
        except Exception as err:
            err_message = f"意图解析异常: {err}"
            logger.error(err_message)
            messages.append(AIMessage(err_message))
        else:
            logger.info(f"last_message: {last_message} user_intent: {user_intent}")
            if isinstance(user_intent, AppUserIntentSchema):
                state["sub_graph_name"] = user_intent.graph_name
    return state


def run_expolore_graph(state: MainAppState) -> MainAppState:
    """运行自由探索子图

    Args:
        state (MainAppState): _description_

    Returns:
        MainAppState: _description_
    """
    messages = state.get("messages")
    logger.trace(f"messages: {messages}")
    last_message = messages[-1]
    if last_message and isinstance(last_message, HumanMessage):
        logger.debug(f"latest human message: content={last_message.content}")
        init_state = {
            "messages": last_message,
            "max_retries": state.get("max_retries"),
            "session_id": state.get("session_id"),
            "client_ip": state.get("client_ip"),
        }
        result = expolore_graph.invoke(init_state)
        logger.info(f"result: {result}")
    return state


def decide_next_step(state: MainAppState):
    """选择下一步的节点

    Args:
        state (MainAppState): _description_
    """
    if state.get("sub_graph_name").strip() == "expolore_graph":
        return "run_expolore_graph"
    else:
        return END


main_builder = StateGraph(MainAppState)
main_builder.add_node("analyze_intent", analyze_intent)
main_builder.add_node("run_expolore_graph", run_expolore_graph)


main_builder.add_edge(START, "analyze_intent")
main_builder.add_conditional_edges(
    "analyze_intent",
    decide_next_step,
    {"run_expolore_graph": "run_expolore_graph", END: END},
)

memory = InMemorySaver()
main_graph = main_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import uuid

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="MainAPp.log",
        console_log_level="DEBUG",
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

    thread: RunnableConfig = {"configurable": {"thread_id": session_id}}

    init_state = {
        "messages": HumanMessage(content="与手机号相关的表有哪些 "),
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    # 1. 先流式执行到中断点
    for event in main_graph.stream(init_state, thread, stream_mode="values"):
        logger.info(f"event: {event}")
