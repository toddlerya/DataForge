#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/08 17:25
# @Author   : guoqun X2590
# @Desc     : 环境配置采集器

import json

from apollo.apollo import Apollo
from config import (
    BDP_WEB_IP,
    LOCAL_CITYCODE,
    METADATA_DB_IP,
    METADATA_DB_NAME,
    METADATA_DB_PASSWORD,
    METADATA_DB_PORT,
    METADATA_DB_USER,
    PANGU_WEB_IP,
    TRE_DOMAIN_DATA_IP,
)
from cruds.environment import save_environment_info
from database_models.schema import EnvironmentOtherConfig
from utils.db_manager import DatabaseManager
from utils.file import get_md5
from utils.log import logger


class EnvInfoCrawler:
    def __init__(self, inner_db_manager: DatabaseManager) -> None:
        """初始化存储入库对象

        Args:
            inner_db_manager (inner_db_manager): _description_
        """
        self.inner_db_manager = inner_db_manager
        self.environment_data: dict[str, str | int | dict] = {}

    def fetch_and_save_environment_info(
        self, env_name: str, apollo_ip: str, tre_domain_data_bdp_web_ip: str
    ) -> bool:
        """更新配置中心的环境配置信息

        Args:
            env_name (str): _description_
            apollo_ip (str): _description_
            tre_domain_data_bdp_web_ip (str): _description_
        Returns:
            bool: _description_
        """
        # 清空属性信息
        self.environment_data = {}
        # 设置基础信息
        self.environment_data = {
            "env_name": env_name,
            "apollo_web_ip": apollo_ip,
            "tre_domain_data_bdp_web_ip": tre_domain_data_bdp_web_ip,
        }
        remark = ""
        apollo_env_config_keys_pair = {
            "LOCAL_CITYCODE": "local_city_code",
            "BDPWeb_ip": "bdp_web_ip",
            "pangu_web_ip": "pangu_web_ip",
            "Metadata_Dbn_ip": "metadata_db_ip",
            "Metadata_Dbn_dbPort": "metadata_db_port",
            "Metadata_Dbn_dbUser": "metadata_db_user",
            "Metadata_Dbn_dbPassword": "metadata_db_password",
            "Metadata_Dbn_dbName": "metadata_db_name",
            "TRE_DOMAIN_DATA_ip": "tre_domain_data_ip",
        }
        logger.info(f"更新环境配置信息: {env_name} 当前使用的Apollo IP: {apollo_ip}")
        apollo = Apollo(ip=apollo_ip)
        status, message, data = apollo.fetch_and_format_all_config()
        if status is False or message != "ok":
            logger.error(message)
        config_list_data: list[dict[str, str | int]] = data.get("config_list", [])
        if not config_list_data:
            # 没有获取到配置信息
            remark = "获取阿波罗配置信息为空! 使用config.py配置临时替代!"
            logger.warning(remark)
            config_list_data = [
                {"key": "local_city_code", "value": LOCAL_CITYCODE},
                {"key": "bdp_web_ip", "value": BDP_WEB_IP},
                {"key": "pangu_web_ip", "value": PANGU_WEB_IP},
                {"key": "Metadata_Dbn_ip", "value": METADATA_DB_IP},
                {"key": "Metadata_Dbn_dbPort", "value": METADATA_DB_PORT},
                {"key": "Metadata_Dbn_dbUser", "value": METADATA_DB_USER},
                {"key": "Metadata_Dbn_dbPassword", "value": METADATA_DB_PASSWORD},
                {"key": "Metadata_Dbn_dbName", "value": METADATA_DB_NAME},
                {"key": "TRE_DOMAIN_DATA_ip", "value": TRE_DOMAIN_DATA_IP},
            ]
        env_hash_input: str = f"{apollo_ip}{tre_domain_data_bdp_web_ip}"
        for apollo_key, value in apollo_env_config_keys_pair.items():
            for item_config in config_list_data:
                if apollo_key == item_config.get("key", ""):
                    self.environment_data[value] = item_config.get("value", "")
                    # 拼接env_hash计算字段
                    env_hash_input += str(item_config.get("value", ""))
        # 计算env_hash
        md5_status, env_hash = get_md5(env_hash_input)
        if md5_status is False:
            logger.error("计算env_uuid错误!")
            return False
        self.environment_data.update({"env_hash": env_hash, "remark": remark})
        logger.debug(
            "记录环境配置信息为: "
            f"{json.dumps(self.environment_data, ensure_ascii=False)}"
        )
        save_status, save_message = save_environment_info(
            environment_data=self.environment_data, db_manager=self.inner_db_manager
        )
        if save_status is False:
            logger.error(save_message)
            return False
        return True

    def standalone_environment_info_save(
        self, env_name: str, other_configs: EnvironmentOtherConfig
    ) -> bool:
        """非WA体系阿波罗管理的其他环境配置场景

        Args:
            env_name (str): _description_
            other_configs (EnvironmentOtherConfig): _description_
        """
        # 清空属性信息
        self.environment_data = {}
        logger.info(
            f"更新环境配置信息: {env_name} "
            f"非Apollo配置场景. other_configs: "
            f"{other_configs.model_dump_json()}"
        )

        # 设置基础信息
        self.environment_data = {
            "env_name": env_name,
        }
        remark = "非Apollo配置场景"
        # 计算env_uuid
        md5_status, env_hash = get_md5(other_configs.model_dump_json())
        if md5_status is False:
            logger.error("计算env_uuid错误!")
            return False
        self.environment_data.update(
            {
                "env_hash": env_hash,
                "other_configs": other_configs.model_dump(),
                "remark": remark,
            }
        )
        save_status, save_message = save_environment_info(
            environment_data=self.environment_data, db_manager=self.inner_db_manager
        )
        if save_status is False:
            logger.error(save_message)
            return False
        return True
