#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/20 10:20
# @Author   : guoqun X2590
# @FileName : trans_unicode.py
# @Project  : DataForge


import uuid

from loguru import logger

from common.initialization import setup_logging
from config import PROJECT_PATH
from utils.log import LogManager, TracedLogger

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="debug.log",
    file_log_level="TRACE",
)
setup_logging(log_config.get_config().get("handlers"))

traced_logger = TracedLogger()

trace_uuid = uuid.uuid4().hex

logger.info(f"trace_uuid: {trace_uuid} ")

token = traced_logger.set_trace_uuid(trace_uuid)


logger.info("start..")


@logger.catch
def danger():
    raise AttributeError("env_name不能为空")
    # x = 1 / 0


danger()

logger.info("end")
