#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 15:07
# @Author   : guoqun X2590
# @FileName : serve.py
# @Project  : DataForge


from uvicorn import Config, Server

from common.initialization import setup_logging
from config import ENV_LOG_LEVEL, ENV_PORT, PROJECT_PATH
from server.api.base import app
from utils.log import LogManager


class Serve:
    def __init__(self):
        self.log_config = LogManager(
            base_path=str(PROJECT_PATH.absolute()),
            log_path="logs",
            log_name="DataForgeServer.log",
            file_log_level=ENV_LOG_LEVEL,
            console_log_level=ENV_LOG_LEVEL,
        ).get_config()

    def run(self):
        """
        启动API服务
        """
        api_server = Server(
            Config(app=app, host="0.0.0.0", port=int(ENV_PORT), workers=2)
        )
        setup_logging(self.log_config["handlers"])
        api_server.run()


if __name__ == "__main__":
    s = Serve()
    s.run()
