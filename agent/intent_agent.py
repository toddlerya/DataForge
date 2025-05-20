# coding: utf-8
# @Time:     2025/5/8 11:20
# @Author:   toddlerya
# @FileName: intent_agent.py
# @Project:  DataForge

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.llm import ollama_llm
from agent.prompt import prompt_intent_analyse
from agent.state import DataForgeState, UserIntentSchema


def analyze_agent(state: DataForgeState) -> dict:
    user_input = state.get("user_input", "")
    messages = state.get("messages", [])
    logger.debug(f"user_input: {user_input} messages: {messages}")

    structured_llm = ollama_llm.with_structured_output(UserIntentSchema)

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


def confirm(state: DataForgeState):
    """No-op node that should be interrupted on"""
    pass


def should_continue(state: DataForgeState):
    """Return the next node to execute"""

    # Check if human feedback
    confirmed = state.get("confirmed", False)
    if confirmed:
        return "analyze_agent"

    # Otherwise end
    return END


intent_builder = StateGraph(DataForgeState)
intent_builder.add_node("analyze_agent", analyze_agent)
intent_builder.add_node("confirm", confirm)
intent_builder.add_edge(START, "analyze_agent")
intent_builder.add_edge("analyze_agent", "confirm")
intent_builder.add_conditional_edges("confirm", should_continue, ["analyze_agent", END])

memory = MemorySaver()
intent_graph = intent_builder.compile(interrupt_before=["confirm"], checkpointer=memory)


if __name__ == "__main__":
    print(intent_graph.get_graph().draw_mermaid())
    thread = {"configurable": {"thread_id": "4895b601-c056-4af3-a1f3-6dfa03837744"}}
    event = intent_graph.invoke(
        {
            "user_input": """数据库表名称:
ADM_DOMAIN_WHOIS
ODS_TC_DOMAIN_WHOIS
期望表约束条件:
ADM_DOMAIN_WHOIS: DOMAIN IS NOT NULL
ODS_TC_DOMAIN_WHOIS: DOMAIN IS NOT NULL
期望生成数据条数:
ADM_DOMAIN_WHOIS: 2
ODS_TC_DOMAIN_WHOIS: 3"""
        },
        thread,
        stream_mode="values",
    )
    print(event)
