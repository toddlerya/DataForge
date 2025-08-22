#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/20 10:20 
# @Author   : guoqun X2590
# @FileName : trans_unicode.py
# @Project  : DataForge

# rule_str = """{"col":21,"category":"当前时间绝对秒","name":"","ename":"DISC_TIME","cname":"发现时间","preview":"score: 0, reason: 该字段存储的是Unix时间戳，表示从1970年1月1日00:00:00 UTC到现在的秒数。","value":"","args":{}}"""
#
#
# print(rule_str.encode('unicode_escape').decode("utf-8"))

import uuid

from loguru import logger

from utils.log import TracedLogger, LogManager
from config import PROJECT_PATH
from common.initialization import setup_logging

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="DataForgeDataGenApp.log",
    file_log_level="TRACE",
)
setup_logging(log_config.get_config().get("handlers"))

traced_logger = TracedLogger()

trace_uuid = uuid.uuid4().hex

logger.info(f"trace_uuid: {trace_uuid} ")
logger.info(f"traced_logger obj id: {id(traced_logger)}")

token = traced_logger.set_trace_uuid(trace_uuid)
logger.info(f"token {token}")
logger.info(f"token type {type(token)} {token.var}")
logger.info(f"token var {token.var}")
logger.info(f"token var {token.var}")

# traced_logger.reset_trace_uuid(trace_token=token)
# logger.info("reset done")
traced_logger = TracedLogger()
logger.info(f"new traced_logger obj id: {id(traced_logger)}")
if traced_logger.get_trace_uuid() is None:
    logger.info("没有提供trace_uuid, 搞个新的")
    traced_logger.set_trace_uuid(uuid.uuid4().hex)
    logger.info("use new trace_uuid")

