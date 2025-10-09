#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/25 14:42
# @Author   : guoqun X2590
# @FileName : dg_api_client.py
# @Project  : DataForge

import time
from typing import Any, Union
from urllib.parse import urljoin

import httpx
from langchain_core.messages import ToolMessage
from loguru import logger

from agent.dg_configs import (
    DG_GENERATE_TASK_URL,
    DG_NEW_TASK,
    DG_RULE_PREVIEW,
    DG_SERVER_BASE_URL,
    DG_TASK_HISTORY,
)
from agent.state import MetaModeDataGenState, SQLModeDataGenState, TableMetadataSchema
from config import DG_PAYLOAD_PATH
from cruds.task import save_task_info
from utils.db_manager import DatabaseManager
from utils.file import save_dict2jl


def dg_rule_data_preview(
    rule_data: list[dict[str, Any]],
) -> tuple[bool, str, list[dict[str, Any]]]:
    """
    调用DG的规则预览接口查看规则的预览数据

    Args:
        rule_data (list[dict[str, Any]]): _description_

    Returns:
        tuple[bool, str, list[dict[str, Any]]]: _description_
    """
    logger.info("获取DG规则预览数据")
    rule_preview_url = urljoin(DG_SERVER_BASE_URL, DG_RULE_PREVIEW)
    message = "ok"
    data = [{}]
    with httpx.Client() as client:
        response = client.post(rule_preview_url, json=rule_data)
    if response.status_code != 200:
        message = f"请求{rule_preview_url}异常, status_code: {response.status_code}"
        return False, message, data
    try:
        resp_json = response.json()
    except Exception as err:
        message = f"获取{rule_preview_url}响应体异常, ERROR: {err}"
        return False, message, data
    if flag := resp_json.get("flag") is True:
        data = resp_json.get("data", data)
    else:
        message = f"接口{rule_preview_url}响应体flag为{flag}, 异常请DG检查"

    return flag, message, data


def create_dg_task(
    state: Union[SQLModeDataGenState, MetaModeDataGenState],
) -> Union[SQLModeDataGenState, MetaModeDataGenState]:
    """
    创建人DataGenius任务
    Args:
        state:

    Returns:

    """
    logger.info("创建DG任务")
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    client_ip = state["client_ip"]
    state["data_genius_headers"] = {"SPECIFIEDIP": client_ip}
    data_genius_headers = state["data_genius_headers"]
    table_metadata_info: TableMetadataSchema | None = state.get("table_metadata_info")
    if table_metadata_info is None:
        error = "state的table_metadata_info为None, 无法获取table_en_name"
        logger.error(error)
        state["error_messages"].append(ToolMessage(error))
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
            # TODO: 如果发现异常，不应该再查询了，需要加个节点
            state["create_data_genius_task_error"] = (
                f"创建任务异常{create_task_url}, error: {info}"
            )
    task_data = state["task_data"]
    task_data.task_payload = payload
    state["task_data"] = task_data
    return state


def query_dg_task_status(
    state: Union[SQLModeDataGenState, MetaModeDataGenState],
) -> Union[SQLModeDataGenState, MetaModeDataGenState]:
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
    task_data = state["task_data"]
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
                task_data.dg_task_status = 1
                state["task_data"] = task_data
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
                        # 更新任务信息
                        task_data.dg_task_status = 0
                        task_data.dg_task_message = "成功"
                        task_data.dg_task_id = task_id
                        task_data.dg_task_edit_url = data_genius_plan_edit_url

                        # TODO: 调用 DG的genius/get-preview接口，
                        # 获取响应的data结果作为预览数据
                        get_preview_status, get_preview_message, preview_data = (
                            dg_rule_data_preview(rule_data=task_data.task_rule)
                        )
                        if get_preview_status:
                            task_data.dg_task_rule_data_preview = preview_data
                        else:
                            logger.error(get_preview_message)
                        task_data.dg_task_duration = duration
                        state["task_data"] = task_data
                        return state
                    elif result.get("status_name") == "执行中":
                        continue
                    else:
                        # DG任务结果不是成功
                        task_data.dg_task_status = 1
                        task_data.dg_task_message = result.get("status_name")
                        state["task_data"] = task_data
                        return state
            time.sleep(2)
        # 等到超时了，dg也没给结果
        task_data.dg_task_status = 1
        state["task_data"] = task_data
        return state
    return state


def save_task_info2db(
    state: Union[SQLModeDataGenState, MetaModeDataGenState],
) -> Union[SQLModeDataGenState, MetaModeDataGenState]:
    """存储任务信息到数据库

    Args:
        state (Union[SQLModeDataGenState, DataGenState]): _description_

    Returns:
        Union[SQLModeDataGenState, DataGenState]: _description_
    """
    logger.info("存储任务信息到数据库")
    task_data = state["task_data"]
    mode = state.get("mode")
    logger.info(f"gen mode: {mode}")
    task_data.mode = mode
    db_manager = DatabaseManager()
    save_status, save_message = save_task_info(
        db_manager=db_manager, task_info_data=task_data.model_dump()
    )
    if save_status is False:
        logger.error(save_message)
    db_manager.close()
    # 清理state
    return {"user_intent": None}  # type: ignore
