#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/08 15:27
# @Author   : guoqun X2590
# @Desc     : 创建应用的BDP Token

import httpx

from utils.log import logger


def create_bdp_token(
    bdp_ip: str, app_id: str, ip: str = "", user_id: int = -1, bdp_port: int = 8090
) -> tuple[str, dict]:
    """创建BDPtoken

    Args:
        bdp_ip (str): _description_
        app_id (str): _description_
        ip (str, optional): _description_. Defaults to "".
        user_id (int, optional): _description_. Defaults to -1.
        bdp_port (int, optional): _description_. Defaults to 8090.
    """
    logger.info("获取DG规则预览数据")
    url = f"http://{bdp_ip}:{bdp_port}/cas/api/v1/token/create"
    message = "ok"
    payload = {
        "appId": app_id,
        "userId": user_id,
    }
    data = {}
    if ip:
        payload.update({"ip": ip})
    with httpx.Client() as client:
        response = client.post(url, data=payload)
    if response.status_code != 200:
        message = f"请求{url}异常, status_code: {response.status_code}"
        return message, data
    try:
        resp_json = response.json()
    except Exception as err:
        message = f"获取{url}响应体异常, ERROR: {err}"
        return message, data
    if msg := resp_json.get("msg") == "操作成功":
        data = resp_json.get("data", data)
    else:
        message = (
            f"接口{url}响应体msg为{msg}, 请确认BDP服务是否正常以及请求参数是否正常"
        )
    return message, data
