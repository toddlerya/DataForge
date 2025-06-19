#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/6/16 16:40 
# @Author   : guoqun X2590
# @FileName : table_graph.py
# @Project  : DataForge

import pathlib
import re
from typing import List

from loguru import logger
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from agent.llm import chat_llm
from agent.prompt import table_intent_prompt, table_mapping_dimension_prompt, table_ename_translate_prompt, \
    table_fields_fill_prompt
from agent.state import (TableGenState, StructuredTranslateTableEnameSchema, StructuredDimensionMappingSchema,
                         TableGenUserIntentSchema, TableMetadataSchema,
                         DimensionTableFieldsRecommendation, DimensionTableFillFieldResult)
from database_models.schema import TableRawFieldSchema
from cruds.advanced_query import sliding_window_query
from database_models.models import TableMetaDataInfo
from utils.db import Database
from utils.file import save_dict2jl


def analyze_table_intent(state: TableGenState) -> TableGenState:
    logger.info(f"[+] 用户意图分析节点")
    table_user_input = state.get("user_input").strip()
    table_human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {table_user_input} human_intent_feedback: {table_human_intent_feedback}"
    )
    structured_llm = chat_llm.with_structured_output(TableGenUserIntentSchema)
    chat_prompt = table_intent_prompt.format_messages(
        user_input=table_user_input, human_intent_feedback=table_human_intent_feedback
    )
    logger.trace(f"analyze_intent chat_prompt: {chat_prompt}")
    table_user_intent = structured_llm.invoke(chat_prompt)
    state["user_intent"] = table_user_intent
    logger.debug(f"user_intent: {table_user_intent}")
    return state


def table_intent_human_feedback():
    """No-op node that should be interrupted on"""
    pass


