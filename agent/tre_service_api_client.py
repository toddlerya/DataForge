#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/10/24 14:11
# @Author   : guoqun X2590
# @Desc     :

from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import httpx
from loguru import logger

from agent.tre_service_configs import (
    TRE_ENGINE_SERVER_BASE_URL,
    TRE_ENGINE_SERVER_RUN_URL,
    TRE_ENGINE_SERVER_STATUS_URL,
    TRE_ENGINE_SERVER_UPLOAD_URL,
)


def tre_service_upload_file(
    file_path: Path, file_name: str, task_id: str
) -> tuple[str, dict[str, Any]]:
    """
    调用上传TRE文件接口

    Args:
        file_path (Path): _description_
        file_name (str): _description_
        task_id (str): _description_

    Returns:
        tuple[str, dict[str, Any]]: _description_
    """
    tre_service_upload_url = urljoin(
        TRE_ENGINE_SERVER_BASE_URL, TRE_ENGINE_SERVER_UPLOAD_URL
    )
    logger.info(f"调用TRE-Service {tre_service_upload_url}接口")
    message = "ok"
    resp_json = {}
    with httpx.Client() as client:
        with open(file=file_path, mode="rb") as f:
            files = {"file": (file_name, f, "text/plain")}
            data = {"task_id": task_id}
            response = client.post(tre_service_upload_url, data=data, files=files)
            if response.status_code != 200:
                try:
                    resp_json = response.json()
                except Exception:
                    pass
                message = (
                    f"请求 {tre_service_upload_url} 异常, "
                    f"status_code: {response.status_code} "
                    f"resp_json: {resp_json}"
                )
                return message, resp_json
            try:
                resp_json = response.json()
            except Exception as err:
                message = f"获取 {tre_service_upload_url} 响应体异常, ERROR: {err}"
                return message, resp_json
            if resp_message := resp_json.get("message", ""):
                if not resp_message.endswith("上传成功"):
                    message = (
                        f"接口 {tre_service_upload_url} 响应体message为{resp_message}, "
                        f"异常请TRE-Service检查"
                    )
    return message, resp_json


def tre_service_run(task_id: str):
    """运行任务

    Args:
        task_id (str): _description_
    """
    tre_service_run_url = urljoin(TRE_ENGINE_SERVER_BASE_URL, TRE_ENGINE_SERVER_RUN_URL)
    logger.info(f"调用TRE-Service {tre_service_run_url}接口")
    message = "ok"
    resp_json = {}
    with httpx.Client() as client:
        response = client.post(url=tre_service_run_url, params={"task_id": task_id})
        if response.status_code != 200:
            try:
                resp_json = response.json()
            except Exception:
                pass
            message = (
                f"请求 {tre_service_run_url} 异常, "
                f"status_code: {response.status_code} resp_json={resp_json}"
            )
            return message, resp_json
        try:
            resp_json = response.json()
        except Exception as err:
            message = f"获取 {tre_service_run_url} 响应体异常, ERROR: {err}"
            return message, resp_json
        if resp_message := resp_json.get("message", ""):
            if not resp_message.endswith("任务开始处理"):
                message = (
                    f"接口 {tre_service_run_url} 响应体message为{resp_message}, "
                    f"异常请TRE-Service检查"
                )
    return message, resp_json


async def tre_service_status(task_id: str):
    """查看任务状态"""
    tre_service_status_url = urljoin(
        TRE_ENGINE_SERVER_BASE_URL, TRE_ENGINE_SERVER_STATUS_URL
    )
    logger.info(f"调用TRE-Service {tre_service_status_url}接口")
    message = "ok"
    resp_json = {}
    with httpx.Client() as client:
        response = client.get(url=tre_service_status_url, params={"task_id": task_id})
        if response.status_code != 200:
            try:
                resp_json = response.json()
            except Exception:
                pass
            message = (
                f"请求 {tre_service_status_url} 异常, "
                f"status_code: {response.status_code} resp_json={resp_json}"
            )
            return message, resp_json
        try:
            resp_json = response.json()
        except Exception as err:
            message = f"获取 {tre_service_status_url} 响应体异常, ERROR: {err}"
            return message, resp_json
        if resp_message := resp_json.get("message", ""):
            if not resp_message.endswith("任务开始处理"):
                message = (
                    f"接口 {tre_service_status_url} 响应体message为{resp_message}, "
                    f"异常请TRE-Service检查"
                )
    return message, resp_json


if __name__ == "__main__":
    import asyncio

    m, r = asyncio.run(tre_service_status(task_id="8afd4fb93814ca96fae6c28858f4be58"))
    print(m)
    print(r)
