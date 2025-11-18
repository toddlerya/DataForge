#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/11 15:53
# @Author   : guoqun X2590
# @FileName : dg_rule_processor.py
# @Project  : DataForge

from typing import Optional, Union

from agent.dg_configs import DG_STORAGE_PATH
from agent.dg_rule_extend import extract_field_type_and_size, force_update_dg_rule
from agent.llm import chat_llm
from agent.prompt import dg_category_prompt
from agent.state import (
    DataGenUserIntentSchema,
    MetaModeDataGenState,
    PydanticDataGeniusCategoryRecommendation,
    PydanticDataGeniusPlan,
    PydanticDataGeniusRule,
    SQLModeDataGenState,
    TableMetadataSchema,
    TableRawFieldSchema,
    TaskDataSchema,
)
from config import DG_PLAN_CONFIG_PREFIX
from cruds.dg_rule_cache import query_field_dg_rule, save_field_dg_rule
from database_models.schema import RecommendPanGuDictSchema
from utils.db_manager import DatabaseManager
from utils.file import get_md5
from utils.log import logger


def cache_dg_rule(
    db_manager: DatabaseManager,
    field_info: TableRawFieldSchema,
    scope: str,
    pydantic_data_genius_rule: PydanticDataGeniusRule,
    ttl: int = 86400 * 7,
):
    """
    缓存DG规则到数据库
    Args:
        db_manager:
        field_info:
        scope:
        pydantic_data_genius_rule:
        ttl:
    Returns:

    """
    _, rule_uuid = get_md5(
        f"{field_info.en_name}{field_info.cn_name}{field_info.desc}{field_info.field_type}"
    )
    logger.trace(
        f"存储DG规则到缓存, rule_uuid: {rule_uuid} "
        f"pydantic_data_genius_rule: {pydantic_data_genius_rule.model_dump_json()}"
    )
    field_dg_rule_cache_data = {
        "uuid": rule_uuid,
        "scope": scope,
        "ename": field_info.en_name,
        "cname": field_info.cn_name,
        "description": field_info.desc,
        "field_type_name": field_info.field_type,
        "dg_rule": pydantic_data_genius_rule.model_dump(),
        "example_data": field_info.example,
        "ttl": ttl,
    }
    save_status, save_message = save_field_dg_rule(
        db_manager=db_manager,
        field_dg_rule_cache_data=field_dg_rule_cache_data,
    )
    if save_status is False:
        logger.error(
            f"存储DG字段规则缓存异常! "
            f"field_dg_rule_cache_data: {field_dg_rule_cache_data} "
            f"ERROR: {save_message}"
        )


