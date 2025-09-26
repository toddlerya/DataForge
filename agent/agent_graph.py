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

from agent.data_graph import data_gen_graph
from agent.explore_graph import expolore_graph
from agent.llm import chat_llm
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
            user_intent = structured_llm.invoke(chat_promt)
        except Exception as err:
            err_message = f"意图解析异常: {err}"
            logger.error(err_message)
            messages.append(AIMessage(err_message))
        else:
            logger.info(f"last_message: {last_message} user_intent: {user_intent}")
            if isinstance(user_intent, AppUserIntentSchema):
                state["next_sub_graph_name"] = user_intent.sub_graph_name
                state["user_input"] = user_intent.user_input
    return state


def invoke_expolore_graph(state: MainAppState):
    return expolore_graph.invoke(state)


def invoke_data_gen_graph(state: MainAppState):
    return data_gen_graph.invoke(state)


def invoke_sql_mode_data_gen_graph(state: MainAppState):
    return sql_mode_data_gen_graph.invoke(state)


def sub_graph_route(state: MainAppState):
    """子图路由器

    Args:
        state (MainAppState): _description_
    """
    if next_sub_graph_name := state.get("next_sub_graph_name").strip():
        if next_sub_graph_name == "expolore_graph":
            return "expolore_graph"
        elif next_sub_graph_name == "data_gen_graph":
            return "data_gen_graph"
        elif next_sub_graph_name == "sql_mode_data_gen_graph":
            return "sql_mode_data_gen_graph"
        else:
            return END
    else:
        return END


main_builder = StateGraph(MainAppState)
main_builder.add_node("analyze_intent", analyze_intent)
main_builder.add_node("expolore_graph", invoke_expolore_graph)
main_builder.add_node("data_gen_graph", invoke_data_gen_graph)
main_builder.add_node("sql_mode_data_gen_graph", invoke_sql_mode_data_gen_graph)


main_builder.add_edge(START, "analyze_intent")
main_builder.add_conditional_edges(
    "analyze_intent",
    sub_graph_route,
    [
        "expolore_graph",
        "data_gen_graph",
        "sql_mode_data_gen_graph",
        END,
    ],
)

memory = InMemorySaver()
main_graph = main_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import uuid

    from langgraph.types import Command

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="AgentGraph.log",
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

    run_config: RunnableConfig = {"configurable": {"thread_id": session_id}}

    data_gen_input = "生成10条massdata.ADM_REL_MOBILE表的测试数据"
    sql_data_gen_input = "select MD_ID from massdata.ADM_REL_MOBILE"

    init_state = {
        "messages": HumanMessage(content=data_gen_input),
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    # 先流式执行到中断点
    for event in main_graph.stream(init_state, run_config, stream_mode="values"):
        logger.info(f"before interupt event: {event}")

    # 更新用户反馈
    resume_map = {"human_intent_feedback": "Y"}
    # main_graph.update_state(
    #     config=run_config,
    #     values=resume_map,
    # )

    # 继续运行
    main_graph.invoke(Command(resume=resume_map), config=run_config)

    # 新的结果
    # for event in main_graph.stream(init_state, run_config, stream_mode="values"):
    #     logger.info(f"after interupt event: {event}")
