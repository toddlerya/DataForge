# coding: utf-8
# @Time:     2025/5/7 11:40
# @Author:   toddlerya
# @FileName: mapping_agent.py
# @Project:  DataForge

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langchain_core.messages import ToolMessage
from loguru import logger

from agent_v1.state import (
    DataForgeState,
    TableMetadataSchema,
    UserIntentSchema,
)
from cruds.table_metadata import table_metadata_query
from database_models.schema import TableRawFieldSchema
from utils.db import Database


def create_table_raw_field_info(state: DataForgeState):
    intent_table_en_names = state.get("user_intent", {}).table_en_names
    # 查询知识库获取表的字段配置信息

    for table_en_name in intent_table_en_names:
        table_metadata = TableMetadataSchema(table_en_name=table_en_name)
        query_status, query_message, query_result = table_metadata_query(
            table_en_name=table_en_name, db_handler=Database()
        )
        if query_status is False:
            logger.error(f"查询{table_en_name}元数据异常: {query_result}")
            state["table_metadata_error"].append(
                f"查询{table_en_name}元数据异常: {query_result}"
            )
            raw_fields_data = [TableRawFieldSchema()]
            output_fields = {}
        elif query_result is None:
            logger.error(f"未查询到{table_en_name}元数据!")
            state["table_metadata_error"].append(f"未查询到{table_en_name}元数据!")
            raw_fields_data = [TableRawFieldSchema()]
        else:
            raw_fields_data = [
                TableRawFieldSchema(**ele)
                for ele in query_result.table_fields
                if isinstance(ele, dict)
            ]

        table_metadata.raw_fields_info = raw_fields_data

        state["table_metadata_array"].append(table_metadata)


mapping_builder = StateGraph(DataForgeState)
mapping_builder.add_node("create_table_raw_field_info", create_table_raw_field_info)
mapping_builder.add_edge(START, "create_table_raw_field_info")
mapping_builder.add_edge("create_table_raw_field_info", END)

memory = MemorySaver()
mapping_graph = mapping_builder.compile(checkpointer=memory)

if __name__ == "__main__":
    print(mapping_graph.get_graph(xray=True).draw_mermaid())
    # thread = {"configurable": {"thread_id": "4895b601-c056-4af3-a1f3-6dfa03837744"}}
    # event = mapping_graph.invoke(
    #     {
    #         "table_metadata_array": [],
    #         "user_input": "数据库表名称:\nADM_DOMAIN_WHOIS\nODS_TC_DOMAIN_WHOIS\n期望表约束条件:\nADM_DOMAIN_WHOIS: DOMAIN IS NOT NULL\nODS_TC_DOMAIN_WHOIS: DOMAIN IS NOT NULL\n期望生成数据条数:\nADM_DOMAIN_WHOIS: 10\nODS_TC_DOMAIN_WHOIS: 20",
    #         "user_intent": UserIntentSchema(
    #             table_en_names=["ADM_DOMAIN_WHOIS", "ODS_TC_DOMAIN_WHOIS"],
    #             table_conditions={
    #                 "ADM_DOMAIN_WHOIS": "DOMAIN IS NOT NULL",
    #                 "ODS_TC_DOMAIN_WHOIS": "DOMAIN IS NOT NULL",
    #             },
    #             table_data_count={
    #                 "ADM_DOMAIN_WHOIS": 2,
    #                 "ODS_TC_DOMAIN_WHOIS": 3,
    #             },
    #         ),
    #     },
    #     thread,
    #     stream_mode="values",
    # )
    # print(event)