def recommend_dg_rule_by_llm(
    structured_llm,
    col_index: int,
    field_info: TableRawFieldSchema,
    DG_FIELD_CATEGORY_CONFIG: list[dict],
    table_dictkey_map: dict[str, list[RecommendPanGuDictSchema]],
    last_error_message: str,
) -> tuple[bool, str, Optional[PydanticDataGeniusRule]]:
    chat_prompt = dg_category_prompt.format_messages(
        cn_name=field_info.cn_name,
        en_name=field_info.en_name,
        field_type=field_info.field_type,
        desc=field_info.desc,
        sample_value=field_info.example,
        dict_name=field_info.dict_name,
        dg_category_config_data=DG_FIELD_CATEGORY_CONFIG,
        last_error_message=last_error_message,
    )
    logger.trace(f"recommend_dg_rule_by_llm chat_prompt: {chat_prompt}")
    try:
        llm_dg_field_category_recommendation = structured_llm.invoke(chat_prompt)
        logger.trace(
            f"llm_dg_field_category_recommendation.model_dump_json(): "
            f"{llm_dg_field_category_recommendation.model_dump_json()}"
        )
    except Exception as e:
        logger.error(f"llm_dg_field_category_recommendation error: {e}")
        last_error_message = str(e)
        return False, last_error_message, None
    else:
        # 构建该字段的DataGenius规则参数
        # 处理字典规则
        args: dict[str, str | list] = {}
        name = ""
        fix_rule_note = ""
        category = llm_dg_field_category_recommendation.category
        if category in table_dictkey_map:
            dict_items: list[RecommendPanGuDictSchema] | None = table_dictkey_map.get(
                category
            )

            if dict_items:
                if len(dict_items) > 100:
                    # 只取100个枚举值，因为DG的接口设计不支持太大的请求信息，会报413错误
                    dict_items = dict_items[:100]
                choices = [item.dict_id for item in dict_items]
                args = {"choices": choices}
                name = f"{category}_字典规则"
                category = "自定义-枚举"
                logger.debug(
                    f"类别={llm_dg_field_category_recommendation.category} "
                    f"更新为字典规则: {name}"
                )
            else:
                logger.error(
                    f"category: {category}的dict_items={dict_items} 无法生成字典规则"
                )
        if category in ("数字串", "随机串"):
            # 如果是默认字符串、随机串规则需要根据数据的字段的数据类型进行长度处理
            # `CHAR`类型是固定长度的
            # `VARCHAR2`是可变长度的，比如`VARCHAR2(3)`的长度是`[0,3]`
            # 生成的dg规则应该如下：
            """
            {
                "category": "自定义-字符串",
                "ename": "DST_PORT",
                "name": "CHAR(2)",
                "args": {
                    "chars_in": (
                            "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"
                            "OPQRSTUVWXYZ~!@#$%^&*()_+-=]}[{;:,.<>?|"
                        ),
                    "max_": "2",
                    "min_": "2"
                },
                "value": "【SCORE】: 0, 【THINK】: 字段名为'DST_PORT'，类型为'int',
                表示目标端口, 通常为0-65535之间的整数。虽然其数据形式为数字,
                但'端口'属于网络通信中的技术术语，不在预定义的<configs>类别中。
                由于没有匹配的类别, 且无法匹配到任何预定义类别, 因此置信度为0,
                推荐为'数字串'作为默认处理。",
                "cname": "宿端口",
                "preview": "-)",
                "col": 20
            }
            """
            field_type_str = field_info.field_type.upper()
            type_category, size = extract_field_type_and_size(field_type=field_type_str)
            if type_category and size:
                name = field_type_str
                if "CHAR" in type_category:
                    # 处理
                    category = "自定义-字符串"
                    if type_category == "CHAR":
                        args = {
                            "chars_in": "0123456789abcABC",
                            "max_": str(size),
                            "min_": str(size),
                        }
                    elif type_category == "VARCHAR2":
                        args = {
                            "chars_in": (
                                "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMN"
                                "OPQRSTUVWXYZ~!@#$%^&*()_+-=]}[{;:,.<>?|"
                            ),
                            "max_": str(size),
                            "min_": "1",
                        }
                elif "NUM" in type_category:
                    category = "自定义-数字"
                    if type_category == "NUMBER":
                        args = {"max_": "9" * size, "min_": "1"}
                logger.debug(
                    f"类别={llm_dg_field_category_recommendation.category} "
                    f"更新为{category}规则: {name}"
                )
                fix_rule_note = f"【FIX】强制更新为<<{category}>>规则: {name}"
        pydantic_data_genius_rule = PydanticDataGeniusRule(
            col=col_index,
            category=category,
            name=name,
            ename=field_info.en_name,
            cname=field_info.cn_name,
            preview="",
            value=(
                f"【SCORE】: {llm_dg_field_category_recommendation.score}, "
                f"【THINK】: {llm_dg_field_category_recommendation.reason}"
                f"{fix_rule_note}"
            ),
            args=args,
        )
        logger.trace(
            f"pydantic_data_genius_rule: {pydantic_data_genius_rule.model_dump_json()}"
        )
        return True, "", pydantic_data_genius_rule


