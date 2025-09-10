#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/10 10:44
# @Author   : guoqun X2590
# @Desc     : 环境配置注册器

from typing import Optional

from apollo.apollo import Apollo
from database_models.schema import EnvironmentOtherConfig
from utils.log import logger


class EnvironmentManager:
    def __init__(self) -> None:
        self._env_name: str = ""
        self._apollo_web_ip: str = ""
        self._tre_domain_data_bdp_web_ip: str = ""
        self._other_configs: Optional[EnvironmentOtherConfig] = None

    @logger.catch
    def register(self):
        """注册环境配置"""
        if not self._env_name:
            raise AttributeError("env_name不能为空")
        if not self._apollo_web_ip and not self._other_configs:
            raise AttributeError("apollo_web_ip和other_configs至少有一个不可为空")
        if self._apollo_web_ip:
            # 采集apollo信息
            apollo = Apollo(ip=self._apollo_web_ip)
            apollo_status, apollo_message, apollo_result = (
                apollo.fetch_and_format_all_config()
            )
            if apollo_status is False:
                logger.error(apollo_message)
                raise Exception(apollo_message)
            result_array = apollo_result.get("config_list")

    def remove(self, env_name: str):
        """移除环境配置"""

    def enable(self, env_name: str):
        """启用环境配置"""

    def disable(self, env_name: str):
        """禁用环境配置"""

    # env_name 的 setter
    @property
    def env_name(self) -> str:
        return self._env_name

    @env_name.setter
    def env_name(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("env_name must be a string")
        if len(value) < 3:
            raise ValueError("env_name too short (min 4 chars)")
        self._env_name = value

    # apollo_web_ip 的 setter
    @property
    def apollo_web_ip(self) -> str:
        return self._apollo_web_ip

    @apollo_web_ip.setter
    def apollo_web_ip(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("apollo_web_ip must be a string")
        # 简单 IP 校验（可扩展为正则）
        parts = value.strip().split(".")
        if len(parts) != 4 or not all(
            p.isdigit() and 0 <= int(p) <= 255 for p in parts
        ):
            raise ValueError("Invalid IP format")
        self._apollo_web_ip = value.strip()

    # tre_domain_data_bdp_web_ip 的 setter
    @property
    def tre_domain_data_bdp_web_ip(self) -> str:
        return self._tre_domain_data_bdp_web_ip

    @tre_domain_data_bdp_web_ip.setter
    def tre_domain_data_bdp_web_ip(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("tre_domain_data_bdp_web_ip must be a string")
        # 简单 IP 校验（可扩展为正则）
        parts = value.strip().split(".")
        if len(parts) != 4 or not all(
            p.isdigit() and 0 <= int(p) <= 255 for p in parts
        ):
            raise ValueError("Invalid IP format")
        self._tre_domain_data_bdp_web_ip = value.strip()

    # other_configs 的 setter
    @property
    def other_configs(self) -> Optional[EnvironmentOtherConfig]:
        return self._other_configs

    @other_configs.setter
    def other_configs(self, value: Optional[EnvironmentOtherConfig]) -> None:
        if not isinstance(value, (EnvironmentOtherConfig, type(None))):
            raise TypeError("other_configs must be EnvironmentOtherConfig or None")
        self._other_configs = value

    def __repr__(self) -> str:
        return (
            f"EnvironmentRegister("
            f"env_name='{self.env_name}', "
            f"apollo_web_ip='{self.apollo_web_ip}', "
            f"tre_domain_data_bdp_web_ip={self.tre_domain_data_bdp_web_ip}"
            f"other_configs={self.other_configs})"
        )

    def model_dump(self) -> dict:
        """兼容 Pydantic 的 model_dump 接口（可选）"""
        return {
            "env_name": self.env_name,
            "apollo_web_ip": self.apollo_web_ip,
            "tre_domain_data_bdp_web_ip": self.tre_domain_data_bdp_web_ip,
            "other_configs": self.other_configs.model_dump()
            if self.other_configs
            else None,
        }

    def __eq__(self, other) -> bool:
        if not isinstance(other, EnvironmentManager):
            return False
        return (
            self.env_name == other.env_name
            and self.apollo_web_ip == other.apollo_web_ip
            and self.tre_domain_data_bdp_web_ip == other.tre_domain_data_bdp_web_ip
            and self.other_configs == other.other_configs
        )
