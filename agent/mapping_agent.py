# coding: utf-8
# @Time:     2025/5/7 11:40
# @Author:   toddlerya
# @FileName: mapping_agent.py
# @Project:  DataForge
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.state import FieldMappingState


def create_table_raw_field_info(state: FieldMappingState):
    table_en_name = state.get("table_en_name", "")
    logger.debug(f"table_en_name {table_en_name}")
    # 查询知识库获取表的字段配置信息
    # 模拟查询
    from agent.field_map_fill_agent.mock_data import MockTableMetadata

    if table_en_name.upper() in MockTableMetadata().__dir__():
        raw_fields_info = MockTableMetadata().__getattribute__(table_en_name.upper())
    else:
        raw_fields_info = "未查询到该表的字段配置信息"
    return {"raw_fields_info": raw_fields_info}


def human_feedback(state: FieldMappingState):
    """No-op node that should be interrupted on"""
    pass


def should_continue(state: FieldMappingState):
    """Return the next node to execute"""

    # Check if human feedback
    human_mapping_feedback = state.get("human_mapping_feedback", "")
    if human_mapping_feedback:
        return "create_table_raw_field_info"

    # Otherwise end
    return END


builder = StateGraph(FieldMappingState)
builder.add_node("create_table_raw_field_info", create_table_raw_field_info)
builder.add_node("human_feedback", human_feedback)
builder.add_edge(START, "create_table_raw_field_info")
builder.add_edge("create_table_raw_field_info", "human_feedback")
builder.add_conditional_edges(
    "human_feedback", should_continue, ["create_table_raw_field_info", END]
)


memory = MemorySaver()
mapping_graph = builder.compile(
    interrupt_before=["human_feedback"], checkpointer=memory
)


if __name__ == "__main__":
    print(mapping_graph.get_graph().draw_mermaid())