def dg_rule_processor(  # noqa: C901
    state: Union[SQLModeDataGenState, MetaModeDataGenState],
) -> Union[SQLModeDataGenState, MetaModeDataGenState]:
    """
    DataGenius字段分类缓存和推荐处理器
    Args:
        state:

    Returns:

    """
    logger.info("DataGenius字段规则处理")
    # 复用的字段
    logger.trace(f"state: {state}")

    user_intent = state.get("user_intent")
    client_ip = state["client_ip"]
    session_id = state["session_id"]
    DG_FIELD_CATEGORY_CONFIG = state.get("DG_FIELD_CATEGORY_CONFIG")
    logger.trace(
        "DG_FIELD_CATEGORY_CONFIG category slice: "
        f"{[item.get('category') for item in DG_FIELD_CATEGORY_CONFIG]}"
    )
    table_dictkey_map = state.get("table_dictkey_map")

    if isinstance(user_intent, DataGenUserIntentSchema):
        table_en_name = user_intent.table_en_name
        table_metadata: TableMetadataSchema = state["table_metadata_info"]
    else:
        table_metadata = state.get("table_metadata_info")
        table_en_name = table_metadata.table_en_name
    row_count = user_intent.data_count or 1000
    if not table_metadata:
        logger.error("未查询到表元数据，无法进行数据字段分类推荐")
        state["error_messages"].append("未查询到表元数据，无法进行数据字段分类推荐")
        return state
    logger.trace(f"table_metadata: {table_metadata.model_dump_json()}")

    structured_llm = chat_llm.with_structured_output(
        PydanticDataGeniusCategoryRecommendation
    )

    # 如果类别推荐错误，记录错误信息，补充到提示词不要再次生成错误的类别推荐，重试N次
    last_error_message = ""
    field_index = 0
    # 设置最大重试次数
    max_retries = state["max_retries"]
    stop_flag = False
    rules: list[PydanticDataGeniusRule] = []

    db_manager = DatabaseManager()

    while True:
        col_index = field_index + 1
        if field_index >= len(table_metadata.raw_fields_info):
            stop_flag = True
        if stop_flag:
            logger.info("所有字段已处理完毕，结束DataGenius分类推荐")
            break
        field_info = table_metadata.raw_fields_info[field_index]
        table_metadata_source = table_metadata.source
        # 优先查询缓存的DG规则
        query_status, query_message, query_result = query_field_dg_rule(
            db_manager=db_manager,
            ename=field_info.en_name,
            cname=field_info.cn_name,
            field_type_name=field_info.field_type,
        )
        # 命中缓存，直接使用缓存的DG规则
        if query_status and query_result:
            logger.info(
                f"字段 {field_info.en_name} 命中DG规则缓存 "
                f"cache_result: {query_result.to_dict()}"
            )
            dg_rule_dict = query_result.dg_rule
            cached_dg_rule = PydanticDataGeniusRule(
                col=dg_rule_dict.get("col", 1),
                category=dg_rule_dict.get("category", "unknown"),
                name=dg_rule_dict.get("name", ""),
                ename=dg_rule_dict.get("ename", field_info.en_name),
                cname=dg_rule_dict.get("cname", field_info.cn_name),
                preview=dg_rule_dict.get("preview", ""),
                value=dg_rule_dict.get("value", ""),
                args=dg_rule_dict.get("args", {}),
            )
            # 更新字段的DG规则配置
            cached_dg_rule.col = col_index
            rules.append(cached_dg_rule)
            # 字段序号+1
            field_index += 1
            continue

        if query_status is False:
            logger.error(f"查询DG规则缓存异常: {query_message}")

        # 无法命中缓存则继续LLM推荐，有重试机制
        logger.info(f"字段{field_info.en_name}未命中缓存，触发LLM推荐")
        for retry_count in range(max_retries + 1):
            recommend_status, last_error_message, pydantic_data_genius_rule = (
                recommend_dg_rule_by_llm(
                    structured_llm=structured_llm,
                    col_index=col_index,
                    field_info=field_info,
                    DG_FIELD_CATEGORY_CONFIG=DG_FIELD_CATEGORY_CONFIG,
                    table_dictkey_map=table_dictkey_map,
                    last_error_message=last_error_message,
                )
            )
            # 推荐异常，重试
            if recommend_status is False or pydantic_data_genius_rule is None:
                logger.warning(
                    f"推荐异常, 重试第{retry_count}次... "
                    f"field_info: {field_info.model_dump_json()}"
                )
                # LLM推荐重试达到最大次数，给默认DG规则
                if retry_count >= max_retries:
                    llm_dg_field_category_recommendation = (
                        PydanticDataGeniusCategoryRecommendation(
                            category="数字串",
                            score=0,
                            reason="未能识别字段类型, 填充数字串分类",
                        )
                    )
                    logger.warning(
                        f"已达到最大推荐重试次数 {max_retries}, "
                        "自动填充默认DataGenius分类推荐"
                    )
                    logger.trace(
                        f"llm_dg_field_category_recommendation: "
                        f"{llm_dg_field_category_recommendation.model_dump_json()}"
                    )
                    # 构建该字段的DataGenius规则参数
                    pydantic_data_genius_rule = PydanticDataGeniusRule(
                        col=col_index,
                        category=llm_dg_field_category_recommendation.category,
                        name="",
                        ename=field_info.en_name,
                        cname=field_info.cn_name,
                        preview=f"{llm_dg_field_category_recommendation.model_dump_json()}",
                        value=field_info.example,
                    )
                    rules.append(pydantic_data_genius_rule)
                    field_index += 1
                    # 清空错误信息
                    last_error_message = ""
                    # 存储当前推荐的字段DG规则到缓存中
                    cache_dg_rule(
                        db_manager=db_manager,
                        field_info=field_info,
                        scope=table_metadata_source,
                        pydantic_data_genius_rule=pydantic_data_genius_rule,
                        ttl=86400 * 3,
                    )
                    break
            else:
                rules.append(pydantic_data_genius_rule)
                field_index += 1
                # 存储当前推荐的字段DG规则到缓存中
                cache_dg_rule(
                    db_manager=db_manager,
                    field_info=field_info,
                    scope=table_metadata_source,
                    pydantic_data_genius_rule=pydantic_data_genius_rule,
                )
                break
    rule_uuid = session_id
    # 检查特例规则进行更新
    rules = [force_update_dg_rule(rule) for rule in rules]
    pydantic_data_genius_plan = PydanticDataGeniusPlan(
        rule_name=f"{DG_PLAN_CONFIG_PREFIX}{rule_uuid}",
        type_="规则",
        rows=row_count,
        separator="\t",
        rules=rules,
        output=f"{DG_STORAGE_PATH}/output/{client_ip}/{rule_uuid}",
        model=f"{DG_STORAGE_PATH}/models/{client_ip}/{table_en_name}",
        cols=len(table_metadata.raw_fields_info),
    )
    state["pydantic_data_genius_plan"] = pydantic_data_genius_plan
    task_data = TaskDataSchema(
        task_uuid=session_id,
        table_en_name=table_en_name,
        data_row_count=pydantic_data_genius_plan.rows,
        user_intent=state["user_intent"].model_dump(),
        client_ip=client_ip,
        rule_name=pydantic_data_genius_plan.rule_name,
        task_rule=pydantic_data_genius_plan.model_dump().get("rules", []),
        env_name=state.get("env_name", ""),
    )
    state["task_data"] = task_data
    db_manager.close()
    return state


