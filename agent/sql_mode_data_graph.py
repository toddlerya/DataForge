#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/9 16:54
# @Author   : guoqun X2590
# @FileName : sql_mode_data_graph.py
# @Project  : DataForge


import json
import time
import uuid
from urllib.parse import urljoin
from copy import deepcopy

import httpx
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from config import DG_PLAN_PATH, DG_PAYLOAD_PATH
from database_models.schema import RecommendPanGuDictSchema
from agent.llm import chat_llm
from agent.dg_rule_extend import force_update_dg_rule
from agent.prompt import dg_category_prompt, sql_mode_data_intent_prompt
from agent.dg_configs import DG_FIELD_CATEGORY_CONFIG as BASE_DG_FIELD_CATEGORY_CONFIG
from agent.state import (
    PydanticDataGeniusCategoryRecommendation,
    PydanticDataGeniusPlan,
    PydanticDataGeniusRule,
    DataGenSQLModeUserIntentSchema,
    SQLModeDataGenState,
    SQLModeTableInfoSchema,
    TableMetadataSchema,
    TableRawFieldSchema,
    init_dg_category_config
)
from agent.sql_parser import parse_simple_select
from agent.dg_rule_processor import dg_rule_processor
from agent.dg_configs import (
    DG_STORAGE_PATH,
    DG_SERVER_BASE_URL,
    DG_TASK_ADD_URL,
    DG_TASK_HISTORY,
    DG_NEW_TASK,
)
from config import SQL_MODE_DG_PLAN_CONFIG_PREFIX, PROJECT_PATH
from cruds.pangu import query_field_recommend_info_by_ename, query_dict_items_info_by_dictkey
from utils.db import Database
from utils.file import save_dict2jl


def detect_input_type(state: SQLModeDataGenState):
    """
    判断用户输入的是结构化任务参数还是自然语言任务需求
    :param state:
    :return:
    """
    user_intent: DataGenSQLModeUserIntentSchema = state.get("user_intent")
    if user_intent:
        return "sql_parse_to_table_info"
    else:
        return "analyze_intent"


