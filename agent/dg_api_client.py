#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/25 14:42
# @Author   : guoqun X2590
# @FileName : dg_api_client.py
# @Project  : DataForge

import time
from typing import Union
from urllib.parse import urljoin

import httpx
from langchain_core.messages import ToolMessage
from loguru import logger

from agent.dg_configs import (
    DG_GENERATE_TASK_URL,
    DG_NEW_TASK,
    DG_SERVER_BASE_URL,
    DG_TASK_HISTORY,
)
from agent.state import (
    DataGenState,
    DataGenUserIntentSchema,
    SQLModeDataGenState,
    TableMetadataSchema,
)
from config import DG_PAYLOAD_PATH
from utils.file import save_dict2jl


def create_dg_task(
    state: Union[SQLModeDataGenState, DataGenState],
) -> Union[SQLModeDataGenState, DataGenState]:
    """
    创建人DataGenius任务
    Args:
        state:

    Returns:

    """
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    user_intent = state["user_intent"]
    client_ip = state["client_ip"]
    state["data_genius_headers"] = {"USER_PROVIDE_IP": client_ip}
    data_genius_headers = state["data_genius_headers"]
    if isinstance(user_intent, DataGenUserIntentSchema):
        table_en_name = user_intent.table_en_names[0]
    else:
        table_metadata_info: TableMetadataSchema | None = state.get(
            "table_metadata_info"
        )
        if table_metadata_info is None:
            error = (
                "SQLModeDataGenState: state的table_metadata_info为None, "
                "无法获取table_en_name"
            )
            logger.error(error)
            state["error_message"].append(ToolMessage(error))
            return state
        table_en_name = table_metadata_info.table_en_name
    logger.info(
        f"创建DataGenius任务, 任务名称: {pydantic_data_genius_plan.rule_name} "
        f"data_genius_headers: {data_genius_headers}"
    )
    pydantic_data_genius_plan_dict = pydantic_data_genius_plan.model_dump()
    payload = {
        "task": {
            "step": "2",
            "name": pydantic_data_genius_plan.rule_name,
            "type_": pydantic_data_genius_plan.type_,
            "modelName": table_en_name,
            "mode": "create",
            "task_id": "None",
            "duration": None,
            "output_filesize": None,
        },
        "rules": pydantic_data_genius_plan_dict["rules"],
        "separator": pydantic_data_genius_plan.separator,
        "rows": pydantic_data_genius_plan.rows,
        "cols": pydantic_data_genius_plan.cols,
        "send": {
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
        },
        "saveRuleFile": False,
        "blockSize": 100000,
        "source": "",
        "alam": {"isRule": "1", "rule": "", "name": ""},
        "user": client_ip,
    }

    save_json_path = DG_PAYLOAD_PATH.joinpath(
        f"payload_{pydantic_data_genius_plan.rule_name}.json"
    ).absolute()
    save_dict2jl(json_data=payload, save_path=str(save_json_path))
    create_task_url = urljoin(DG_SERVER_BASE_URL, DG_GENERATE_TASK_URL)

    with httpx.Client() as client:
        response = client.post(create_task_url, json=payload)
    if response.status_code != 200:
        logger.error(f"请求{create_task_url}异常, status_code: {response.status_code}")
        state["create_data_genius_task_error"] = (
            f"请求{create_task_url}异常, status_code: {response.status_code}"
        )
    try:
        resp_json = response.json()
    except Exception as err:
        logger.error(f"获取{create_task_url}响应体异常, ERROR: {err}")
        state["create_data_genius_task_error"] = (
            f"请求{create_task_url}异常, error: {err}"
        )
    else:
        if resp_json.get("flag"):
            state["data_genius_task_id"] = resp_json.get("task_id", "no_get_task_id")
        else:
            info = resp_json.get("info")
            logger.error(f"创建任务异常{create_task_url}, info: {info}")
            state["create_data_genius_task_error"] = (
                f"创建任务异常{create_task_url}, error: {info}"
            )
    return state


def query_dg_task_status(
    state: Union[SQLModeDataGenState, DataGenState],
) -> Union[SQLModeDataGenState, DataGenState]:
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
    logger.info(f"data_genius_headers: {data_genius_headers}")
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
