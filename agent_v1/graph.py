#!/usr/bin/env python
# coding: utf-8
# @File    :   graph.py
# @Time    :   2025/05/08 17:26:30
# @Author  :   toddlerya
# @Desc    :   None

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent_v1.gen_faker_data_agent import gen_fake_data_builder
from agent_v1.intent_agent import intent_builder
from agent_v1.mapping_agent import mapping_builder
from agent_v1.state import DataForgeState

builder = StateGraph(DataForgeState)
builder.add_node("intent_agent", intent_builder.compile())
builder.add_node("mapping_agent", mapping_builder.compile())
builder.add_node("gen_fake_data_agent", gen_fake_data_builder.compile())

builder.add_edge(START, "intent_agent")
builder.add_edge("intent_agent", "mapping_agent")
builder.add_edge("mapping_agent", "gen_fake_data_agent")
builder.add_edge("gen_fake_data_agent", END)

memory = MemorySaver()
data_forge_graph = builder.compile(checkpointer=memory)


if __name__ == "__main__":
    print(data_forge_graph.get_graph(xray=True).draw_mermaid())
#     thread = {"configurable": {"thread_id": "4895b601-c056-4af3-a1f3-6dfa03837744"}}
#     event = data_forge_graph.invoke(
#         {
#             "user_input": """数据库表名称:
# ADM_DOMAIN_WHOIS
# ODS_TC_DOMAIN_WHOIS
# 期望表约束条件:
# ADM_DOMAIN_WHOIS: DOMAIN IS NOT NULL AND ADM_DOMAIN_WHOIS.DOMAIN = ODS_TC_DOMAIN_WHOIS.DOMAIN AND ADM_DOMAIN_WHOIS.LAST_TIME >= '2025-04-08'
# ODS_TC_DOMAIN_WHOIS: DOMAIN IS NOT NULL AND ADM_DOMAIN_WHOIS.DOMAIN = ODS_TC_DOMAIN_WHOIS.DOMAIN
# 期望生成数据条数:
# ADM_DOMAIN_WHOIS: 2
# ODS_TC_DOMAIN_WHOIS: 3""",
#             "table_metadata_array": [],
#         },
#         thread,
#         stream_mode="values",
#     )
#     print(event)
