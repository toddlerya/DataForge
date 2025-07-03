#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 15:07 
# @Author   : guoqun X2590
# @FileName : serve.py
# @Project  : DataForge


import logging
import os.path
import sys

from uvicorn import Config, Server
from chainlit.utils import mount_chainlit
from chainlit.cli import run_chainlit

from server.api.base import app
from utils.log import LogManager, logger
from config import ENV_LOG_LEVEL, ENV_PORT, PROJECT_PATH


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding loguru level if exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        # Find caller from where originated the loggerd message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(handlers: list):
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
    # requests禁用debug和info日志，不跟随业务日志级别，其中requests调用的是urllib3.connectionpool，因此设置这个日志级别即可
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)


class Serve:
    def __init__(self):
        self.log_config = LogManager(
            base_path=str(PROJECT_PATH.absolute()),
            log_path='server/log',
            log_name='DataForge.log',
            file_log_level=ENV_LOG_LEVEL,
            console_log_level=ENV_LOG_LEVEL
        ).get_config()

    def run(self):
        """
        启动API服务
        """
        api_server = Server(
            Config(
                app=app,
                host='0.0.0.0',
                port=int(ENV_PORT),
                workers=2
            )
        )
        setup_logging(self.log_config['handlers'])
        api_server.run()


if __name__ == '__main__':
    s = Serve()
    s.run()