def analyze_data_intent(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    解析用户意图，SQL模式
    :param state:
    :return:
    """
    user_input = state.get("user_input").strip()
    human_intent_feedback = state.get("human_intent_feedback", "")
    logger.debug(
        f"analyze_data_intent => user_input: {user_input} human_intent_feedback: {human_intent_feedback}"
    )
    structured_llm = chat_llm.with_structured_output(DataGenSQLModeUserIntentSchema)
    chat_prompt = sql_mode_data_intent_prompt.format_messages(
        user_input=user_input, human_intent_feedback=human_intent_feedback
    )
    logger.trace(f"analyze_intent chat_prompt: {chat_prompt}")
    user_intent = structured_llm.invoke(chat_prompt)
    state["user_intent"] = user_intent
    logger.debug(f"user_intent: {user_intent}")
    return state


def data_intent_human_feedback_node():
    """No-op node that should be interrupted on"""
    pass


def should_data_intent_continue(state: SQLModeDataGenState):
    """Return the next node to execute"""

    # Check if human feedback
    human_intent_feedback = state.get("human_intent_feedback", "").strip()
    if human_intent_feedback == "正确":
        return "sql_parse_to_table_info"

    # Otherwise proceed to create table info
    return "analyze_intent"


def sql_parse_to_table_info(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    解析SQL为表结构JSON
    :param state:
    :return:
    """
    logger.info("[+] 解析SQL为表结构JSON")
    user_intent = state.get("user_intent")
    user_sql = user_intent.sql
    logger.info(f"用户提供的SQL: {user_sql}")
    status, error, result = parse_simple_select(user_sql)
    if status is False or not result:
        table_info_error = f"解析SQL异常! error={error} result={result}"
        logger.error(table_info_error)
        state["table_info_error"] = table_info_error
        return state
    try:
        logger.debug(f"sql parse result: {result}")
        table_info = SQLModeTableInfoSchema(
            table_en_name=list(result.keys())[0],
            fields_info=result[(list(result.keys())[0])],
        )
        logger.debug(f"table_info: {table_info.model_dump_json()}")
        state["table_info_data"] = table_info
    except Exception as err:
        table_info_error = f"SQL生成表结构化信息异常: {err}"
        logger.error(table_info_error)
        state["table_info_error"] = table_info_error
        return state
    return state


def rag_sql_table_filed_info(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    根据字段知识库增强字段信息
    :param state:
    :return:
    """
    logger.info("RAG增强字段属性信息")
    table_info_data: SQLModeTableInfoSchema = state["table_info_data"]
    DG_FIELD_CATEGORY_CONFIG = deepcopy(BASE_DG_FIELD_CATEGORY_CONFIG)
    table_metadata_info = TableMetadataSchema(table_en_name=table_info_data.table_en_name)
    table_metadata_error: list[str] = list()
    table_dict_category_code_map: dict[str, str] = dict()
    table_dictkey_map: dict[str, list[RecommendPanGuDictSchema]] = dict()
    db_handler = Database()
    for each_field in table_info_data.fields_info:
        status, message, recommend_data = query_field_recommend_info_by_ename(db_handler=db_handler,
                                                                              field_en_name=each_field.en_name)
        if status is False:
            err_message = f"RAG增强字段属性异常: table_en_name={table_info_data.table_en_name} " \
                          f"field_en_name={each_field.en_name} ERROR: {message}"
            logger.error(err_message)
            table_metadata_error.append(err_message)
        if recommend_data is None:
            raw_field_data = TableRawFieldSchema(en_name=each_field.en_name)
            table_metadata_info.raw_fields_info.append(raw_field_data)
        else:
            raw_field_data = TableRawFieldSchema(
                en_name=each_field.en_name,
                cn_name=recommend_data.cname,
                desc=[recommend_data.description if recommend_data.description else ""][0],
                field_type=recommend_data.field_type_name,
                is_require=recommend_data.is_required,
                dict_key=[recommend_data.dictkey if recommend_data.dictkey else ""][0],
            )
            if recommend_data.dictkey:
                dict_status, dict_message, dict_result = query_dict_items_info_by_dictkey(
                    db_handler=db_handler,
                    dictkey_with_nlevel=recommend_data.dictkey)
                if dict_status is False:
                    logger.error(f"获取盘古字典异常: {dict_message}")
                elif dict_result:
                    one_dict = dict_result[0]
                    category = one_dict.dict_category
                    if category not in table_dict_category_code_map:
                        table_dict_category_code_map[category] = one_dict.dictkey_with_nlevel
                        value = one_dict.model_dump()
                        value.pop("uuid")
                        value.pop("dictkey_with_nlevel")
                        value.pop("dict_category_code")
                        value.pop("dict_category")
                        logger.info(f"将盘古字典添加到DG规则配置中: {category}")
                        config_value = {"category": category, "value": json.dumps(value, ensure_ascii=False)}
                        DG_FIELD_CATEGORY_CONFIG.append(config_value)
                        table_dictkey_map[category] = dict_result
                        raw_field_data.dict_name = category
            table_metadata_info.raw_fields_info.append(raw_field_data)
    state["table_metadata_info"] = table_metadata_info
    state["table_metadata_error"] = table_metadata_error
    state["table_dict_category_code_map"] = table_dict_category_code_map
    state["table_dictkey_map"] = table_dictkey_map
    state["DG_FIELD_CATEGORY_CONFIG"] = DG_FIELD_CATEGORY_CONFIG
    # 动态更新配置
    init_dg_category_config.DG_FIELD_CATEGORY_CONFIG = DG_FIELD_CATEGORY_CONFIG
    # 如果已经生成过实例了，需要清空缓存更新
    PydanticDataGeniusCategoryRecommendation.reset_allowed_categories()
    return state


#
# def add_pg_dict2dg_category(state: SQLModeDataGenState) -> SQLModeDataGenState:
#     """
#     将盘古字典加入到dg规则类别中
#     :param state:
#     :return:
#     """
#     logger.info("[+] 将盘古字典加入到dg规则类别中")
#     table_dictkey_with_nlevel_slice: list[str] = state.get("table_dictkey_with_nlevel_slice", [])
#     table_dictkey_map: dict[str, list[RecommendPanGuDictSchema]] = dict()
#     DG_FIELD_CATEGORY_CONFIG = state.get("DG_FIELD_CATEGORY_CONFIG")
#     for each_dictkey_with_nlevel in table_dictkey_with_nlevel_slice:
#         dict_status, dict_message, dict_result = query_dict_items_info_by_dictkey(db_handler=Database(),
#                                                                                   dictkey_with_nlevel=each_dictkey_with_nlevel)
#         if dict_status is False:
#             logger.error(f"获取盘古字典异常: {dict_message}")
#             continue
#         else:
#             if dict_result:
#                 one_dict = dict_result[0]
#                 category = one_dict.dict_category
#                 value = one_dict.model_dump()
#                 value.pop("uuid")
#                 value.pop("dictkey_with_nlevel")
#                 value.pop("dict_category_code")
#                 value.pop("dict_category")
#                 logger.info(f"将盘古字典添加到DG规则配置中: {category}")
#                 config_value = {"category": category, "value": json.dumps(value, ensure_ascii=False)}
#                 DG_FIELD_CATEGORY_CONFIG.append(config_value)
#                 table_dictkey_map[category] = dict_result
#     state["table_dictkey_map"] = table_dictkey_map
#     state["DG_FIELD_CATEGORY_CONFIG"] = DG_FIELD_CATEGORY_CONFIG
#     return state


def dg_category_recommend(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    DataGenius字段分类推荐节点
    Args:
        state:

    Returns:

    """
    logger.info("DataGenius字段分类推荐")
    table_metadata_info = state["table_metadata_info"]
    user_intent = state["user_intent"]
    client_ip = state["client_ip"]
    DG_FIELD_CATEGORY_CONFIG = state.get("DG_FIELD_CATEGORY_CONFIG")
    table_dictkey_map = state.get("table_dictkey_map")
    state["data_genius_headers"] = {"USER_PROVIDE_IP": client_ip}
    table_en_name = table_metadata_info.table_en_name
    row_count = user_intent.data_count
    structured_llm = chat_llm.with_structured_output(
        PydanticDataGeniusCategoryRecommendation
    )

    # 如果类别推荐错误，记录错误信息，补充到提示词不要再次生成错误的类别推荐，重试N次
    last_error_message = ""
    field_index = 0
    retry_count = 0
    # 设置最大重试次数
    max_retries = state["max_retries"]
    stop_flag = False
    rules: list[PydanticDataGeniusRule] = []
    while True:
        if field_index >= len(table_metadata_info.raw_fields_info):
            stop_flag = True
        if stop_flag:
            logger.info("所有字段已处理完毕，结束DataGenius分类推荐")
            break
        field_info = table_metadata_info.raw_fields_info[field_index]
        if retry_count >= max_retries:
            llm_dg_field_category_recommendation = (
                PydanticDataGeniusCategoryRecommendation(
                    category="数字串",
                    score=0,
                    reason="未能识别字段类型, 填充数字串分类",
                )
            )
            logger.warning(
                f"已达到最大推荐重试次数 {max_retries}，自动填充默认DataGenius分类推荐"
            )
            logger.trace(
                f"llm_dg_field_category_recommendation: {llm_dg_field_category_recommendation.model_dump_json()}"
            )
            # 构建该字段的DataGenius规则参数
            pydantic_data_genius_rule = PydanticDataGeniusRule(
                col=field_index + 1,
                category=llm_dg_field_category_recommendation.category,
                name="",
                ename=field_info.en_name,
                cname=field_info.cn_name,
                preview=f"{llm_dg_field_category_recommendation.model_dump_json()}",
                value="",
            )
            rules.append(pydantic_data_genius_rule)
            field_index += 1
            # 清空字段重试次数，开始下一个字段的推荐
            retry_count = 0
            continue
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
        logger.trace(f"llm_dg_field_category_recommendation chat_prompt: {chat_prompt}")
        try:
            llm_dg_field_category_recommendation = structured_llm.invoke(chat_prompt)
            logger.trace(
                f"llm_dg_field_category_recommendation.model_dump_json(): "
                f"{llm_dg_field_category_recommendation.model_dump_json()}"
            )
        except Exception as e:
            logger.error(f"llm_dg_field_category_recommendation error: {e}")
            last_error_message = str(e)
            retry_count += 1
        else:
            last_error_message = ""
            # 构建该字段的DataGenius规则参数
            # 处理字典规则
            args = {}
            name = ""
            category = llm_dg_field_category_recommendation.category
            if category in table_dictkey_map:
                dict_items: list[RecommendPanGuDictSchema] = table_dictkey_map.get(category)
                # TODO: 只取100个枚举值，因为DG的接口设计不支持太大的请求信息，会报413错误
                if len(dict_items) > 100:
                    dict_items = dict_items[:100]
                choices = [item.dict_id for item in dict_items]
                args = {"choices": choices}
                name = f"{category}_字典规则"
                category = "自定义-枚举"
                logger.debug(f"类别={llm_dg_field_category_recommendation.category} 更新为字典规则: {name}")
            pydantic_data_genius_rule = PydanticDataGeniusRule(
                col=field_index + 1,
                category=category,
                name=name,
                ename=field_info.en_name,
                cname=field_info.cn_name,
                preview=f"score: {llm_dg_field_category_recommendation.score}, reason: {llm_dg_field_category_recommendation.reason}",
                value=field_info.example,
                args=args
            )
            logger.trace(
                f"pydantic_data_genius_rule: {pydantic_data_genius_rule.model_dump_json()}"
            )
            rules.append(pydantic_data_genius_rule)
            field_index += 1
            # 清空字段重试次数，开始下一个字段的推荐
            retry_count = 0
    rule_uuid = str(uuid.uuid4())
    # 检查特例规则进行更新
    rules = [force_update_dg_rule(rule) for rule in rules]
    pydantic_data_genius_plan = PydanticDataGeniusPlan(
        rule_name=f"{SQL_MODE_DG_PLAN_CONFIG_PREFIX}{rule_uuid}.json",
        type_="规则",
        rows=row_count,
        separator="\t",
        rules=rules,
        output=f"{DG_STORAGE_PATH}/output/{client_ip}/{rule_uuid}",
        model=f"{DG_STORAGE_PATH}/models/{client_ip}/{table_en_name}",
        cols=len(table_metadata_info.raw_fields_info),
    )
    state["pydantic_data_genius_plan"] = pydantic_data_genius_plan
    return state


def save_dg_plan2json(state: SQLModeDataGenState):
    """
    存储DG执行计划任务配置
    Args:
        state:

    Returns:

    """
    logger.info("存储DataGenius任务规则")
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    table_metadata_info: TableMetadataSchema = state.get("table_metadata_info")
    if pydantic_data_genius_plan:
        data = pydantic_data_genius_plan.model_dump()
        save_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}.json"
        ).absolute()
        save_dict2jl(json_data=data, save_path=str(save_json_path))
    if table_metadata_info:
        table_metadata_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}_table_metadata.json"
        )
        save_dict2jl(
            json_data=table_metadata_info.model_dump(), save_path=table_metadata_json_path
        )
    return state


def create_dg_task(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    创建人DataGenius任务
    Args:
        state:

    Returns:

    """
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    table_info_data = state["table_info_data"]
    data_genius_headers = state["data_genius_headers"]
    table_en_name = table_info_data.table_en_name
    logger.info(
        f"创建DataGenius任务, 任务名称: {pydantic_data_genius_plan.rule_name} data_genius_headers: {data_genius_headers}"
    )
    pydantic_data_genius_plan_dict = pydantic_data_genius_plan.model_dump()
    payload = {
        "task": json.dumps(
            {
                "step": "2",
                "name": pydantic_data_genius_plan.rule_name,
                "type_": pydantic_data_genius_plan.type_,
                "modelName": table_en_name,
                "mode": "create",
                "task_id": "None",
                "duration": None,
                "output_filesize": None,
            }
        ),
        "rules": json.dumps(pydantic_data_genius_plan_dict["rules"]),
        "separator": pydantic_data_genius_plan.separator,
        "rows": pydantic_data_genius_plan.rows,
        "cols": pydantic_data_genius_plan.cols,
        "send": json.dumps(
            {
                "send_type": 1,
                "id": None,
                "tip": "无配置，点击刷新或添加。",
                "connect_test": False,
                "connect_test_tip": "",
                "table_name": "",
                "table_test": False,
                "table_test_tip": "",
                "table_columns": [],
                "schemas": "public",
            }
        ),
        "saveRuleFile": False,
        "blockSize": 100000,
        "source": "",
        "alam": json.dumps({"isRule": "1", "rule": "", "name": ""}),
    }

    save_json_path = DG_PAYLOAD_PATH.joinpath(
        f"payload_{pydantic_data_genius_plan.rule_name}"
    ).absolute()
    save_dict2jl(json_data=payload, save_path=str(save_json_path))
    create_task_url = urljoin(DG_SERVER_BASE_URL, DG_TASK_ADD_URL)

    with httpx.Client() as client:
        response = client.post(
            create_task_url, data=payload, headers=data_genius_headers
        )
    if response.status_code != 200:
        logger.error(f"请求{create_task_url}异常, status_code: {response.status_code}")
        state["create_data_genius_task_error"] = (
            f"请求{create_task_url}异常, status_code: {response.status_code}"
        )
        logger.debug(
            f"state.create_data_genius_task_error: {state['create_data_genius_task_error']}"
        )
    return state


def query_dg_task_status(state: SQLModeDataGenState) -> SQLModeDataGenState:
    """
    查询当前任务状态
    Args:
        state:

    Returns:

    """
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    logger.info(f"查询DataGenius进度, 任务名称: {pydantic_data_genius_plan.rule_name}")
    query_task_url = urljoin(DG_SERVER_BASE_URL, DG_TASK_HISTORY)
    payload = {"limit": 10}
    data_genius_headers = state["data_genius_headers"]
    with httpx.Client() as client:
        for _ in range(60):
            response = client.get(
                query_task_url, params=payload, headers=data_genius_headers
            )
            if response.status_code != 200:
                logger.error(
                    f"请求{query_task_url}异常, status_code: {response.status_code}"
                )
                state["query_data_genius_task_error"] = (
                    f"请求{query_task_url}异常, status_code: {response.status_code}"
                )
                return state
            resp_json = response.json()
            for result in resp_json.get("results", [{}]):
                if result.get("name", "") == pydantic_data_genius_plan.rule_name:
                    if result.get("status_name") == "成功":
                        logger.trace(f"matched result: {result}")
                        task_id = result.get("task_id", "not_found_task_id")
                        duration = result.get("duration_", "not_found_duration")
                        # 拼接URL
                        output_url = urljoin(
                            DG_SERVER_BASE_URL,
                            result.get("output", "not_found_output_url"),
                        )
                        output_filesize = result.get(
                            "output_filesize", "not_found_output_filesize"
                        )
                        data_genius_plan_edit_url = (
                            f"{DG_SERVER_BASE_URL}/{DG_NEW_TASK}?"
                            f"step=2&"
                            f"name={pydantic_data_genius_plan.rule_name}&"
                            f"type_={pydantic_data_genius_plan.type_}&"
                            f"modelName={pydantic_data_genius_plan.model}&"
                            f"mode=edit&"
                            f"task_id={task_id}"
                        )
                        logger.debug(
                            f"duration: {duration}\n output_url: {output_url}\n "
                            f"output_filesize: {output_filesize}\n"
                            f"data_genius_plan_edit_url: {data_genius_plan_edit_url}"
                        )
                        state["data_genius_plan_task_id"] = task_id
                        state["data_genius_plan_run_duration"] = duration
                        state["data_genius_plan_output_url"] = output_url
                        state["data_genius_plan_output_filesize"] = output_filesize
                        state["data_genius_plan_edit_url"] = data_genius_plan_edit_url
                        return state
            time.sleep(2)
    return state


sql_mode_data_gen_builder = StateGraph(SQLModeDataGenState)
sql_mode_data_gen_builder.add_node("analyze_intent", analyze_data_intent)
sql_mode_data_gen_builder.add_node(
    "intent_human_feedback_node", data_intent_human_feedback_node
)
sql_mode_data_gen_builder.add_node("sql_parse_to_table_info", sql_parse_to_table_info)
sql_mode_data_gen_builder.add_node("rag_sql_table_filed_info", rag_sql_table_filed_info)
# sql_mode_data_gen_builder.add_node("add_pg_dict2dg_category", add_pg_dict2dg_category)
sql_mode_data_gen_builder.add_node("dg_category_recommend", dg_rule_processor)
sql_mode_data_gen_builder.add_node("save_dg_plan2json", save_dg_plan2json)
sql_mode_data_gen_builder.add_node("create_dg_task", create_dg_task)
sql_mode_data_gen_builder.add_node("query_dg_task_status", query_dg_task_status)

sql_mode_data_gen_builder.add_conditional_edges(
    START, detect_input_type, ["sql_parse_to_table_info", "analyze_intent"]
)
sql_mode_data_gen_builder.add_edge("analyze_intent", "intent_human_feedback_node")
sql_mode_data_gen_builder.add_conditional_edges(
    "intent_human_feedback_node",
    should_data_intent_continue,
    ["analyze_intent", "sql_parse_to_table_info"],
)
sql_mode_data_gen_builder.add_edge("sql_parse_to_table_info", "rag_sql_table_filed_info")
sql_mode_data_gen_builder.add_edge("rag_sql_table_filed_info", "dg_category_recommend")
# sql_mode_data_gen_builder.add_edge("add_pg_dict2dg_category", "dg_category_recommend")
sql_mode_data_gen_builder.add_edge("dg_category_recommend", "save_dg_plan2json")
sql_mode_data_gen_builder.add_edge("save_dg_plan2json", "create_dg_task")
sql_mode_data_gen_builder.add_edge("create_dg_task", "query_dg_task_status")
sql_mode_data_gen_builder.add_edge("query_dg_task_status", END)

memory = MemorySaver()
sql_mode_data_gen_graph = sql_mode_data_gen_builder.compile(
    interrupt_before=["intent_human_feedback_node"], checkpointer=memory
)

if __name__ == "__main__":
    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH

    from utils.log import LogManager

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="DataForgeSQLModeDataGenApp.log",
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))
    init_env()

    print(sql_mode_data_gen_graph.get_graph(xray=True).draw_mermaid())
    user_input = """SQL内容(必填): select MD_ID, ACCOUNTNAME, USERNUM, USERID, MOBILE, NICKNAME, REGIS_TIME, REGISIP, REGISIPID, REGISIP_LOCATION, REGISIPPORT, REGISIP_PROVINCIAL_CODE, REGISIP_CITY_CODE, REGISIP_COUNTRY_CODE, REGISIP_REGIONAL_CODE, PACKAGENAME, CAPTURE_TIME, ACTIONTYPE, ACTIONTIME from XY_BF_ACCOUNT
    期望生成数据条数(必填): 100"""
    session_id = uuid.uuid4().hex
    thread = {"configurable": {"thread_id": session_id}}
    init_state = {
        "user_input": user_input,
        "user_intent": DataGenSQLModeUserIntentSchema(
            **{
                "sql": "select MD_ID, ACCOUNTNAME, USERNUM, USERID, MOBILE, NICKNAME, REGIS_TIME, REGISIP, REGISIPID, REGISIP_LOCATION, REGISIPPORT, REGISIP_PROVINCIAL_CODE, REGISIP_CITY_CODE, REGISIP_COUNTRY_CODE, REGISIP_REGIONAL_CODE, PACKAGENAME, CAPTURE_TIME, ACTIONTYPE, ACTIONTIME from XY_BF_ACCOUNT",
                "data_count": 100,
            }
        ),
        "human_intent_feedback": "正确",
        "max_retries": 5,
        "client_ip": "10.0.23.57",
        "session_id": session_id,
    }
    for event in sql_mode_data_gen_graph.stream(
            init_state, thread, stream_mode="values"
    ):
        user_intent: DataGenSQLModeUserIntentSchema = event.get("user_intent")
        if user_intent:
            logger.info(f"user_intent: {user_intent.model_dump_json(indent=2)}")
        # 模拟用户意图识别的研判反馈
        # sql_mode_data_gen_graph.update_state(thread, {"human_intent_feedback": "正确"},
        #                                      as_node="intent_human_feedback_node")
        # for event in sql_mode_data_gen_graph.stream(None, thread, stream_mode="values"):
        # Review
        human_intent_feedback = event.get("human_intent_feedback")
        if human_intent_feedback:
            logger.info(f"human_intent_feedback: {human_intent_feedback}")

        table_info_error = event.get("table_info_error")
        if table_info_error:
            logger.info(f"table_info_error: {table_info_error}")

        table_info_data: SQLModeTableInfoSchema = event.get("table_info_data")
        if table_info_data:
            logger.info(f"table_info_data: {table_info_data.model_dump_json()}")

        table_metadata_info = event.get("table_metadata_info")
        if table_metadata_info:
            logger.info(f"table_metadata_info: {table_metadata_info.model_dump_json()}")

        table_metadata_error = event.get("table_metadata_error")
        if table_metadata_error:
            logger.info(f"table_metadata_error: {table_metadata_error}")

        table_dict_category_code_map = event.get("table_dict_category_code_map")
        if table_dict_category_code_map:
            logger.info(f"table_dict_category_code_map: {table_dict_category_code_map}")

        create_data_genius_task_error = event.get("create_data_genius_task_error")
        if create_data_genius_task_error:
            logger.info(
                f"create_data_genius_task_error: {create_data_genius_task_error}"
            )

        query_data_genius_task_error = event.get("query_data_genius_task_error")
        if query_data_genius_task_error:
            logger.info(f"query_data_genius_task_error: {query_data_genius_task_error}")

        data_genius_plan_run_duration = event.get("data_genius_plan_run_duration")
        if data_genius_plan_run_duration:
            logger.info(
                f"data_genius_plan_run_duration: {data_genius_plan_run_duration}"
            )

        data_genius_plan_output_url = event.get("data_genius_plan_output_url")
        if data_genius_plan_output_url:
            logger.info(f"data_genius_plan_output_url: {data_genius_plan_output_url}")

        data_genius_plan_output_filesize = event.get("data_genius_plan_output_filesize")
        if data_genius_plan_output_filesize:
            logger.info(
                f"data_genius_plan_output_filesize: {data_genius_plan_output_filesize}"
            )
