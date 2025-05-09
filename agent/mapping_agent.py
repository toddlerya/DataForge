# coding: utf-8
# @Time:     2025/5/7 11:40
# @Author:   toddlerya
# @FileName: mapping_agent.py
# @Project:  DataForge


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.state import (
    DataForgeState,
    TableMetadataSchema,
    TableRawFieldSchema,
    UserIntentSchema,
)


def create_table_raw_field_info(state: DataForgeState):
    intent_table_en_names = state.get("user_intent", UserIntentSchema()).table_en_names
    # 查询知识库获取表的字段配置信息
    # 模拟查询
    from agent.mock_data import MockTableMetadata

    for table_en_name in intent_table_en_names:
        table_metadata = TableMetadataSchema(table_en_name=table_en_name)
        if table_en_name.upper() in MockTableMetadata().__dir__():
            raw_fields_info = MockTableMetadata().__getattribute__(
                table_en_name.upper()
            )
            raw_fields_data = [
                TableRawFieldSchema(**ele)
                for ele in raw_fields_info
                if isinstance(ele, dict)
            ]
        else:
            raw_fields_info = ["未查询到该表的字段配置信息"]
            raw_fields_data = [TableRawFieldSchema()]
        table_metadata.raw_fields_info = raw_fields_data
        state.table_metadata.append(table_metadata)


mapping_builder = StateGraph(DataForgeState)
mapping_builder.add_node("create_table_raw_field_info", create_table_raw_field_info)
mapping_builder.add_edge(START, "create_table_raw_field_info")
mapping_builder.add_edge("create_table_raw_field_info", END)


memory = MemorySaver()
mapping_graph = mapping_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    print(mapping_graph.get_graph().draw_mermaid())
