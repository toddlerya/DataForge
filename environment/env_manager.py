#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/10 10:44
# @Author   : guoqun X2590
# @Desc     : 环境配置管理器

import json
from typing import Optional

from config import ENVRIONMENT_CONFIG, PROJECT_PATH
from crawler.env_info_crawler import EnvInfoCrawler
from cruds.environment import change_env_status
from database_models.schema import EnvironmentConfigYAMLSchema, EnvironmentOtherConfig
from database_models.sys_enum import EnvironmentStatus
from utils.db_manager import DatabaseManager
from utils.file import load_yaml_from_file
from utils.log import logger


def load_all_env_config_from_yaml_and_update_db():
    """读取environment.yaml配置并更新数据库配置和定时任务

    Returns:
        _type_: _description_
    """
    logger.info(f"读取环境YAML配置: {ENVRIONMENT_CONFIG}")
    db_manager = DatabaseManager()
    config_yaml = ENVRIONMENT_CONFIG
    config_data_slice: list[EnvironmentConfigYAMLSchema] = []
    env_manager = EnvironmentManager(db_manager=db_manager)
    message, data = load_yaml_from_file(yaml_file_path=config_yaml)
    if message != "ok":
        logger.error(message)
        raise Exception(message)
    logger.trace(f"{config_yaml} ==> {json.dumps(data, ensure_ascii=False)}")
    # 校验
    config_data_slice = [EnvironmentConfigYAMLSchema(**ele) for ele in data]
    for each_env_data in config_data_slice:
        logger.debug(f"each_env_data: {id(each_env_data)} {each_env_data}")
        env_manager.env_name = each_env_data.env_name
        if each_env_data.apollo_web_ip:
            env_manager.apollo_web_ip = each_env_data.apollo_web_ip
        if each_env_data.tre_domain_data_bdp_web_ip:
            env_manager.tre_domain_data_bdp_web_ip = (
                each_env_data.tre_domain_data_bdp_web_ip
            )
        if each_env_data.other_configs:
            env_manager.other_configs = each_env_data.other_configs
        # 注册并更新
        env_manager.register_and_update()
        # 配置开关设置调度
        if each_env_data.status is EnvironmentStatus.enable:
            env_manager.enable()
        elif each_env_data.status is EnvironmentStatus.disable:
            env_manager.disable()
        elif each_env_data.status is EnvironmentStatus.retired:
            env_manager.retired()
        # 重置对象配置值
        env_manager.reset()
    db_manager.close()


def validate_ipv4(value: str, value_name: str):
    if not isinstance(value, str):
        raise TypeError(f"{{value_name}} must be a string, input {value_name}={value}")
    # 简单 IP 校验（可扩展为正则）
    parts = value.strip().split(".")
    if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        raise ValueError(f"Invalid IP format, input {value_name}={value}")


