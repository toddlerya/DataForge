#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/6/16 16:40 
# @Author   : guoqun X2590
# @FileName : table_graph.py
# @Project  : DataForge


from loguru import logger
import httpx
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.llm import chat_llm
from agent.prompt import table_intent_prompt
from agent.state import (TableGenState, TableGenUserIntentSchema)
from utils.db import Database



def analyze_table_intent(state: TableGenState) -> TableGenState:
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {user_input} human_intent_feedback: {human_intent_feedback}"
    )
    structured_llm = chat_llm.with_structured_output(TableGenUserIntentSchema)
    chat_prompt = table_intent_prompt.format_messages(
        user_input=user_input, human_intent_feedback=human_intent_feedback
    )
    logger.trace(f"analyze_intent chat_prompt: {chat_prompt}")
    user_intent = structured_llm.invoke(chat_prompt)
    state["user_intent"] = user_intent
    logger.debug(f"user_intent: {user_intent}")
    return state


def table_intent_human_feedback():
    """No-op node that should be interrupted on"""
    pass


def should_table_intent_continue(state: TableGenState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确":
        return END

    # Otherwise proceed to create table info
    return "analyze_intent"


table_gen_builder = StateGraph(TableGenState)
table_gen_builder.add_node("analyze_table_intent", analyze_table_intent)
table_gen_builder.add_node("table_intent_human_feedback", table_intent_human_feedback)

table_gen_builder.add_edge(START, "analyze_table_intent")
table_gen_builder.add_edge("analyze_table_intent", "table_intent_human_feedback")
table_gen_builder.add_conditional_edges(
    "table_intent_human_feedback",
    should_table_intent_continue,
    ["analyze_table_intent", END],
)

memory = MemorySaver()
table_gen_graph = table_gen_builder.compile(
    interrupt_before=["table_intent_human_feedback"], checkpointer=memory
)

if __name__ == "__main__":
    print(table_gen_graph.get_graph(xray=True).draw_mermaid())
    user_input = """帮我生成一些人员属性、上网行为、位置轨迹类别的表，每个类别的表最少2张，最多10张，每个表的字段数量最少10个，最多100个"""
    thread = {"configurable": {"thread_id": "123"}}
    init_state = {
        "user_input": user_input
    }
    for event in table_gen_graph.stream(init_state, thread, stream_mode="values"):
        user_intent: TableGenUserIntentSchema = event.get("user_intent")
        if user_intent:
            logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")
    # 模拟用户意图识别的研判反馈
    table_gen_graph.update_state(thread, {"human_intent_feedback": "正确"}, as_node="table_intent_human_feedback")

    for event in table_gen_graph.stream(None, thread, stream_mode="values"):
        # Review
        human_intent_feedback = event.get("human_intent_feedback")
        if human_intent_feedback:
            logger.info(f"human_intent_feedback: {human_intent_feedback}")
