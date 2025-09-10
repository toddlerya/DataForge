#!/usr/bin/env python
# coding: utf-8
# @File    :   configs.py
# @Time    :   2023/11/3 18:30
# @Author  :   guo qun X2590
# @Desc    :   None


import os
import pathlib

ENV_LOG_LEVEL = os.getenv("LOG_LEVEL", default="INFO")
ENV_SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", default=0)
ENV_HOST = os.getenv("SERVER_HOST", default="0.0.0.0")
ENV_PORT = os.getenv("SERVER_PORT", default=25702)

APOLLO_ENV_NAME = os.getenv("APOLLO_ENV_NAME", "测试部D环境")
APOLLO_WEB_IP = os.getenv("APOLLO_WEB_IP", default="172.21.4.30")
APOLLO_WEB_PORT = int(os.getenv("APOLLO_WEB_PORT", default=8070))
TRE_DOMAIN_DATA_BDP_IP = os.getenv("TRE_DOMAIN_DATA_BDP_IP", "172.16.29.12")
TRE_DOMAIN_DATA_IP = os.getenv("TRE_DOMAIN_DATA_IP", "172.17.63.12")
DEFAULT_DATA_EXPIRED_DAY = 15
ENV_DATA_EXPIRED_DAY = os.getenv("DATA_EXPIRED_DAY", DEFAULT_DATA_EXPIRED_DAY)

# 阿波罗配置 Polaris.Polaris.public
BDP_WEB_IP = os.getenv("BDP_WEB_IP", "172.21.4.33")
LOCAL_CITYCODE = os.getenv("LOCAL_CITYCODE", "320100")
# 盘古界面配置 pangu_web_ip
PANGU_WEB_IP = os.getenv("PANGU_WEB_IP", "172.16.113.100")
# 盘古元数据库配置 jdbc:postgresql://172.21.4.32:5432/metadata20250421
# Metadata_Dbn_ip
METADATA_DB_IP = os.getenv("METADATA_DB_IP", "172.21.4.32")
# Metadata_Dbn_dbPort
METADATA_DB_PORT = os.getenv("METADATA_DB_PORT", 5432)
# Metadata_Dbn_dbUser
METADATA_DB_USER = os.getenv("METADATA_DB_USER", "metadata20250116")
# Metadata_Dbn_dbPassword
METADATA_DB_PASSWORD = os.getenv("METADATA_DB_PASSWORD", "metadata_20250116")
# Metadata_Dbn_dbName
METADATA_DB_NAME = os.getenv("METADATA_DB_NAME", "metadata20250421")
# BDP App Info
PANGU_APP_ID = os.getenv("PANGU_APP_ID", "pangu")
TRE_DOMAIN_DATA_APP_ID = os.getenv("TRE_DOMAIN_DATA_APP_ID", "offsite")


try:
    ENV_DATA_EXPIRED_DAY = int(ENV_DATA_EXPIRED_DAY)
except ValueError as _:
    print(
        f"DATA_EXPIRED_DAY配置不是整数, 请确认, 使用默认值{DEFAULT_DATA_EXPIRED_DAY}. "
        f"current value: {ENV_DATA_EXPIRED_DAY} type: {type(ENV_DATA_EXPIRED_DAY)}"
    )
    ENV_DATA_EXPIRED_DAY = DEFAULT_DATA_EXPIRED_DAY


PROJECT_PATH = pathlib.Path(__file__).parent
SAVE_DATA_PATH = PROJECT_PATH.joinpath("data").absolute()
DG_PLAN_PATH = SAVE_DATA_PATH.joinpath("dg_plan").absolute()
DG_PAYLOAD_PATH = SAVE_DATA_PATH.joinpath("dg_payload").absolute()
GEN_TABLE_MODELS_BASE_PATH = SAVE_DATA_PATH.joinpath("gen_table_models").absolute()
GEN_TABLE_MODELS_TEMP_PATH = GEN_TABLE_MODELS_BASE_PATH.joinpath("temp").absolute()
GEN_TABLE_MODELS_DATA_PATH = GEN_TABLE_MODELS_BASE_PATH.joinpath("data").absolute()
CONF_DATA_PATH = PROJECT_PATH.joinpath("conf").absolute()
DATABASE_PATH = PROJECT_PATH.joinpath("database").absolute()

PRESET_FIXED_DG_RULE_PATH = PROJECT_PATH.joinpath(
    "preset_fixed_field_dg_rule"
).absolute()
PRESET_FIXED_PANGU_DG_RULE_PATH = PRESET_FIXED_DG_RULE_PATH.joinpath("pangu.yaml")
PRESET_FIXED_TRE_DG_RULE_PATH = PRESET_FIXED_DG_RULE_PATH.joinpath("tre.yaml")

PICK_DATA_SQL_LIMIT = 1
BEGIN_TIME_OFFSET = -60
END_TIME_OFFSET = 0
DATETIME_RANGE_DESC = "近两个月"

# FMDB表命名空间
MASS_DATA_NAMESPACE = "massdata"
FMDB_META_NAMESPACE = "fmdbmeta"
TAOSHA_NAMESPACE = "taosha"
NB_MASS_NO_NAMESPACE = "nb_mass"

TASK_TIMEOUT = 60 * 60 * 2


print(
    f"当前运行日志级别: {ENV_LOG_LEVEL} "
    f"数据默认保留{ENV_DATA_EXPIRED_DAY}天, {__file__}"
)


ENV_DB_MODE = "POSTGRESQL"
DIALECT = "postgresql"
DRIVER = "psycopg2"
DB_HOST = os.getenv("INNER_DB_HOST", "172.16.108.3")
DB_PORT = 5432
DB_USERNAME = "data_forge"
DB_PASSWORD = "data_forge_2590"
DB_NAME = "data_forge"
CHARSET = "UTF8"
SQLALCHEMY_URL = (
    f"{DIALECT}+{DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?client_encoding={CHARSET}"
)

# SQLAlchemy Config
SQLALCHEMY_ECHO = True if int(ENV_SQLALCHEMY_ECHO) else False
SQLALCHEMY_AUTO_FLUSH = True
SQLALCHEMY_AUTO_COMMIT = False


HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/103.0.5060.53 Safari/537.36 PolarisInspection/1.0.0"
}


# 数据域配置
data_scope_ip_port = "172.17.63.12:12018"
data_scope_resource_url = (
    f"https://{data_scope_ip_port}/offsite/v1/domain/page/resource"
)
data_scope_resource_detail_url = (
    f"https://{data_scope_ip_port}/offsite/v1/resource/detail"
)
data_scope_cookie = (
    "contextPath=/offsite; citycode=330000; appId=offsite; "
    "topoptid=offsite; userToken=e52cd971b6b34d6cb2392f509afb28e3; "
    "appToken=dd9da97d36d247d18c60cf73327b4c7c"
)

DG_PLAN_CONFIG_PREFIX = "dg_task_plan_"
SQL_MODE_DG_PLAN_CONFIG_PREFIX = "sql_dg_task_plan_"

DG_HEADERS = {"USER_PROVIDE_IP": "10.0.23.57"}
