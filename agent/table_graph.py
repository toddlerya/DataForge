#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/6/16 16:40
# @Author   : guoqun X2590
# @FileName : table_graph.py
# @Project  : DataForge


import random
import re
from typing import List, Tuple

from loguru import logger
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import FunctionMessage
from langgraph.graph import END, START, StateGraph

from config import GEN_TABLE_MODELS_DATA_PATH, GEN_TABLE_MODELS_TEMP_PATH
from agent.llm import chat_llm
from agent.prompt import (
    table_intent_prompt,
    table_mapping_dimension_prompt,
    table_ename_translate_prompt,
    table_fields_fill_prompt,
)
from agent.state import (
    TableGenState,
    StructuredTranslateTableEnameSchema,
    StructuredDimensionMappingSchema,
    TableGenUserIntentSchema,
    GenSourceTableMetadataSchema,
    DimensionTableFieldsRecommendation,
    DimensionTableFillFieldResult,
)
from database_models.schema import GenTableFieldSchema
from cruds.advanced_query import sliding_window_query
from database_models.models import TableMetaDataInfo
from utils.db import Database
from utils.file import save_dict2jl, targz_archive, create_dir


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
    logger.debug(f"user_intent structured_output: {table_user_intent}")
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
        logger.debug(
            f"当前窗口: {window_index} 当前偏移量: {offset} 当前数据: {windows_data}"
        )
        pass

    logger.info(f"[+] 元数据表作为素材分组策略，当前策略为滑动窗口拼接数据")
    material_table_groups = sliding_window_query(
        db_handler=Database(),
        model_class=TableMetaDataInfo,
        fields=["table_en_name", "table_cn_name", "description", "table_fields"],
        # 滑动窗口参数增加随机性
        window_size=random.randint(10, 20),
        step_size=random.randint(5, 10),
        filters={"source": ["盘古", "数据域"]},
        # callback=print_cb
    )
    logger.debug(f"material_table_groups count: {len(material_table_groups)}")
    state["material_table_groups"] = material_table_groups
    return state


