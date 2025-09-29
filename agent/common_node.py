#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/26 14:38
# @Author   : guoqun X2590
# @Desc     : 公共的Node

from typing import Union

from loguru import logger

from agent.state import (
    MainAppState,
    MetaModeDataGenState,
    SQLModeDataGenState,
    TableMetadataSchema,
)
from config import DG_PLAN_PATH
from utils.file import save_dict2jl


def save_dg_plan2json(
    state: Union[MetaModeDataGenState, SQLModeDataGenState],
) -> Union[MetaModeDataGenState, SQLModeDataGenState]:
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
            json_data=table_metadata_info.model_dump(),
            save_path=table_metadata_json_path,
        )
    return state


def restart_graph(
    state: Union[MainAppState, MetaModeDataGenState, SQLModeDataGenState],
    config: dict,
    # clear_keys: set = {
    #     "user_input",
    #     "user_intent",
    #     "main_user_intent",
    #     "next_sub_graph_name",
    #     "human_intent_feedback",
    #     "dont_run_dg_task",
    # },
) -> Union[MainAppState, MetaModeDataGenState, SQLModeDataGenState]:
    """清空所有状态重置图

    Args:
        state (Union[MainAppState,MetaModeDataGenState, SQLModeDataGenState]): _description_
        config (RunnableConfig): _description_
        graph (CompiledStateGraph): _description_
        clear_keys (Set): 需要清空的state的key

    Returns:
        Union[MainAppState,MetaModeDataGenState, SQLModeDataGenState]: _description_
    """
    # values = {}
    # for key in clear_keys:
    #     if key in state:
    #         values.update({key: None})
    logger.info("restart_graph start...")
    if config and state:
        # 重新始化state
        # 获取用户的反馈内容
        human_intent_feedback = state.get("human_intent_feedback", "你好")
        logger.info(f"human_intent_feedback: {human_intent_feedback}")
        configurable = config.get("configurable", {})
        pregel_checkpointer = configurable.get("__pregel_checkpointer")
        thread_id = configurable.get("thread_id")
        if pregel_checkpointer and thread_id:
            pregel_checkpointer.delete_thread(thread_id)
        else:
            logger.error(
                f"pregel_checkpointer={pregel_checkpointer} thread_id={thread_id}"
            )
    else:
        logger.error(f"无法重启图  config={config}")
    return state
