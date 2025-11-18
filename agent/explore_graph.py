#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/23 15:08
# @Author   : guoqun X2590
# @Desc     : 自由探索

import json

from fastapi.encoders import jsonable_encoder
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from loguru import logger

from agent.llm import chat_llm
from agent.prompt import expolore_chat_prompt
from agent.state import ExploreState
from cruds.dynamic_query import query_sql
from cruds.table_metadata import table_metadata_fuzzy_query
from utils.db_manager import DatabaseManager


@tool
def metadata_table_statistic_tool():
    """查询当前已经有多少元数据表"""
    db_manager = None
    try:
        db_manager = DatabaseManager()
        sql = """select count(*) as total_number, "source", env_name
        from table_meta_data_info tmdi group by "source" ,env_name ;"""
        status, message, result = query_sql(db_manager=db_manager, sql_text=sql)
        if status is False:
            message = f"查询当前已经有多少元数据表异常: {message}"
            logger.error(message)
            return message
        else:
            logger.info(
                f"查询当前已经有多少元数据表: "
                f"type(result)={type(result)} result={result}"
            )
            return jsonable_encoder(result)
    except Exception as err:
        message = f"初始化数据库链接失败: {err}"
        logger.error(message)
        return message
    finally:
        if db_manager:
            db_manager.close()


@tool(return_direct=True)
def metadata_table_filter_tool(table_name: str, env_name: str = ""):
    """根据表名称模糊查询符合条件的表的元数据信息,
    如果有环境名称可以根据环境名称缩小查询范围

    Args:
        table_name (str): 表名称,可以是英文名或中文名
        env_name (str): 环境名称, 默认为空字符串
    """
    db_manager = None
    try:
        db_manager = DatabaseManager()
        status, message, result = table_metadata_fuzzy_query(
            table_name=table_name, env_name=env_name, db_manager=db_manager
        )
        if status is False:
            message = (
                f"根据条件table_name={table_name}, env_name={env_name},"
                f"模糊查询表元数据异常: {message}"
            )
            logger.error(message)
            return message
        else:
            # data = [ele.to_dict() for ele in result]
            logger.info(
                f"根据条件table_name={table_name}, env_name={env_name},"
                f"模糊查询表元数据结果共计{len(result)}个,"
                f"表名分别是: {[ele.table_en_name for ele in result]}"
            )
            return jsonable_encoder(result)
    except Exception as err:
        message = f"初始化数据库链接失败: {err}"
        logger.error(message)
        return message
    finally:
        if db_manager:
            db_manager.close()


tool_register = [metadata_table_statistic_tool, metadata_table_filter_tool]

llm_with_tool = chat_llm.bind_tools(tools=tool_register)
tool_node = ToolNode(tool_register)


def explore_chat(state: ExploreState) -> ExploreState:
    """探索对话哦

    Args:
        state (ExploreState): _description_

    Returns:
        ExploreState: _description_
    """
    messages = state["messages"]
    last_message = messages[-1]
    logger.debug(f"last_message: {type(last_message)} {last_message}")
    if last_message and isinstance(last_message, HumanMessage):
        logger.debug(f"latest human message: content={last_message.content}")
        state["question"] = str(last_message.content)
        chat_prompt = expolore_chat_prompt.format_messages(question=last_message)
        response = llm_with_tool.invoke(input=chat_prompt)
        logger.info(f"response: {type(response)} {response}")
        state["messages"].append(response)
        if (
            isinstance(response, AIMessage)
            and response.tool_calls
            and len(response.tool_calls) > 0
        ):
            logger.debug(f"AI message: tool_calls={response.tool_calls}")
            state["tool_name"] = response.tool_calls[0]["name"]
            state["tool_args"] = response.tool_calls[0]["args"]
    elif (
        last_message and isinstance(last_message, ToolMessage) and last_message.content
    ) and last_message.name:
        logger.debug(
            f"last tool message: "
            f"tool_name={last_message.name} content={last_message.content}"
        )
        if last_message.name == state.get("tool_name"):
            state["tool_call_result"] = last_message.content
        else:
            logger.warning(
                f"当前获取的是工具{last_message.name}执行结果, "
                f"与上一轮AI调用的工具名称{state.get('tool_name')}不同"
            )
    return state


def should_continue(state: ExploreState):
    """决定是继续调用工具还是结束"""
    messages = state["messages"]
    last_message = messages[-1]
    logger.debug(f"last_message: {type(last_message)} {last_message}")
    if (
        isinstance(last_message, AIMessage)
        and last_message.tool_calls
        and len(last_message.tool_calls) > 0
    ):
        return "tool_node"
    else:
        return "filter_and_summarize_data"


def filter_and_summarize_data(state: ExploreState) -> ExploreState:
    """根据数据库查询工具类型精简数据库查询结果，保留必要字段，为大模型总结准备。"""
    tool_name = ""
    tool_call_result = None
    if tool_call_result := state.get("tool_call_result"):
        logger.trace(
            f"tool_call_result => type={type(tool_call_result)} value={tool_call_result}"
        )
        if tool_call_result and isinstance(tool_call_result, str):
            if tool_name := state.get("tool_name"):
                if tool_name == "metadata_table_filter_tool":
                    logger.info(
                        "metadata_table_filter_tool工具调用结果, 只保留表的中文名和英文名"
                    )
                    # 只保留表的中文名和英文名
                    summarize_data = [
                        {
                            "table_en_name": ele.get("table_en_name"),
                            "table_cn_name": ele.get("table_cn_name"),
                        }
                        for ele in json.loads(tool_call_result)
                    ]
                    state["summarize_tool_call_result"] = summarize_data
    return state