def material_tables_mapping_dimension_table(state: TableGenState):
    """
    素材表输入LLM映射出一组特征表
    Args:
        state:

    Returns:

    """

    def extract_reference_table_metadata_info(
        each_material_table_group: list[dict],
        recommend_reference_material_table_en_name_slice: list[str],
    ) -> Tuple[list[GenSourceTableMetadataSchema], list[str]]:
        """
        提取补全参照表字段信息备用
        Args:
            each_material_table_group:
            recommend_reference_material_table_en_name_slice:

        Returns:

        """
        logger.debug(
            f"each_material_table_group count: {len(each_material_table_group)}"
        )
        reference_table_metadata_slice: list[GenSourceTableMetadataSchema] = list()
        reference_table_en_name_slice: list[str] = list()
        for each_material_table in each_material_table_group:
            table_en_name = each_material_table.get("table_en_name", "")
            if (
                table_en_name.upper()
                in recommend_reference_material_table_en_name_slice
                or table_en_name.lower()
                in recommend_reference_material_table_en_name_slice
            ):
                raw_fields_info = each_material_table.get("table_fields", [])
                table_cn_name = each_material_table.get("table_cn_name", "")
                # 补充字段的来源表信息
                source_fields_info = []
                for ele in raw_fields_info:
                    ele.update(
                        {
                            "source_table_en_name": table_en_name,
                            "source_table_cn_name": table_cn_name,
                        }
                    )
                    source_fields_info.append(ele)
                reference_table_metadata = GenSourceTableMetadataSchema(
                    table_en_name=table_en_name,
                    table_cn_name=table_cn_name,
                    source_fields_info=source_fields_info,
                )
                reference_table_metadata_slice.append(reference_table_metadata)
                # LLM结构化输出时会把reference_material_table_en_name_slice改变大小写，导致后续数据库检索异常，这里需要处理下
                reference_table_en_name_slice.append(table_en_name)
        return reference_table_metadata_slice, reference_table_en_name_slice

    logger.info(f"[+] 素材表输入LLM映射出一组特征表节点")
    material_table_groups: list[list[dict]] = state.get("material_table_groups")
    # TODO: material_table_groups增加个洗牌策略，让每次生成的表更有随机性
    user_intent: TableGenUserIntentSchema = state["user_intent"]
    mapping_dimension_table_info_slice = list()
    recommend_dimension_table_en_name_slice = list()
    for each_group in material_table_groups[: int(user_intent.table_number)]:
        # 构建每一组素材的提示词
        material_table_infos = ""
        for index, material_table in enumerate(each_group):
            each_material_table_info = (
                f"表 {index}: \n"
                f"表英文名称: {material_table.get('table_en_name')}\n"
                f"表中文名称: {material_table.get('table_cn_name')}\n"
                f"表描述: {material_table.get('description')}\n\n"
            )
            material_table_infos += each_material_table_info
        chat_prompt = table_mapping_dimension_prompt.format_messages(
            user_intent_categories=user_intent.categories,
            material_table_infos=material_table_infos,
        )
        # 构建每一组的结构化信息
        structured_llm = chat_llm.with_structured_output(
            StructuredDimensionMappingSchema
        )
        logger.trace(
            f"material_tables_mapping_dimension_table chat_prompt: {chat_prompt}"
        )

        retry_count = 0
        # 设置最大重试次数
        max_retries = state["max_retries"]
        while True:
            if retry_count >= max_retries:
                break
            try:
                dimension_mapping_result: StructuredDimensionMappingSchema = (
                    structured_llm.invoke(chat_prompt)
                )
            except Exception as e:
                logger.error(f"material_tables_mapping_dimension_table error: {e}")
                retry_count += 1
            else:
                logger.trace(
                    f"输出 dimension_mapping_result: {dimension_mapping_result}"
                )
                if (
                    dimension_mapping_result.recommend_category
                    in user_intent.categories
                ):
                    # 如果推荐的类别在用户意图范围内采纳
                    logger.debug(
                        f"采纳 dimension_mapping_result: {dimension_mapping_result}"
                    )
                    # 如果生成的特征表名称没保存则保存下，否则跳过
                    if (
                        dimension_mapping_result.recommend_dimension_table_en_name
                        not in recommend_dimension_table_en_name_slice
                    ):
                        recommend_dimension_table_en_name_slice.append(
                            dimension_mapping_result.recommend_dimension_table_en_name
                        )
                        # 提取补全参照表字段信息备用，更新reference_material_table_metadata_slice信息
                        # LLM结构化输出时会把recommend_reference_material_table_en_name_slice改变大小写，导致后续数据库检索异常，这里需要处理下
                        (
                            dimension_mapping_result.reference_material_table_metadata_slice,
                            dimension_mapping_result.reference_material_table_en_name_slice,
                        ) = extract_reference_table_metadata_info(
                            each_group,
                            dimension_mapping_result.recommend_reference_material_table_en_name_slice,
                        )
                        mapping_dimension_table_info_slice.append(
                            dimension_mapping_result
                        )
                    else:
                        logger.warning(
                            f"推荐生成的特征表重复，丢弃-> "
                            f"result.recommend_dimension_table_en_name: {dimension_mapping_result.recommend_dimension_table_en_name} "
                            f"result.dimension_table_en_name: {dimension_mapping_result.dimension_table_en_name} "
                            f"recommend_dimension_table_en_name_slice: {recommend_dimension_table_en_name_slice}"
                        )
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
        for index, mapping_dimension_table_info in enumerate(
            mapping_dimension_table_info_slice
        ):
            stop_flag = True
            if (
                mapping_dimension_table_info.recommend_dimension_table_en_name
                in mapping_dimension_table_info.recommend_reference_material_table_en_name_slice
                or not re.match(
                    pattern=r"^[A-Z][A-Z_]+[A-Z]$",
                    string=mapping_dimension_table_info.dimension_table_en_name,
                )
            ):
                # 表的英文名在参照表清单中，或表的英文名称称为中文，需要根据表的中文名称翻译处理

                chat_prompt = table_ename_translate_prompt.format_messages(
                    table_name=mapping_dimension_table_info.dimension_table_cn_name
                )
                structured_llm = chat_llm.with_structured_output(
                    StructuredTranslateTableEnameSchema
                )
                retry_count = 0
                # 设置最大重试次数
                max_retries = state["max_retries"]
                while stop_flag:
                    if retry_count >= max_retries:
                        break
                    try:
                        translate_table_ename: StructuredTranslateTableEnameSchema = (
                            structured_llm.invoke(chat_prompt)
                        )
                    except Exception as e:
                        logger.error(f"translate_table_name error: {e}")
                        retry_count += 1
                    else:
                        logger.debug(
                            f"dimension_table_en_name: {mapping_dimension_table_info.dimension_table_en_name} "
                            f"dimension_table_cn_name: {mapping_dimension_table_info.dimension_table_cn_name} "
                            f"translated_table_ename: {translate_table_ename}"
                        )
                        mapping_dimension_table_info.dimension_table_en_name = (
                            translate_table_ename.table_ename
                        )
                        stop_flag = False
            # 给表名称加后缀
            mapping_dimension_table_info.dimension_table_en_name = (
                mapping_dimension_table_info.dimension_table_en_name + "_BYTS"
            )
            # 更新
            mapping_dimension_table_info_slice[index] = mapping_dimension_table_info
        state["mapping_dimension_table_info_slice"] = mapping_dimension_table_info_slice
    return state


