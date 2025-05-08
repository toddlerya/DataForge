#!/usr/bin/env python
# coding: utf-8
# @File    :   graph.py
# @Time    :   2025/05/08 17:26:30
# @Author  :   toddlerya
# @Desc    :   None

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.gen_faker_data_agent import gen_faker_data_builder
from agent.intent_agent import intent_builder
from agent.state import DataForgeState

builder = StateGraph(DataForgeState)
builder.add_node("input_intent_agent", intent_builder.compile())
builder.add_node("input_gen_faker_data_agent", gen_faker_data_builder.compile())

builder.add_edge(START, "input_intent_agent")
builder.add_edge("input_intent_agent", "input_gen_faker_data_agent")
builder.add_edge("input_gen_faker_data_agent", END)

memory = MemorySaver()
data_forge_graph = builder.compile(checkpointer=memory)


if __name__ == "__main__":
    print(data_forge_graph.get_graph(xray=True).draw_mermaid())
    thread = {"configurable": {"thread_id": "4895b601-c056-4af3-a1f3-6dfa03837744"}}
    event = data_forge_graph.invoke(
        {
            "user_input": """数据库表名称:
adm_test
ods_test
期望表约束条件:
adm_test: from_city_code != to_city_code and datetime = 20250508 and ods_test.phone = adm_test.phone
ods_test: idcard is not null and phone is not null
期望生成数据条数:
adm_test: 10
ods_test: 20"""
        },
        thread,
        stream_mode="values",
    )
