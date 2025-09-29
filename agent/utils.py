#!/usr/bin/env python
# coding: utf-8
# @File    :   utils.py
# @Time    :   2025/05/09 15:23:17
# @Author  :   toddlerya
# @Desc    :   None

import json
from datetime import datetime, timezone
from typing import Union

import aiofiles
from langchain_core.runnables.config import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from loguru import logger

from agent.state import MainAppState, MetaModeDataGenState, SQLModeDataGenState


async def save_json_data_async(save_json_path, fake_data):
    async with aiofiles.open(save_json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(fake_data, ensure_ascii=False, indent=2))


FIELD_TYPE_MAP = {"int": int, "string": str}


def today_timestamp_range() -> tuple[str, str]:
    """
    获取当日开始时间（00:00:00）到当前时刻的时间戳区间范围（以秒为单位）。
    :return: (start_timestamp, end_timestamp)
    """
    # 获取当前时间（UTC+0）
    now = datetime.now(timezone.utc)
    # 获取当天的开始时间（00:00:00）
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # 获取当前时间的时间戳（秒）
    end_timestamp = int(now.timestamp())
    # 获取当天开始时间的时间戳（秒）
    start_timestamp = int(start_of_day.timestamp())
    return str(start_timestamp), str(end_timestamp)


def reset_graph_state(
    state: Union[MainAppState, MetaModeDataGenState, SQLModeDataGenState],
    run_config: RunnableConfig,
    graph: CompiledStateGraph,
    clear_keys: set = {
        "user_input",
        "user_intent",
        "main_user_intent",
        "next_sub_graph_name",
        "human_intent_feedback",
        "dont_run_dg_task",
    },
) -> tuple[
    Union[MainAppState, MetaModeDataGenState, SQLModeDataGenState], RunnableConfig
]:
    """重置输入和意图

    Args:
        state (Union[MainAppState,MetaModeDataGenState, SQLModeDataGenState]): _description_
        config (RunnableConfig): _description_
        graph (CompiledStateGraph): _description_
        clear_keys (Set): 需要清空的state的key

    Returns:
        Union[MainAppState,MetaModeDataGenState, SQLModeDataGenState]: _description_
        RunnableConfig: _description_
    """
    values = {}
    for key in clear_keys:
        if key in state:
            values.update({key: None})
    new_run_config = graph.update_state(run_config, values=values)
    logger.info(f"new_run_config: {new_run_config}")
    graph.invoke(None, new_run_config)
    return state, new_run_config
