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
test_d_env = "172.21.4.30"
ENV_APOLLO_IP = os.getenv("APOLLO_WEB_IP", default=test_d_env)
ENV_APOLLO_WEB_PORT = int(os.getenv("APOLLO_WEB_PORT", default=8070))
DEFAULT_DATA_EXPIRED_DAY = 15
ENV_DATA_EXPIRED_DAY = os.getenv("DATA_EXPIRED_DAY", DEFAULT_DATA_EXPIRED_DAY)
try:
    ENV_DATA_EXPIRED_DAY = int(ENV_DATA_EXPIRED_DAY)
except ValueError as _:
    print(
        f"DATA_EXPIRED_DAY配置不是整数, 请确认, 使用默认值{DEFAULT_DATA_EXPIRED_DAY}. "
        f"current value: {ENV_DATA_EXPIRED_DAY} type: {type(ENV_DATA_EXPIRED_DAY)}"
    )
    ENV_DATA_EXPIRED_DAY = DEFAULT_DATA_EXPIRED_DAY

SERVER_PORT = 20211

PROJECT_PATH = pathlib.Path(__file__).parent

TTH_BASE_API = "http://TTHServer:20235/api/tth"
TTH_TOOL_TASK_STATUS_API = "/tool/task/status"
TTH_TOOL_TASK_RESULT_SUMMARY_API = "/tool/task/result/summary"
TTH_TOOL_TASK_RESULT_SUMMARY_FILE_API = "/tool/task/result/summary/file"
TTH_TOOL_TASK_RESULT_RECORD_API = "/tool/task/result/record"
TTH_TOOL_TASK_RESULT_RECORD_FILE_API = "/tool/task/result/record/file"
TTH_TOOL_TASK_CASE_STATUS_API = "/tool/task/case/status"
TTH_TOOL_TASK_CASE_RECORD_API = "/tool/task/case/record"
TTH_REGISTRY_API = "/tool/registry"

PANGU_API_STATUS = "/app/api/job_status/"
PANGU_API_DATA_SIZE = "/app/api/data_size"
PANGU_API_KINSHIP_INFO = "/app/api/kinship_info"
PANGU_API_JOB_INFO = "/app/api/job_info"
PANGU_WAIT_SECONDS = 60 * 30

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

# LABELS
POLARIS_LABEL = "Polaris"

PANGU_TASK_API_PORT = 11019

# 阿波罗配置 Polaris.Polaris.public
# 盘古元数据库配置 jdbc:postgresql://172.21.4.32:5432/metadata20250421
# Metadata_Dbn_ip
METADATA_DB_IP = "172.21.4.32"
# Metadata_Dbn_dbPort
METADATA_DB_PORT = 5432
# Metadata_Dbn_dbUser
METADATA_DB_USER = "metadata20250116"
# Metadata_Dbn_dbPassword
METADATA_DB_PASSWORD = "metadata_20250116"
# Metadata_Dbn_dbName
METADATA_DB_NAME = "metadata20250421"

# 盘古界面配置 pangu_web_ip
PANGU_WEB_IP = "172.16.113.100"
# 淘沙界面配置 Vmodel_ip
VMODEL_WEB_IP = "172.16.113.93"
# 淘沙业务库配置
# VmodelPgDbn_ip
VMODEL_DB_IP = "172.16.104.78"
# VmodelPgDbn_dbPort
VMODEL_DB_PORT = 5432
# VmodelPgDbn_dbUser
VMODEL_DB_USER = "cdas"
# VmodelPgDbn_dbPassword
VMODEL_DB_PASSWORD = "Cdas@123456"
# VmodelPgDbn_dbName
VMODEL_DB_NAME = "cdas"

print(
    f"当前运行日志级别: {ENV_LOG_LEVEL} "
    f"数据默认保留{ENV_DATA_EXPIRED_DAY}天, {__file__}"
)

# ENV_DB_MODE = "SQLITE"
# DIALECT = "sqlite"
# CHARSET = "UTF8"
# DB_NAME = "data_forge"
# DB_FILE = DB_NAME + ".db"
# DATABASE_FILE_PATH = DATABASE_PATH.joinpath(DB_FILE)
# SQLALCHEMY_URL = f"{DIALECT}:///{DATABASE_FILE_PATH}?mode=WAL&charset={CHARSET}"


ENV_DB_MODE = "POSTGRESQL"
DIALECT = "postgresql"
DRIVER = "psycopg2"
DB_HOST = os.getenv("INNER_DB_HOST", "172.16.150.178")
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

# 盘古配置
pangu_ip_port = "172.21.4.42:11018"
# 数据资产-数据资源目录
pangu_data_resource_dir_url = (
    f"https://{pangu_ip_port}/catalog/catalog/res/searchResourceManage"
)
# 数据资产-设置中心-资源管理(内部)
pangu_data_inner_resource_dir_url = (
    f"https://{pangu_ip_port}/catalog/catalog/data/getResourcePage"
)
pangu_entity_list_url = f"https://{pangu_ip_port}/catalog/catalog/query/getEntityList"
pangu_entity_detail_url = (
    f"https://{pangu_ip_port}/catalog/catalog/query/getEntityDetail"
)
pangu_data_sample_query_url = (
    f"https://{pangu_ip_port}/catalog/catalog/query/getDataBySql"
)

pangu_cookie = (
    "contextPath=/catalog; JSESSIONID=212D9047AF5D54880D245EE23D92C371; "
    "contextPath=/; citycode=330100; appId=pangu; topoptid=pangu; "
    "JSESSIONID=8CE476D6DFFC4A1DEEEC90D89199E76D; "
    "userToken=fc661ef848c8490ca04f65f94bbd4d03; "
    "appToken=d3ec1cb3323440f7976b28f487ba6425; "
    "loginIp=10.0.23.57; loginMac=A4-BB-6D-43-BE-0D"
)

pangu_field_type_map = {
    -1: "string",
    1: "string",
    2: "int",
    3: "byte",
    4: "long",
    5: "short",
    6: "double",
    7: "decimal",
    9: "date",
    10: "timestamp",
    11: "binary",
    18: "float",
    20: "array",
    21: "array<string>",
    22: "array<int>",
    23: "array<long>",
    24: "array<float>",
}

DG_PLAN_CONFIG_PREFIX = "dg_task_plan_"
SQL_MODE_DG_PLAN_CONFIG_PREFIX = "sql_dg_task_plan_"

DG_HEADERS = {"USER_PROVIDE_IP": "10.0.23.57"}