class EnvironmentManager:
    def __init__(self, db_manager: DatabaseManager) -> None:
        self.db_manager = db_manager
        self.env_name: str = ""
        self.apollo_web_ip: str = ""
        self.tre_domain_data_bdp_web_ip: str = ""
        self.other_configs: Optional[EnvironmentOtherConfig] = None
        self.env_info_crawler = EnvInfoCrawler(inner_db_manager=self.db_manager)
        self.validator()

    @logger.catch
    def validator(self):
        """校验合法性"""
        logger.info("校验参数合法性")
        if self.env_name:
            if not isinstance(self.env_name, str):
                raise TypeError("env_name must be a string")
            self.env_name = self.env_name.strip()
            if len(self.env_name) < 3:
                raise ValueError(
                    f"env_name too short (min 4 chars), input env_name={self.env_name}"
                )
            if len(self.env_name) > 128:
                raise ValueError(
                    f"env_name too long (max 128 chars), input env_name={self.env_name}"
                )
        if self.apollo_web_ip:
            validate_ipv4(value=self.apollo_web_ip, value_name="apollo_web_ip")
        if self.tre_domain_data_bdp_web_ip:
            validate_ipv4(
                value=self.tre_domain_data_bdp_web_ip,
                value_name="tre_domain_data_bdp_web_ip",
            )
        if self.other_configs:
            if not isinstance(self.other_configs, (EnvironmentOtherConfig)):
                raise TypeError("other_configs must be EnvironmentOtherConfig")

    @logger.catch
    def reset(self):
        """重置参数"""
        self.env_name = ""
        self.apollo_web_ip = ""
        self.tre_domain_data_bdp_web_ip = ""
        self.other_configs = None

    @logger.catch
    def register_and_update(self):
        """注册和更新环境配置"""
        if not self.env_name:
            raise AttributeError("env_name不能为空")
        if not self.apollo_web_ip and not self.other_configs:
            raise AttributeError("apollo_web_ip和other_configs至少有一个不可为空")
        # 采集阿波罗配置，更新数据库配置
        if self.apollo_web_ip:
            # 采集apollo信息并入库存储
            if not self.env_info_crawler.fetch_and_save_environment_info(
                env_name=self.env_name,
                apollo_ip=self.apollo_web_ip,
                tre_domain_data_bdp_web_ip=self.tre_domain_data_bdp_web_ip,
            ):
                logger.error(
                    f"Apollo配置注册更新异常! "
                    f"env_name={self.env_name} "
                    f"apollo_web_ip={self.apollo_web_ip}"
                )
        # 其他独立配置信息入库
        if self.other_configs:
            if not self.env_info_crawler.standalone_environment_info_save(
                env_name=self.env_name, other_configs=self.other_configs
            ):
                logger.error(
                    f"独立配置注册更新异常!"
                    f"env_name={self.env_name}"
                    f"other_configs={self.other_configs.model_dump_json()}"
                )

    def retired(self):
        """废弃环境配置"""
        change_env_status(
            env_name=self.env_name,
            status=EnvironmentStatus.retired,
            db_manager=self.db_manager,
        )
        # TODO: 移除定时任务

    def enable(self):
        """启用环境配置并添加任务"""
        change_env_status(
            env_name=self.env_name,
            status=EnvironmentStatus.enable,
            db_manager=self.db_manager,
        )
        # TODO: 添加定时任务

    def disable(self):
        """禁用环境配置"""
        change_env_status(
            env_name=self.env_name,
            status=EnvironmentStatus.disable,
            db_manager=self.db_manager,
        )
        # TODO: 移除定时任务

    def __repr__(self) -> str:
        return (
            "EnvironmentRegister("
            f"env_name='{self.env_name}', "
            f"apollo_web_ip='{self.apollo_web_ip}', "
            f"tre_domain_data_bdp_web_ip={self.tre_domain_data_bdp_web_ip}"
            f"other_configs={
                self.other_configs.model_dump_json() if self.other_configs else None
            }, "
            ")"
        )

    def model_dump(self) -> dict:
        """兼容 Pydantic 的 model_dump 接口"""
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


if __name__ == "__main__":
    from loguru import logger

    from common.initialization import setup_logging
    from config import PROJECT_PATH
    from utils.log import LogManager

    log_config = LogManager(
        base_path=str(PROJECT_PATH.absolute()),
        log_path="logs",
        log_name="debug.log",
        file_log_level="TRACE",
        console_log_level="DEBUG",
    )
    setup_logging(log_config.get_config().get("handlers"))

    # env_manager = EnvironmentManager(db_manager=DatabaseManager())
    # env_manager.read_config()
    # env_manager.env_name = "测试部仿真测试环境"
    # env_manager.apollo_web_ip = APOLLO_WEB_IP
    # env_manager.tre_domain_data_bdp_web_ip = TRE_DOMAIN_DATA_BDP_IP
    # other_configs = EnvironmentOtherConfig(
    #     postgresql=RelationalDatabaseConfig(), mysql=None, tsml=None
    # )
    # env_manager.other_configs = other_configs
    # env_manager.register_and_update()

    load_all_env_config_from_yaml_and_update_db()
