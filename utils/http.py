#!/usr/bin/env python
# coding: utf-8
# @File    :   http.py
# @Time    :   2023/11/20 14:52
# @Author  :   guo qun X2590
# @Desc    :   None


import shutil
from typing import Optional, Tuple, Union

import requests

from config import HEADERS
from utils.log import logger


def slash_join(*parts):
    """
    将多个URL部分拼接为一个完整的URL
    """
    return "/".join(part.strip("/") for part in parts)


def http_cli(
    session: requests.Session,
    method: str,
    url: str,
    payload=None,
    payload_type: str = "",
    files: Optional[Union[dict, tuple, list]] = None,
    timeout: int = 60,
    stream: bool = False,
    verify: bool = False,
) -> Tuple[bool, str, Optional[requests.Response]]:
    """
    HTTP 客户端
    Args:
    session: 请求会话
        method:  请求方法
        url:     请求地址
        payload: 请求参数
        payload_type: params|json|data
        timeout: 超时时间, 默认60秒
        stream: 流传输
        verify: 验证SSL证书
    Returns:
        (status, message, Response)
    """
    if payload is None:
        payload = {}
    message = "ok"
    status = True
    resp = None
    method = method.lower()
    if payload_type:
        kwargs = {
            "method": method,
            "url": url,
            payload_type: payload,
            "files": files,
            "timeout": timeout,
            "proxies": None,
            "headers": HEADERS,
            "stream": stream,
            "verify": verify,
        }
    else:
        kwargs = {
            "method": method,
            "url": url,
            "files": files,
            "timeout": timeout,
            "proxies": None,
            "headers": HEADERS,
            "stream": stream,
            "verify": verify,
        }
    try:
        resp = session.request(**kwargs)
    except Exception as err:
        message = f"HTTP Client 发送请求失败: {kwargs}，错误信息: {err}"
        status = False
    else:
        if resp.status_code != 200:
            if resp.status_code == 422:
                message = (
                    f"HTTP请求失败: HTTP_STATUS_CODE: {resp.status_code}, "
                    f"METHOD: {method}, URL: {url}, "
                    f"PAYLOAD: {payload} RESPONSE: {resp.json()}"
                )
            else:
                message = (
                    f"HTTP请求失败: HTTP_STATUS_CODE: {resp.status_code}, "
                    f"METHOD: {method}, URL: {url}, "
                    f"PAYLOAD: {payload}"
                )
            status = False
            logger.error(message)
    return status, message, resp


def resp2json(resp: requests.Response) -> Tuple[bool, str, dict]:
    """
    将响应体对象转为json数据
    Args:
        resp : 响应体对象

    Returns:
        (status, message, data)
    """
    status = True
    message = "ok"
    data = {}
    try:
        data = resp.json()
    except requests.RequestException as err:
        message = f"解析响应体获取JSON失败: {err}"
        status = False
        logger.error(message)
    return status, message, data


def resp2file(resp: requests.Response, save_file_path: str) -> Tuple[bool, str]:
    """
    将响应体存储为文件
    Args:
        resp: 响应体对象
        save_file_path: 存储文件的路径

    Returns:
        (status, message)
    """
    status = True
    message = "ok"
    try:
        with open(file=save_file_path, mode="wb") as f:
            resp.raw.decode_content = True
            shutil.copyfileobj(resp.raw, f)
    except Exception as err:
        message = (
            f"存储响应体为文件失败: SAVE_FILE_PATH: {save_file_path}, ERROR: {err}"
        )
        status = False
        logger.error(message)
    return status, message
