#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/10/15 15:31
# @Author   : guoqun X2590
# @Desc     :

from typing import Optional

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt
from loguru import logger

from agent.state import TREExportFileSchema, TSMLState, TSMLUserIntentSchema
from agent.tre_service_api_client import tre_service_upload_file


def validate_tsml_input_args(state: TSMLState):
    """校验tsml图的输入信息,若没有提示用户提供所需内容"""
    tre_export_file_info: Optional[TREExportFileSchema] = state.get(
        "tre_export_file_info"
    )
    logger.trace(f"tre_export_file_info={tre_export_file_info}")
    if tre_export_file_info:
        logger.debug(f"tre_export_file_info={tre_export_file_info.model_dump_json()} ")
        return "analyze_tsml_intent"
    else:
        logger.warning("用户未上传tsml文件")
        return "wait_human_upload_tsml_file"


def wait_human_upload_tsml_file(state: TSMLState):
    tre_export_file_info = interrupt("请上传TRE导出的tsml文件和sql文件")
    state["tre_export_file_info"] = tre_export_file_info
    return state


def analyze_tsml_intent(state: TSMLState) -> TSMLState:
    """分析tsml意图

    Args:
        state (ExploreState): _description_

    Returns:
        ExploreState: _description_
    """
    messages = state["messages"]
    last_message = messages[-1]
    tre_export_file_info = state.get("tre_export_file_info")
    logger.debug(
        f"last_message: {type(last_message)} {last_message} "
        f"tre_export_file_info={tre_export_file_info}"
    )
    if tre_export_file_info:
        state["messages"].append(
            AIMessage(content=f"已收到TRE导出的文件: {tre_export_file_info}")
        )
        state["tsml_user_intent"] = TSMLUserIntentSchema(
            tre_export_file_info=tre_export_file_info,
            plans=[
                "1. 解析TSML文件提取SELECT SQL",
                "2. 根据提取SELECT SQL构造测试数据",
                "3. 将测试数据入库",
                "4. 执行TSML获取结果",
            ],
        )
    return state


def upload_tre_files_node(state: TSMLState) -> TSMLState:
    """上传TRE运行所需文件"""
    logger.info("上传TRE文件")
    task_id = state.get("session_id")
    tre_export_file_info = state.get("tre_export_file_info")
    if not tre_export_file_info:
        logger.error("未获取需要上传的TRE文件")
        return state
    # 上传TSML文件
    if tre_tsml_file_info := tre_export_file_info.tre_tsml_file_info:
        tsml_upload_message, tsml_upload_resp = tre_service_upload_file(
            file_name=tre_tsml_file_info.name,
            file_path=pathlib.Path(tre_tsml_file_info.path),
            task_id=task_id,
        )
        if tsml_upload_message != "ok":
            state["messages"].append(AIMessage(content=tsml_upload_message))

    return state


def parse_tsml_by_tsml_test_engine(state: TSMLState):
    """调用tsml测试引擎服务解析tsml文件"""
    tre_export_file_info = state.get("tre_export_file_info")
    if tre_export_file_info:
        # 上传文件
        logger.info("模拟请求tsml测试引擎.")
        # 获取响应
        logger.info("模拟获取响应结果")
        tsml_parse_result = {
            "model_name": "特定域名",
            "model_desc": "重点人特定域名离线分析模型",
            "model_category": "9999",
            "model_code": "3201_11_10375",
            "gen_data_sqls": {
                "zdr_dict_tab": "SELECT create_time, create_userid, create_userorg, "
                "dict_id, dict_name, dict_name_simplify, dict_pid, dict_type, level, "
                "modify_time, remark, sort, status FROM zdr_dict_tab;",
                "relation_nostatus": "SELECT dept_id, entity_id, model_id, "
                "rule_id, rule_name, rule_type, userid FROM relation_nostatus;",
            },
        }
        state["tsml_parse_result"] = tsml_parse_result
    return state


def query_sql_data_gen_result(state: TSMLState):
    session_id = state.get("session_id")
    if session_id:
        # 使用任务uuid查询是否生成完成了
        sql_data_gen_result = {"zdr_dict_tab": 1000, "relation_nostatus": 2000}
        state["sql_data_gen_result"] = sql_data_gen_result
    return state


def query_tsml_run_result(state: TSMLState):
    session_id = state.get("session_id")
    if session_id:
        # 使用任务uuid查询是否生成完成了
        tsml_run_result = {
            "summary": "TSML运行结果概要....",
            "stauts": "成功",
            "input": 1000,
            "output": 2000,
            "report": f"http://tsml.test.engine/report/{session_id}.html",
        }
        state["tsml_run_result"] = tsml_run_result
    return state


tsml_builder = StateGraph(TSMLState)
tsml_builder.add_node("wait_human_upload_tsml_file", wait_human_upload_tsml_file)
tsml_builder.add_node("analyze_tsml_intent", analyze_tsml_intent)
tsml_builder.add_node("parse_tsml_by_tsml_test_engine", parse_tsml_by_tsml_test_engine)
tsml_builder.add_node("query_sql_data_gen_result", query_sql_data_gen_result)
tsml_builder.add_node("query_tsml_run_result", query_tsml_run_result)

tsml_builder.add_conditional_edges(
    START,
    validate_tsml_input_args,
    ["analyze_tsml_intent", "wait_human_upload_tsml_file"],
)
tsml_builder.add_edge("wait_human_upload_tsml_file", "analyze_tsml_intent")
tsml_builder.add_edge("analyze_tsml_intent", "parse_tsml_by_tsml_test_engine")
tsml_builder.add_edge("parse_tsml_by_tsml_test_engine", "query_sql_data_gen_result")
tsml_builder.add_edge("query_sql_data_gen_result", "query_tsml_run_result")
tsml_builder.add_edge("query_tsml_run_result", END)

memory = InMemorySaver()
tsml_graph = tsml_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    import pathlib

    from common.initialization import init_env, setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager

    current_file_path = pathlib.Path(__file__)
    current_log_name = (
        f"{current_file_path.name.replace(current_file_path.suffix, '')}.log"
    )

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name=current_log_name,
        file_log_level="TRACE",
    )
    setup_logging(log_config.get_config().get("handlers"))

    init_env()
    print(tsml_graph.get_graph(xray=True).draw_mermaid())
