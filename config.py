#!/usr/bin/env python
# coding: utf-8
# @File    :   config.py
# @Time    :   2023/11/3 18:30
# @Author  :   guo qun X2590
# @Desc    :   None


import os
import pathlib

ENV_LOG_LEVEL = os.getenv("TESTTOOLHUB_LOG_LEVEL", default="INFO")
ENV_SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", default=False)
ENV_HOST = os.getenv("TESTTOOLHUB_HOST", default="127.0.0.1")
ENV_PORT = os.getenv("TESTTOOLHUB_PORT", default=20211)
dev3_env = "172.16.112.99"
ENV_APOLLO_IP = os.getenv("APOLLO_WEB_IP", default=dev3_env)
ENV_APOLLO_WEB_PORT = os.getenv("APOLLO_WEB_PORT", default=8070)
ENV_DATA_EXPIRED_DAY = os.getenv("DATA_EXPIRED_DAY", 15)
try:
    ENV_DATA_EXPIRED_DAY = int(ENV_DATA_EXPIRED_DAY)
except ValueError as err:
    print(f"DATA_EXPIRED_DAY配置不是整数, 请确认, 使用默认值30. "
          f"current value: {ENV_DATA_EXPIRED_DAY} type: {type(ENV_DATA_EXPIRED_DAY)}")
    ENV_DATA_EXPIRED_DAY = 30

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

INPUT_DATA_PATH = PROJECT_PATH.joinpath("input_data").absolute()
STAGE_DATA_PATH = PROJECT_PATH.joinpath("stage_data").absolute()
TEMP_DATA_PATH = PROJECT_PATH.joinpath("temp").absolute()
SAVE_DATA_PATH = PROJECT_PATH.joinpath("data").absolute()
CONF_DATA_PATH = PROJECT_PATH.joinpath("conf").absolute()
DATABASE_PATH = PROJECT_PATH.joinpath("database").absolute()

TTH_CONFIG_PATH = CONF_DATA_PATH.joinpath("tth_config.yaml").absolute()
REGISTRY_CONFIG_PATH = CONF_DATA_PATH.joinpath("registry.yaml").absolute()
OMS_CONFIG_PATH = CONF_DATA_PATH.joinpath("oms_config.yaml").absolute()

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
# 盘古元数据库配置
# Metadata_Dbn_ip
METADATA_DB_IP = "172.16.113.102"
# Metadata_Dbn_dbPort
METADATA_DB_PORT = 5432
# Metadata_Dbn_dbUser
METADATA_DB_USER = "metadata"
# Metadata_Dbn_dbPassword
METADATA_DB_PASSWORD = "1qaz@2WSX3"
# Metadata_Dbn_dbName
METADATA_DB_NAME = "metadata"
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

print(f"当前运行日志级别: {ENV_LOG_LEVEL} 数据默认保留{ENV_DATA_EXPIRED_DAY}天")

ENV_DB_MODE = "SQLITE"
DIALECT = "sqlite"
CHARSET = "UTF8"
DB_NAME = "data_forge"
DB_FILE = DB_NAME + ".db"
DATABASE_FILE_PATH = DATABASE_PATH.joinpath(DB_FILE)
SQLALCHEMY_URL = f"{DIALECT}:///{DATABASE_FILE_PATH}?mode=WAL&charset={CHARSET}"
# SQLAlchemy Config
SQLALCHEMY_ECHO = ENV_SQLALCHEMY_ECHO
SQLALCHEMY_AUTO_FLUSH = True
SQLALCHEMY_AUTO_COMMIT = False

# API Config
API_PREFIX = "/api"

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/103.0.5060.53 Safari/537.36 PolarisInspection/1.0.0"
}

PROXIES = {"http": None, "https": None}