def should_table_intent_continue(state: TableGenState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确":
        return "material_table_group_strategy"

    # Otherwise proceed to create table info
    return "analyze_intent"


def material_table_group_sliding_window_strategy(state: TableGenState):
    """
    元数据表作为素材分组策略，当前策略为滑动窗口拼接数据
    Args:
        state:

    Returns:

    """

    def print_cb(windows_data, window_index, offset):
        logger.debug(f"当前窗口: {window_index} 当前偏移量: {offset} 当前数据: {windows_data}")
        pass

    logger.info(f"[+] 元数据表作为素材分组策略，当前策略为滑动窗口拼接数据")
    all_results = sliding_window_query(db_handler=Database(),
                                       model_class=TableMetaDataInfo,
                                       fields=["table_en_name", "table_cn_name", "description", "table_fields"],
                                       window_size=20,
                                       step_size=10
                                       # filters={"source": "盘古"},
                                       # callback=print_cb
                                       )
    state["material_table_groups"] = all_results
    return state


def material_tables_mapping_dimension_table(state: TableGenState):
    """
    素材表输入LLM映射出一组特征表
    Args:
        state:

    Returns:

    """

    def extract_reference_table_metadata_info(each_material_table_group: list[dict],
                                              reference_table_en_name_slice: list[str]):
        """
        提取补全参照表字段信息备用
        Args:
            each_material_table_group:
            reference_table_en_name_slice:

        Returns:

        """
        reference_table_metadata_slice: list[TableMetadataSchema] = list()
        for each_material_table in each_material_table_group:
            if each_material_table.get("table_en_name", "") in reference_table_en_name_slice:
                reference_table_metadata = TableMetadataSchema(
                    table_en_name=each_material_table.get("table_en_name", ""),
                    table_cn_name=each_material_table.get("table_cn_name", ""),
                    raw_fields_info=each_material_table.get("table_fields", []),
                )
                reference_table_metadata_slice.append(reference_table_metadata)
        return reference_table_metadata_slice

    logger.info(f"[+] 素材表输入LLM映射出一组特征表节点")
    material_table_groups: list[list[dict]] = state.get("material_table_groups")
    user_intent: TableGenUserIntentSchema = state["user_intent"]
    mapping_dimension_table_info_slice = list()
    recommend_dimension_table_en_name_slice = list()
    for each_group in material_table_groups[:5]:
        # 构建每一组素材的提示词
        material_table_infos = ""
        for index, material_table in enumerate(each_group):
            each_material_table_info = f"表 {index}: \n" \
                                       f"表英文名称: {material_table.get('table_en_name')}\n" \
                                       f"表中文名称: {material_table.get('table_cn_name')}\n" \
                                       f"表描述: {material_table.get('description')}\n\n"
            material_table_infos += each_material_table_info
        chat_prompt = table_mapping_dimension_prompt.format_messages(user_intent_categories=user_intent.categories,
                                                                     material_table_infos=material_table_infos)
        # 构建每一组的结构化信息
        structured_llm = chat_llm.with_structured_output(StructuredDimensionMappingSchema)
        logger.trace(f"material_tables_mapping_dimension_table chat_prompt: {chat_prompt}")

        retry_count = 0
        # 设置最大重试次数
        max_retries = state["max_retries"]
        while True:
            if retry_count >= max_retries:
                break
            try:
                dimension_mapping_result: StructuredDimensionMappingSchema = structured_llm.invoke(chat_prompt)
            except Exception as e:
                logger.error(f"material_tables_mapping_dimension_table error: {e}")
                retry_count += 1
            else:
                logger.debug(f"dimension_mapping_result: {dimension_mapping_result}")
                if dimension_mapping_result.recommend_category in user_intent.categories:
                    # 如果推荐的类别在用户意图范围内采纳
                    logger.info(dimension_mapping_result)
                    # 如果生成的特征表名称没保存则保存下，否则跳过
                    if dimension_mapping_result.dimension_table_en_name not in recommend_dimension_table_en_name_slice:
                        recommend_dimension_table_en_name_slice.append(dimension_mapping_result.dimension_table_en_name)
                        # 提取补全参照表字段信息备用，更新reference_material_table_fields_slice信息
                        dimension_mapping_result.reference_material_table_metadata_slice = extract_reference_table_metadata_info(
                            each_group, dimension_mapping_result.reference_material_table_en_name_slice)
                        mapping_dimension_table_info_slice.append(dimension_mapping_result)
                    else:
                        logger.warning(f"推荐生成的特征表重复，丢弃: {dimension_mapping_result}")
                break
    state["mapping_dimension_table_info_slice"] = mapping_dimension_table_info_slice
    return state


def translate_table_name(state: TableGenState):
    """
    将生成的table_ename为中文的情况翻译为英文
    Args:
        state:

    Returns:

    """
    logger.info(f"[+] 将生成的table_ename为中文的情况翻译为英文节点")
    mapping_dimension_table_info_slice = state.get("mapping_dimension_table_info_slice")
    if mapping_dimension_table_info_slice:
        for index, mapping_dimension_table_info in enumerate(mapping_dimension_table_info_slice):
            stop_flag = True
            if mapping_dimension_table_info.dimension_table_en_name in \
                    mapping_dimension_table_info.reference_material_table_en_name_slice \
                    or not re.match(pattern=r"^[A-Z][A-Z_]+[A-Z]$",
                                    string=mapping_dimension_table_info.dimension_table_en_name):
                # 表的英文名在参照表清单中，或表的英文名称称为中文，需要根据表的中文名称翻译处理
                chat_prompt = table_ename_translate_prompt.format_messages(
                    table_name=mapping_dimension_table_info.dimension_table_cn_name
                )
                structured_llm = chat_llm.with_structured_output(StructuredTranslateTableEnameSchema)
                retry_count = 0
                # 设置最大重试次数
                max_retries = state["max_retries"]
                while stop_flag:
                    if retry_count >= max_retries:
                        break
                    try:
                        translate_table_ename: StructuredTranslateTableEnameSchema = structured_llm.invoke(chat_prompt)
                    except Exception as e:
                        logger.error(f"translate_table_name error: {e}")
                        retry_count += 1
                    else:
                        logger.debug(f"dimension_table_en_name: {mapping_dimension_table_info.dimension_table_en_name} "
                                     f"dimension_table_cn_name: {mapping_dimension_table_info.dimension_table_cn_name} "
                                     f"translated_table_ename: {translate_table_ename}")
                        mapping_dimension_table_info.dimension_table_en_name = translate_table_ename.table_ename
                        stop_flag = False
            # 给表名称加后缀
            mapping_dimension_table_info.dimension_table_en_name = mapping_dimension_table_info.dimension_table_en_name + "_BYTS"
            # 更新
            mapping_dimension_table_info_slice[index] = mapping_dimension_table_info
        state["mapping_dimension_table_info_slice"] = mapping_dimension_table_info_slice
    return state


def save_mapping_dimension_table_info(state: TableGenState):
    logger.info("[+] 存储mapping_dimension_table_info节点")
    mapping_dimension_table_info_slice = state.get("mapping_dimension_table_info_slice")
    if mapping_dimension_table_info_slice:
        for mapping_dimension_table_info in mapping_dimension_table_info_slice:
            data = mapping_dimension_table_info.model_dump()
            save_json_path = (
                pathlib.Path(r"F:\GITLAB\DataForge\data\gen_models")
                .joinpath(f"{mapping_dimension_table_info.dimension_table_en_name}.json")
                .absolute()
            )
            save_dict2jl(json_data=data, save_path=str(save_json_path))
    return state


def gen_dimension_table_config(state: TableGenState):
    """
    回填字段生成特征表
    Args:
        state:

    Returns:

    """

    def reformat_reference_material_table_fields(raw_fields_info: List[TableRawFieldSchema]):
        """
        提取精简表字段信息用作提示词
        Args:
            table_metadata_slice:

        Returns:

        """
        result = list()
        for field_metadata in raw_fields_info:
            result.append(
                {
                    "en_name": field_metadata.en_name,
                    "cn_name": field_metadata.cn_name
                }
            )
        return result

    logger.info("[+] 回填字段生成特征表节点")
    mapping_dimension_table_info_slice = state.get("mapping_dimension_table_info_slice")
    dimension_table_config_slice = list()
    for mapping_dimension_table_info in mapping_dimension_table_info_slice:
        # 依次处理每个参照表，提取填充特征表字段
        for each_reference_material_table in mapping_dimension_table_info.reference_material_table_metadata_slice:
            chat_prompt = table_fields_fill_prompt.format_messages(
                category=mapping_dimension_table_info.recommend_category,
                table_cn_name=mapping_dimension_table_info.dimension_table_cn_name,
                table_fields_list=reformat_reference_material_table_fields(
                    each_reference_material_table.raw_fields_info)
            )
            structured_llm = chat_llm.with_structured_output(DimensionTableFieldsRecommendation)
            # TODO
            retry_count = 0
            # 设置最大重试次数
            max_retries = state["max_retries"]
            stop_flag = True
            while stop_flag:
                if retry_count >= max_retries:
                    break
                try:
                    dimension_mapping_result: StructuredDimensionMappingSchema = structured_llm.invoke(chat_prompt)
                except Exception as e:
                    logger.error(f"material_tables_mapping_dimension_table error: {e}")
                    retry_count += 1
                else:
                    logger.debug(f"dimension_mapping_result: {dimension_mapping_result}")
                    if dimension_mapping_result.recommend_category in user_intent.categories:
                        # 如果推荐的类别在用户意图范围内采纳
                        logger.info(dimension_mapping_result)
                    stop_flag = False
        dimension_table_fill_fields_result = DimensionTableFillFieldResult(
            recommend_category=mapping_dimension_table_info.recommend_category,
            dimension_table_en_name=mapping_dimension_table_info.dimension_table_en_name,
            dimension_table_cn_name=mapping_dimension_table_info.dimension_table_cn_name,
            dimension_table_fields_recommendations=[],
            dimension_table_fields=[]
        )
        dimension_table_config_slice.append(dimension_table_fill_fields_result)
    state["dimension_table_config_slice"] = dimension_table_config_slice
    return state


table_gen_builder = StateGraph(TableGenState)
table_gen_builder.add_node("analyze_table_intent", analyze_table_intent)
table_gen_builder.add_node("table_intent_human_feedback", table_intent_human_feedback)
table_gen_builder.add_node("material_table_group_strategy", material_table_group_sliding_window_strategy)
table_gen_builder.add_node("material_tables_mapping_dimension_table", material_tables_mapping_dimension_table)
table_gen_builder.add_node("translate_table_name", translate_table_name)
table_gen_builder.add_node("save_mapping_dimension_table_info", save_mapping_dimension_table_info)

table_gen_builder.add_edge(START, "analyze_table_intent")
table_gen_builder.add_edge("analyze_table_intent", "table_intent_human_feedback")
table_gen_builder.add_conditional_edges(
    "table_intent_human_feedback",
    should_table_intent_continue,
    ["analyze_table_intent", "material_table_group_strategy"],
)
table_gen_builder.add_edge("material_table_group_strategy", "material_tables_mapping_dimension_table")
table_gen_builder.add_edge("material_tables_mapping_dimension_table", "translate_table_name")
table_gen_builder.add_edge("translate_table_name", "save_mapping_dimension_table_info")
table_gen_builder.add_edge("save_mapping_dimension_table_info", END)

memory = MemorySaver()
table_gen_graph = table_gen_builder.compile(
    interrupt_before=["table_intent_human_feedback"], checkpointer=memory
)

if __name__ == "__main__":
    print(table_gen_graph.get_graph(xray=True).draw_mermaid())
    user_input = """帮我生成一些人员属性、上网行为、位置轨迹类别的表，每个类别的表最少2张，最多10张，每个表的字段数量最少10个，最多100个"""
    thread = {"configurable": {"thread_id": "123"}}
    init_state = {
        "user_input": user_input,
        "max_retries": 5
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
