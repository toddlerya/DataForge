#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/28 09:17
# @Author   : guoqun X2590
# @Desc     : DG相关流程


from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger

from agent.common_node import save_dg_plan2json
from agent.dg_api_client import create_dg_task, query_dg_task_status, save_task_info2db
from agent.dg_rule_processor import dg_rule_processor
from agent.state import DataGenBaseState


def is_pre_heat_dg_rule_mode(state: DataGenBaseState):
    """
    如果是预热字段推荐DG规则模式则不创建DG任务
    Args:
        state:

    Returns:

    """
    pre_heat_mode = state.get("pre_heat_mode", False)
    if pre_heat_mode is True:
        return END
    else:
        return "save_dg_plan2json"


def is_only_dg_rule_gen_mode(state: DataGenBaseState):
    """如果是DG规则生成模式,则不需要创建DG任务,但需要存储此次调用的任务规则信息

    Args:
        state (DataGenState): _description_
    """
    dont_run_dg_task = state.get("dont_run_dg_task")
    logger.info(f"dont_run_dg_task: {dont_run_dg_task}")
    if dont_run_dg_task is True:
        return "save_task_info2db"
    else:
        return "create_dg_task"


dg_builder = StateGraph(DataGenBaseState)
dg_builder.add_node("dg_rule_processor", dg_rule_processor)
dg_builder.add_node("save_dg_plan2json", save_dg_plan2json)
dg_builder.add_node("create_dg_task", create_dg_task)
dg_builder.add_node("query_dg_task_status", query_dg_task_status)
dg_builder.add_node("save_task_info2db", save_task_info2db)


dg_builder.add_edge(START, "dg_rule_processor")
dg_builder.add_conditional_edges(
    "dg_rule_processor", is_pre_heat_dg_rule_mode, ["save_dg_plan2json", END]
)
dg_builder.add_conditional_edges(
    "save_dg_plan2json",
    is_only_dg_rule_gen_mode,
    ["save_task_info2db", "create_dg_task"],
)
dg_builder.add_edge("create_dg_task", "query_dg_task_status")
dg_builder.add_edge("query_dg_task_status", "save_task_info2db")
dg_builder.add_edge("save_task_info2db", END)

memory = InMemorySaver()
process_dg_graph = dg_builder.compile(checkpointer=memory)


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
    print(process_dg_graph.get_graph(xray=True).draw_mermaid())
    logger.info("\n" + process_dg_graph.get_graph(xray=True).draw_mermaid())
