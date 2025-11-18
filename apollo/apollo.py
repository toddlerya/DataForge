#!/usr/bin/env python
# coding: utf-8
# @File    :   apollo.py
# @Time    :   2024/5/16 14:22
# @Author  :   guo qun X2590
# @Desc    :   None

from copy import deepcopy

import requests
import urllib3
from urllib3.exceptions import InsecureRequestWarning

from config import APOLLO_WEB_IP, APOLLO_WEB_PORT, HEADERS
from utils.http import slash_join
from utils.log import logger


class Apollo:
    def __init__(
        self,
        ip: str = APOLLO_WEB_IP,
        port: int = APOLLO_WEB_PORT,
        app_id: str = "Polaris",
        name_space: str = "Polaris.public",
    ):
        self.ip = ip
        self.port = port
        self.app_id = app_id
        self.name_space = name_space
        # 阿波罗配置中心
        self.APOLLO_CREATE_APP_URL = (
            f"https://{self.ip}:{self.port}/openapi/v1/apps/create-app"
        )
        self.APOLLO_CREATE_APP_PAYLOAD = {"appId": "Polaris", "name": "北极星"}
        self.APOLLO_CREATE_AUTHORIZATION_HEADER = {
            "Authorization": "f1ae5a2e2f6967719f0b7b360a62bd36b146e42b"
        }
        self.APOLLO_FETCH_URL = (
            f"https://{self.ip}:{self.port}"
            f"/openapi/v1/envs/PRO/apps/{self.app_id}/clusters/default/namespaces/{self.name_space}"
        )
        self.APOLLO_QUERY_BY_KEY_URL = f"{self.APOLLO_FETCH_URL}/items/"
        self.headers = deepcopy(HEADERS)
        logger.info(f"阿波罗配置中心服务: https://{self.ip}:{self.port}")
        self.token = ""
        # 禁用https的证书警告
        urllib3.disable_warnings(InsecureRequestWarning)

    def auth(self) -> tuple[bool, str]:
        """
        认证获取token
        Returns:

        """
        headers = deepcopy(HEADERS)
        headers.update({**self.APOLLO_CREATE_AUTHORIZATION_HEADER})
        try:
            resp = requests.post(
                url=self.APOLLO_CREATE_APP_URL,
                headers=headers,
                proxies=None,
                verify=False,
                timeout=60,
                json=self.APOLLO_CREATE_APP_PAYLOAD,
            )
        except Exception as err:
            message = f"调用{self.APOLLO_CREATE_APP_URL}接口异常: {err}"
            return False, message
        else:
            if resp.status_code != 200:
                message = f"获取Apollo的token失败, HTTP_STATUS_CODE: {resp.status_code}"
                return False, message
            try:
                resp_data = resp.json()
            except Exception as err:
                return False, f"URL {self.APOLLO_CREATE_APP_URL} resp.json()异常: {err}"
            if resp_data.get("status", "") != "OLD":
                message = (
                    f"不应出现此情况: [POST] URL: {self.APOLLO_CREATE_APP_URL} "
                    f"HEADERS: {headers} PAYLOAD: {self.APOLLO_CREATE_APP_PAYLOAD} "
                    f"RESPONSE: {resp_data}"
                )
                return False, message
            else:
                self.token = resp_data.get("token", "未获取到token")
                return True, "ok"

    def fetch_all_config(self) -> tuple[bool, str, list[dict[str, str | int]]]:
        """
        获取全部配置
        Returns:

        """
        headers = deepcopy(HEADERS)
        headers.update({"Authorization": self.token})
        try:
            resp = requests.get(
                url=self.APOLLO_FETCH_URL,
                headers=headers,
                proxies=None,
                verify=False,
                timeout=60,
            )
        except Exception as err:
            message = f"调用{self.APOLLO_FETCH_URL}接口异常: {err}"
            return False, message, [{}]
        else:
            if resp.status_code != 200:
                message = (
                    f"获取Apollo的全部配置失败, [GET] URL: {self.APOLLO_FETCH_URL} "
                    f"HEADERS: {headers} HTTP_STATUS_CODE: {resp.status_code}"
                )
                return False, message, [{}]
        try:
            resp_data = resp.json()
        except Exception as err:
            return (
                False,
                f"URL {self.APOLLO_CREATE_APP_URL} resp.json()异常: {err}",
                [{}],
            )
        if resp_data.get("appId", "") != self.app_id:
            message = (
                f"[appId!={self.app_id}]不应出现此情况: [GET] "
                f"URL: {self.APOLLO_FETCH_URL} "
                f"HEADERS: {headers} RESPONSE: appId={resp_data.get('appId')}, "
                f"与请求的appId={self.app_id}不同"
            )
            return False, message, [{}]
        value_array = resp_data.get("items", [{}])
        if value_array and value_array[0]:
            return True, "ok", value_array
        else:
            message = (
                f"[响应体没有items]不应出现此情况: [GET] URL: {self.APOLLO_FETCH_URL} "
                f"HEADERS: {headers} RESPONSE: {resp_data}"
            )
            return False, message, value_array

    def query_value_by_key(self, key: str) -> tuple[bool, str]:
        """
        根据key，查询阿波罗中某个配置
        Args:
            key:

        Returns:

        """
        headers = deepcopy(HEADERS)
        headers.update({"Authorization": self.token})
        url = slash_join(self.APOLLO_QUERY_BY_KEY_URL, key)
        try:
            resp = requests.get(
                url=url, headers=headers, proxies=None, verify=False, timeout=60
            )
        except Exception as err:
            logger.error(f"调用{url}接口异常: {err}")
            return False, ""
        else:
            if resp.status_code != 200:
                logger.error(
                    f"获取Apollo的{key}的配置值失败, "
                    f"HTTP_STATUS_CODE: {resp.status_code}"
                )
                return False, ""
            resp_data = resp.json()
            if resp_data.get("key", "") != key:
                logger.warning(
                    f"不应出现此情况: [GET] URL: {url} HEADERS: {headers} "
                    f"RESPONSE: {resp_data}"
                )
            value = resp_data.get("value", "未获取到value")
            return True, value

    def fetch_and_format_all_config(
        self,
    ) -> tuple[bool, str, dict[str, list[dict[str, str | int]]]]:
        """
        格式化为PolarisInspectionConfig的结果格式
        Returns:

        """
        result_array = []

        auth_status, auth_message = self.auth()
        if auth_status is False:
            return (
                auth_status,
                f"apollo获取token失败: {auth_message}",
                {"config_list": result_array},
            )
        _status, _message, _value_array = self.fetch_all_config()
        if _status:
            for index, each_value in enumerate(_value_array):
                each_result = {
                    "projectName": self.app_id,
                    "nameSpaceName": self.name_space,
                    "key": each_value.get("key"),
                    "value": each_value.get("value"),
                    "comment": each_value.get("comment"),
                    "id": index + 1,
                    "modifyTime": each_value.get("dataChangeLastModifiedTime"),
                }
                result_array.append(each_result)
            return _status, "ok", {"config_list": result_array}
        else:
            _message = "获取阿波罗配置中心数据, "
            f"格式化为PolarisInspectionConfig的结果结构失败: {_message}"
            return _status, _message, {"config_list": result_array}


if __name__ == "__main__":
    import json

    test_d_env = "172.21.4.30"
    dev_env = "172.16.110.144"
    dev3_env = "172.16.112.99"
    apollo = Apollo(ip=test_d_env)
    status, message, _result_array = apollo.fetch_and_format_all_config()
    print(status)
    print(message)
    print(json.dumps(_result_array, ensure_ascii=False))