def save_mapping_dimension_table_info(state: TableGenState):
    logger.info("[+] 存储mapping_dimension_table_info节点")
    mapping_dimension_table_info_slice = state.get("mapping_dimension_table_info_slice")
    if mapping_dimension_table_info_slice:
        # 创建state.get("session_temp_data_path")目录
        status, message = create_dir(
            dir_path=str(state.get("session_temp_data_path").absolute())
        )
        if status is False:
            state["create_session_temp_data_path_message"] = message
            return state
        for mapping_dimension_table_info in mapping_dimension_table_info_slice:
            data = mapping_dimension_table_info.model_dump()
            # 移除此字段信息，因为此输出过程不需要体现这个信息
            data.pop("reference_material_table_metadata_slice")
            save_json_path = (
                state.get("session_temp_data_path")
                .joinpath(
                    f"{mapping_dimension_table_info.dimension_table_en_name}-mapping_dimension_table_info.json"
                )
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

    def reformat_reference_material_table_fields(
        source_fields_info: List[GenTableFieldSchema],
    ):
        """
        提取精简表字段信息用作提示词
        Args:
            source_fields_info:

        Returns:

        """
        result = list()
        for field_metadata in source_fields_info:
            result.append(
                {"en_name": field_metadata.en_name, "cn_name": field_metadata.cn_name}
            )
        return result

    logger.info("[+] 回填字段生成特征表节点")
    user_intent = state.get("user_intent")
    mapping_dimension_table_info_slice = state.get("mapping_dimension_table_info_slice")
    dimension_table_config_slice = list()
    for mapping_dimension_table_info in mapping_dimension_table_info_slice:
        # 生成每个特征表的配置信息
        dimension_table_fields_recommendations = list()
        dimension_table_fields = list()
        for (
            each_reference_material_table
        ) in mapping_dimension_table_info.reference_material_table_metadata_slice:
            # 依次处理每个参照表，提取填充特征表字段
            reference_material_table_en_name_count = len(
                mapping_dimension_table_info.reference_material_table_en_name_slice
            )
            try:
                recommend_top_num = (
                    int(
                        user_intent.table_field_col_max
                        / reference_material_table_en_name_count
                    )
                    + 1
                )
            except Exception as err:
                logger.warning(f"计算推荐字段TopN参数错误: {err}, 给默认值50")
                recommend_top_num = 50
            chat_prompt = table_fields_fill_prompt.format_messages(
                category=mapping_dimension_table_info.recommend_category,
                table_cn_name=mapping_dimension_table_info.dimension_table_cn_name,
                table_fields_list=reformat_reference_material_table_fields(
                    each_reference_material_table.source_fields_info
                ),
                top_num=recommend_top_num,
            )
            logger.trace(
                f"gen_dimension_table_config call llm args: "
                f"recommend_category: {mapping_dimension_table_info.recommend_category} "
                f"dimension_table_en_name: {mapping_dimension_table_info.dimension_table_en_name} "
                f"dimension_table_cn_name: {mapping_dimension_table_info.dimension_table_cn_name} "
                f"top_num: {recommend_top_num} "
                f"each_reference_material_table: {each_reference_material_table.table_en_name}"
            )
            structured_llm = chat_llm.with_structured_output(
                DimensionTableFieldsRecommendation
            )
            retry_count = 0
            # 设置最大重试次数
            max_retries = state["max_retries"]
            stop_flag = True
            while stop_flag:
                if retry_count >= max_retries:
                    logger.error(
                        f"达到最大重试次数: {max_retries}! 退出处理dimension_table_fields_recommendation"
                    )
                    break
                try:
                    dimension_table_fields_recommendation: DimensionTableFieldsRecommendation = structured_llm.invoke(
                        chat_prompt
                    )
                except Exception as e:
                    logger.error(f"gen_dimension_table_config error: {e}")
                    retry_count += 1
                else:
                    # 补充素材表信息：
                    dimension_table_fields_recommendation.material_table_en_name = (
                        each_reference_material_table.table_en_name
                    )
                    dimension_table_fields_recommendation.material_table_cn_name = (
                        each_reference_material_table.table_cn_name
                    )
                    dimension_table_fields_recommendation.top_num = recommend_top_num
                    # 对dimension_table_fields_recommendation的field_en_name_slice去重，保证一张表的推荐字段没有重复
                    dimension_table_fields_recommendation.field_en_name_slice = list(
                        set(dimension_table_fields_recommendation.field_en_name_slice)
                    )
                    logger.trace(
                        f"gen_dimension_table_config dimension_table_fields_recommendation: "
                        f"{dimension_table_fields_recommendation}"
                    )
                    dimension_table_fields_recommendations.append(
                        dimension_table_fields_recommendation
                    )
                    # 根据推荐字段获取对应字段的元数据信息
                    dimension_table_field = [
                        ele
                        for ele in each_reference_material_table.source_fields_info
                        if ele.en_name
                        in dimension_table_fields_recommendation.field_en_name_slice
                    ]
                    dimension_table_fields.extend(dimension_table_field)
                    # 去重特征表推荐的字段元数据信息
                    seen_field_en_name = set()
                    unique_data_list = list()
                    for item in dimension_table_fields:
                        if item.en_name not in seen_field_en_name:
                            unique_data_list.append(item)
                            seen_field_en_name.add(item.en_name)
                    dimension_table_fields = unique_data_list
                    stop_flag = False
        # 每张特征表的结果
        dimension_table_fill_fields_result = DimensionTableFillFieldResult(
            recommend_category=mapping_dimension_table_info.recommend_category,
            dimension_table_en_name=mapping_dimension_table_info.dimension_table_en_name,
            dimension_table_cn_name=mapping_dimension_table_info.dimension_table_cn_name,
            dimension_table_fields_recommendations=dimension_table_fields_recommendations,
            dimension_table_fields=dimension_table_fields,
        )
        # logger.debug(f"dimension_table_fill_fields_result: {dimension_table_fill_fields_result}")
        dimension_table_config_slice.append(dimension_table_fill_fields_result)
    state["dimension_table_config_slice"] = dimension_table_config_slice
    return state


def save_dimension_table_config(state: TableGenState):
    logger.info("[+] 存储dimension_table_config节点")
    dimension_table_config_slice = state.get("dimension_table_config_slice")
    if dimension_table_config_slice:
        for dimension_table_fill_fields_result in dimension_table_config_slice:
            data = dimension_table_fill_fields_result.model_dump()
            save_json_path = (
                state.get("session_temp_data_path")
                .joinpath(
                    f"{dimension_table_fill_fields_result.dimension_table_en_name}-dimension_table_config.json"
                )
                .absolute()
            )
            save_dict2jl(json_data=data, save_path=str(save_json_path))
    return state


def archive_table_data(state: TableGenState):
    """
    打包任务生成的表配置数据
    :param state:
    :return:
    """
    logger.info(
        f"[+] 打包session_id={state.get('session_id')} client_ip={state.get('client_ip')}结果数据"
    )
    result_archive_file_name = f"""{state.get("client_ip")}_{state.get("session_id")}_llm_gen_table_config.tar.gz"""
    session_archive_file_path = GEN_TABLE_MODELS_DATA_PATH.joinpath(
        result_archive_file_name
    )
    status, message = targz_archive(
        dir_to_archive=GEN_TABLE_MODELS_TEMP_PATH.joinpath(state.get("session_id")),
        archive_filename_path=session_archive_file_path,
    )
    if status is False:
        state["archive_message"] = message
    else:
        state["session_archive_file_path"] = session_archive_file_path
    return state


table_gen_builder = StateGraph(TableGenState)
table_gen_builder.add_node("analyze_table_intent", analyze_table_intent)
table_gen_builder.add_node("table_intent_human_feedback", table_intent_human_feedback)
table_gen_builder.add_node(
    "material_table_group_strategy", material_table_group_sliding_window_strategy
)
table_gen_builder.add_node(
    "material_tables_mapping_dimension_table", material_tables_mapping_dimension_table
)
table_gen_builder.add_node("translate_table_name", translate_table_name)
table_gen_builder.add_node(
    "save_mapping_dimension_table_info", save_mapping_dimension_table_info
)
table_gen_builder.add_node("gen_dimension_table_config", gen_dimension_table_config)
table_gen_builder.add_node("save_dimension_table_config", save_dimension_table_config)
table_gen_builder.add_node("archive_table_data", archive_table_data)

table_gen_builder.add_edge(START, "analyze_table_intent")
table_gen_builder.add_edge("analyze_table_intent", "table_intent_human_feedback")
table_gen_builder.add_conditional_edges(
    "table_intent_human_feedback",
    should_table_intent_continue,
    ["analyze_table_intent", "material_table_group_strategy"],
)
table_gen_builder.add_edge(
    "material_table_group_strategy", "material_tables_mapping_dimension_table"
)
table_gen_builder.add_edge(
    "material_tables_mapping_dimension_table", "translate_table_name"
)
table_gen_builder.add_edge("translate_table_name", "save_mapping_dimension_table_info")
table_gen_builder.add_edge(
    "save_mapping_dimension_table_info", "gen_dimension_table_config"
)
table_gen_builder.add_edge("gen_dimension_table_config", "save_dimension_table_config")
table_gen_builder.add_edge("save_dimension_table_config", "archive_table_data")
table_gen_builder.add_edge("archive_table_data", END)

memory = MemorySaver()
table_gen_graph = table_gen_builder.compile(
    interrupt_before=["table_intent_human_feedback"], checkpointer=memory
)

if __name__ == "__main__":
    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH

    from utils.log import LogManager

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="DataForgeTableGenApp.log",
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))
    init_env()

    print(table_gen_graph.get_graph(xray=True).draw_mermaid())
    user_input = """帮我生成一些人员属性、上网行为、位置轨迹类别的表，每个表的字段数量最少10个，最多100个，至少生成2张表"""
    thread = {"configurable": {"thread_id": "123"}}
    init_state = {"user_input": user_input, "max_retries": 5}
    for event in table_gen_graph.stream(init_state, thread, stream_mode="values"):
        user_intent: TableGenUserIntentSchema = event.get("user_intent")
        if user_intent:
            logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")
    # 模拟用户意图识别的研判反馈
    table_gen_graph.update_state(
        thread, {"human_intent_feedback": "正确"}, as_node="table_intent_human_feedback"
    )

    for event in table_gen_graph.stream(None, thread, stream_mode="values"):
        # Review
        # human_intent_feedback = event.get("human_intent_feedback")
        # if human_intent_feedback:
        #     logger.info(f"human_intent_feedback: {human_intent_feedback}")

        # dimension_table_config_slice = event.get("dimension_table_config_slice")
        # if dimension_table_config_slice:
        #     logger.info(f"dimension_table_config_slice count: {len(dimension_table_config_slice)}")
        pass
