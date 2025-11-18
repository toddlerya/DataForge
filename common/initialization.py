#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/8 16:42
# @Author   : guoqun X2590
# @FileName : initialization.py
# @Project  : DataForge

import logging
import sys

from config import (
    CONF_DATA_PATH,
    DG_PAYLOAD_PATH,
    DG_PLAN_PATH,
    ENV_LOG_LEVEL,
    FMDB_INSERT_SQL_PATH,
    GEN_TABLE_MODELS_DATA_PATH,
    GEN_TABLE_MODELS_TEMP_PATH,
    SAVE_DATA_PATH,
)
from utils.file import create_dir
from utils.log import InterceptHandler, logger


def setup_logging(handlers):
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(logging.getLevelName(ENV_LOG_LEVEL))
    # remove every other logger's handlers
    # and propagate a root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True
    # configure loguru
    logger.configure(handlers=handlers)
    # requests禁用debug和info日志，不跟随业务日志级别，
    # 其中requests调用的是urllib3.connectionpool，因此设置这个日志级别即可
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("apscheduler").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def init_env():
    """
    初始化运行环境
    Returns:

    """
    # 创建数据目录
    for path in [
        SAVE_DATA_PATH,
        DG_PLAN_PATH,
        DG_PAYLOAD_PATH,
        FMDB_INSERT_SQL_PATH,
        GEN_TABLE_MODELS_DATA_PATH,
        GEN_TABLE_MODELS_TEMP_PATH,
        CONF_DATA_PATH,
    ]:
        logger.info(f"创建所需目录: {path}")
        status, message = create_dir(str(path))
        if status is False:
            logger.error(message)
            sys.exit(1)


if __name__ == "__main__":
    init_env()
