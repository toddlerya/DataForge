#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/23 15:08
# @Author   : guoqun X2590
# @Desc     : 探索


from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from loguru import logger

from agent.llm import chat_llm
from agent.prompt import explore_intent_prompt
from agent.state import ExploreState, ExploreUserIntentSchema
from cruds.dynamic_query import query_sql
from utils.db_manager import DatabaseManager


@tool
def metadata_table_statistic_tool():
    """查询当前已经有多少元数据表"""
    db_manager = DatabaseManager()
    sql = """select count(*) as total_number, "source", env_name 
    from table_meta_data_info tmdi group by "source" ,env_name ;"""
    status, message, result = query_sql(db_manager=db_manager, sql_text=sql)
    if status is False:
        message = f"查询当前已经有多少元数据表异常: {message}"
        logger.error(message)
        return message
    else:
        logger.info(f"查询当前已经有多少元数据表: result={result}")
        return result


llm_with_tool = chat_llm.bind_tools(tools=[metadata_table_statistic_tool])


def analyze_explore_intent(state: ExploreState) -> ExploreState:
    messages = state.get("messages")
    logger.trace(f"messages: {messages}")
    last_message = messages[-1]
    if last_message and isinstance(last_message, HumanMessage):
        logger.debug(f"latest human message: content={last_message.content}")
        structured_llm = chat_llm.with_structured_output(ExploreUserIntentSchema)
        chat_promt = explore_intent_prompt.format_messages(user_input=last_message)
        logger.trace(f"analyze_explore_intent chat_prompt: {chat_promt}")
        try:
            user_intent = structured_llm.invoke(chat_promt)
        except Exception as err:
            err_message = f"意图解析异常: {err}"
            logger.error(err_message)
            messages.append(AIMessage(err_message))
        else:
            logger.info(f"last_message: {last_message} user_intent: {user_intent}")
    return state


def intent_human_feedback_node(state: ExploreState):
    """No-op node that should be interrupted on"""
    return state


def explore_chat(state: ExploreState) -> ExploreState:
    """探索对话哦

    Args:
        state (ExploreState): _description_

    Returns:
        ExploreState: _description_
    """
    messages = state["messages"]

    response = llm_with_tool.invoke(input=messages)
    logger.info(f"response: {type(response)} {response}")
    return {"messages": response}


def should_continue(state: ExploreState):
    """决定是继续调用工具还是结束"""
    messages = state["messages"]
    last_message = messages[-1]
    logger.debug(f"last_message: {type(last_message)} {last_message}")
    if isinstance(last_message, AIMessage):
        if last_message.tool_calls and len(last_message.tool_calls) > 0:
            return "tool_node"
    return END


tool_node = ToolNode([metadata_table_statistic_tool])

explore_builder = StateGraph(ExploreState)
explore_builder.add_node("analyze_explore_intent", analyze_explore_intent)
explore_builder.add_node("intent_human_feedback_node", intent_human_feedback_node)
explore_builder.add_node("tool_node", tool_node)
explore_builder.add_node("explore_chat", explore_chat)


explore_builder.add_edge(START, "explore_chat")
explore_builder.add_conditional_edges(
    "explore_chat", should_continue, ["tool_node", END]
)
explore_builder.add_edge("tool_node", "explore_chat")

memory = InMemorySaver()
data_gen_graph = explore_builder.compile(
    interrupt_before=["intent_human_feedback_node"], checkpointer=memory
)


if __name__ == "__main__":
    import uuid

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="DataForgeDataGenApp.log",
        console_log_level="DEBUG",
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

    thread: RunnableConfig = {"configurable": {"thread_id": session_id}}

    init_state = {
        "messages": HumanMessage(content="现在有多少元数据表？"),
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    # 1. 先流式执行到中断点
    for event in data_gen_graph.stream(init_state, thread, stream_mode="values"):
        logger.info(f"event: {event}")
