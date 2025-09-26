#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/26 14:38
# @Author   : guoqun X2590
# @Desc     : 公共的Node
from typing import Union

from agent.state import DataGenState, SQLModeDataGenState


def clear_task_state(
    state: Union[SQLModeDataGenState, DataGenState],
) -> Union[SQLModeDataGenState, DataGenState]:
    # 需要保留的跨任务的状态
    persistent_keys = {
        "messages",
        "session_id",
        "client_ip",
        "max_retries",
    }
    # 创建新的干净的状态
    clean_state = {key: state[key] for key in persistent_keys if key in state}
    # 重置任务特定状态
    clean_state.update({})
    return state
