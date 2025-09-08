#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/08 17:25
# @Author   : guoqun X2590
# @Desc     : 环境配置采集器


from apollo.apollo import Apollo
from config import (
    METADATA_DB_IP,
    METADATA_DB_NAME,
    METADATA_DB_PASSWORD,
    METADATA_DB_PORT,
    METADATA_DB_USER,
    PANGU_WEB_IP,
    TRE_DOMAIN_DATA_IP,
)
from utils.db import Database
from utils.log import logger


class EnvInfoCrawler:
    def __init__(self, inner_db_handler: Database) -> None:
        """初始化存储入库对象

        Args:
            inner_db_handler (Database): _description_
        """
        self.db_handler = inner_db_handler
        self.env_uuid = ""
        self.environment_data = {}

    def fetch_environment_info(
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
        self.environment_data = {
            "env_name": env_name,
            "apollo_web_ip": apollo_ip,
            "tre_domain_data_bdp_web_ip": tre_domain_data_bdp_web_ip,
        }
        env_config_keys_pair = {
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
        config_list_data = data.get("config_list", [])
        if not config_list_data:
            # 没有获取到配置信息
            remark = "获取阿波罗配置信息为空! 使用config.py配置临时替代!"
            logger.warning(remark)
            config_list_data = [
                {"key": "Metadata_Dbn_ip", "value": METADATA_DB_IP},
                {"key": "Metadata_Dbn_dbPort", "value": METADATA_DB_PORT},
                {"key": "Metadata_Dbn_dbUser", "value": METADATA_DB_USER},
                {"key": "Metadata_Dbn_dbPassword", "value": METADATA_DB_PASSWORD},
                {"key": "Metadata_Dbn_dbName", "value": METADATA_DB_NAME},
                {"key": "pangu_web_ip", "value": PANGU_WEB_IP},
                {"key": "TRE_DOMAIN_DATA_ip", "value": TRE_DOMAIN_DATA_IP},
            ]
        for key, value in env_config_keys_pair.items():
            for item_config in config_list_data:
                if key == item_config.get("key", ""):
                    self.environment_data[value] = item_config.get("value", "")
                    # ip参数计算uuid
                    if value.endswith("ip"):
                        env_uuid_input += item_config.get("value", "")
