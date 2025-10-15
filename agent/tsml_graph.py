#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/10/15 15:31
# @Author   : guoqun X2590
# @Desc     :

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.state import TSMLState


def validate_tsml_input_args(state: TSMLState):
    """校验tsml图的输入信息,若没有提示用户提供所需内容"""
    tsml_file_info = state.get("tsml_file_info")
    if tsml_file_info:
        logger.debug(f"tsml_file_info: {tsml_file_info.model_dump_json()}")
        state["tsml_validate"] = True
    else:
        logger.warning("用户未上传tsml文件")
        state["messages"].append(AIMessage(content="请上传tsml文件"))
        state["tsml_validate"] = False
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
    tsml_file_info = state.get("tsml_file_info")
    tsml_validate = state.get("tsml_validate")
    logger.debug(
        f"last_message: {type(last_message)} {last_message} "
        f"tsml_file_info={tsml_file_info} tsml_validate={tsml_validate} "
    )
    if last_message and isinstance(last_message, HumanMessage):
        logger.debug(f"latest human message: content={last_message.content}")
        state["user_input"] = str(last_message.content)
    return state


tsml_builder = StateGraph(TSMLState)
tsml_builder.add_node("validate_tsml_input_args", validate_tsml_input_args)
tsml_builder.add_node("analyze_tsml_intent", analyze_tsml_intent)

tsml_builder.add_edge(START, "validate_tsml_input_args")
tsml_builder.add_edge("validate_tsml_input_args", "analyze_tsml_intent")
# tsml_builder.add_conditional_edges(
#     START, validate_tsml_input_args, ["analyze_tsml_intent", END]
# )
tsml_builder.add_edge("analyze_tsml_intent", END)

memory = InMemorySaver()
tsml_graph = tsml_builder.compile(checkpointer=memory)
