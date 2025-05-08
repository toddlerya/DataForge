# coding: utf-8
# @Time:     2025/5/8 11:20
# @Author:   toddlerya
# @FileName: intent_agent.py
# @Project:  DataForge

from loguru import logger

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage

from agent.input_analyze_agent.state import UserIntentSchema, UserIntentState
from agent.llm import chat_llm
from agent.prompt import prompt_intent_analyse


def analyze_agent(state: UserIntentState) -> dict:
    user_input = state.get("user_input", "")
    messages = state.get("messages", [])
    logger.debug(f"user_input: {user_input} messages: {messages}")

    structured_llm = chat_llm.with_structured_output(UserIntentSchema)

    system_message = prompt_intent_analyse.format(
        user_input=user_input, messages=messages
    )
    logger.debug(f"system_message: {system_message}")
    user_intent = structured_llm.invoke(
        [
            SystemMessage(content=system_message),
            HumanMessage(content="分析用户输入的信息并结构化输出"),
        ]
    )
    logger.debug(f"user_intent: {user_intent}")
    return {"user_intent": user_intent}


def confirm(state: UserIntentState):
    """No-op node that should be interrupted on"""
    pass


def should_continue(state: UserIntentState):
    """Return the next node to execute"""

    # Check if human feedback
    confirmed = state.get("confirmed", False)
    if confirmed:
        return "analyze_agent"

    # Otherwise end
    return END


builder = StateGraph(UserIntentState)
builder.add_node("analyze_agent", analyze_agent)
builder.add_node("confirm", confirm)
builder.add_edge(START, "analyze_agent")
builder.add_edge("analyze_agent", "confirm")
builder.add_conditional_edges("confirm", should_continue, ["analyze_agent", END])

memory = MemorySaver()
intent_graph = builder.compile(interrupt_before=["confirm"], checkpointer=memory)


if __name__ == "__main__":
    print(intent_graph.get_graph().draw_mermaid())
    thread = {"configurable": {"thread_id": "4895b601-c056-4af3-a1f3-6dfa03837744"}}
    event = intent_graph.invoke(
        {"user_input": """数据库表名称:
adm_test
ods_test
期望表约束条件:
adm_test: from_city_code != to_city_code and datetime = 20250508 and ods_test.phone = adm_test.phone
ods_test: idcard is not null and phone is not null
期望生成数据条数:
adm_test: 10
ods_test: 20"""}, thread, stream_mode="values"
    )