if __name__ == "__main__":
    category = "关联方向类型"
    dict_items: list[RecommendPanGuDictSchema] | None = [
        RecommendPanGuDictSchema(
            uuid=101711,
            dictkey_with_nlevel="FHWACODE_0021:2",
            dict_category_code="FHWACODE_0021",
            dict_category="关联方向类型",
            dict_level=2,
            dict_id="1",
            dict_name="客户端IP为源IP",
            env_name=None,
        ),
        RecommendPanGuDictSchema(
            uuid=101713,
            dictkey_with_nlevel="FHWACODE_0021:2",
            dict_category_code="FHWACODE_0021",
            dict_category="关联方向类型",
            dict_level=2,
            dict_id="3",
            dict_name="无法判断客户端IP",
            env_name=None,
        ),
        RecommendPanGuDictSchema(
            uuid=101712,
            dictkey_with_nlevel="FHWACODE_0021:2",
            dict_category_code="FHWACODE_0021",
            dict_category="关联方向类型",
            dict_level=2,
            dict_id="2",
            dict_name="客户端IP为宿IP",
            env_name=None,
        ),
    ]
    # 只取100个枚举值，因为DG的接口设计不支持太大的请求信息，会报413错误

    if dict_items:
        if len(dict_items) > 100:
            # 只取100个枚举值，因为DG的接口设计不支持太大的请求信息，会报413错误
            dict_items = dict_items[:100]
        choices = [item.dict_id for item in dict_items]
        args = {"choices": choices}
        name = f"{category}_字典规则"
        category = "自定义-枚举"
        logger.debug(f"类别={category} 更新为字典规则: {name}")
    else:
        logger.error(f"category: {category}的dict_items={dict_items} 无法生成字典规则")