def summary_node(state: ExploreState) -> ExploreState:
    logger.info("summary_node running...")
    messages = state["messages"]
    last_message = messages[-1]
    question = state.get("question", "")
    logger.debug(f"question: {question}")
    # logger.debug(f"last_message: {type(last_message)} {last_message}")
    tool_call_result = state.get("tool_call_result")
    if tool_call_result:
        logger.info(f"tool_call_result length: {len(tool_call_result)}")
    summarize_tool_call_result = state.get("summarize_tool_call_result")
    if summarize_tool_call_result:
        logger.info(
            f"summarize_tool_call_result length: {len(summarize_tool_call_result)}"
        )
    tool_result = summarize_tool_call_result or tool_call_result
    if tool_result:
        prompt = [
            SystemMessage("按照用户的提问, 总结以下信息, 遵循事实"),
            HumanMessage(content=question),
            json.dumps(tool_result, ensure_ascii=False),
        ]
        logger.info(f"with tool result summary prompt: {prompt}")
        summary_result = chat_llm.invoke(prompt)
    elif last_message.content:
        prompt = [
            SystemMessage(
                "按照用户的提问, 总结以下信息, 遵循事实, 不知道的就告诉用户说你不知道"
            ),
            HumanMessage(content=question),
            last_message,
        ]
        logger.info(f"without tool result summary prompt: {prompt}")
        summary_result = chat_llm.invoke(prompt)
    else:
        # 工具查询没结果，兜底逻辑，不知道就是不知道
        summary_result = AIMessage(content="对不起, 我不知道。")
    if summary_result.content:
        logger.info(f"summary_result: {type(summary_result)} {summary_result}")
        state["summary"] = summary_result.content
        state["messages"].append(summary_result)
    else:
        # 取上一轮的AI输出作为结果
        logger.info("总结AI的结果是空的, 取上一轮AI的结果")
        not_none_ai_messages = [
            ele
            for ele in messages
            if (isinstance(ele, AIMessage) and ele.content != "")
        ]
        if not_none_ai_messages:
            last_ai_message = not_none_ai_messages[-1]
            logger.info(f"最后一轮非空AI的结果: {last_ai_message}")
            state["summary"] = last_ai_message.content
            state["messages"].append(last_ai_message)
    return state


explore_builder = StateGraph(ExploreState)
explore_builder.add_node("tool_node", tool_node)
explore_builder.add_node("explore_chat", explore_chat)
explore_builder.add_node("filter_and_summarize_data", filter_and_summarize_data)
explore_builder.add_node("summary_node", summary_node)


explore_builder.add_edge(START, "explore_chat")
explore_builder.add_conditional_edges(
    "explore_chat", should_continue, ["tool_node", "filter_and_summarize_data"]
)
explore_builder.add_edge("tool_node", "explore_chat")
explore_builder.add_edge("filter_and_summarize_data", "summary_node")
explore_builder.add_edge("summary_node", END)

memory = InMemorySaver()
expolore_graph = explore_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import uuid

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager, TracedLogger

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="Explore.log",
        console_log_level="DEBUG",
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))

    init_env()
    print(expolore_graph.get_graph(xray=True).draw_mermaid())

    session_id = uuid.uuid4().hex

    traced_logger = TracedLogger()
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        traced_logger.set_trace_uuid(session_id)

    run_config = RunnableConfig(configurable={"thread_id": session_id})

    init_state = {
        "messages": HumanMessage(content="当前有多少元数据表"),
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": "10.0.23.57",
    }

    for index, event in enumerate(
        expolore_graph.stream(init_state, run_config, stream_mode="values")
    ):
        logger.debug(f"event ==> index={index} {event}")
        if summary := event.get("summary"):
            logger.info(f"summary={summary}")
        if tool_name := event.get("tool_name"):
            logger.info(f"tool_name={tool_name}")
        if tool_args := event.get("tool_args"):
            logger.info(f"tool_args={tool_args}")
        if tool_call_result := event.get("tool_call_result"):
            logger.info(
                f"tool_call_result={tool_call_result} "
                f"type(tool_call_result)={type(tool_call_result)}"
            )
        if summarize_tool_call_result := event.get("summarize_tool_call_result"):
            logger.info(
                f"summarize_tool_call_result={summarize_tool_call_result} "
                f"type(summarize_tool_call_result)={type(summarize_tool_call_result)}"
            )

    logger.info("===============新的问题开始了===============")

    # 2. 再次提问
    expolore_graph.update_state(
        run_config,
        {"messages": HumanMessage("给我 NB_APP_SKE_BINDPHONE 表的字段信息")},
        as_node="explore_chat",
    )

    for index, event in enumerate(
        expolore_graph.stream(init_state, run_config, stream_mode="values")
    ):
        logger.debug(f"event ==> index={index} {event}")
        if summary := event.get("summary"):
            logger.info(f"summary={summary}")
        if tool_name := event.get("tool_name"):
            logger.info(f"tool_name={tool_name}")
        if tool_args := event.get("tool_args"):
            logger.info(f"tool_args={tool_args}")
        if tool_call_result := event.get("tool_call_result"):
            logger.info(
                f"tool_call_result={tool_call_result}"
                f"type(tool_call_result)={type(tool_call_result)}"
            )
        if summarize_tool_call_result := event.get("summarize_tool_call_result"):
            logger.info(
                f"summarize_tool_call_result={summarize_tool_call_result} "
                f"type(summarize_tool_call_result)={type(summarize_tool_call_result)}"
            )
