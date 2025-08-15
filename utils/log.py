#!/usr/bin/env python
# coding: utf-8
# @File    :   log.py
# @Time    :   2023/04/13 13:57:32
# @Author  :   toddlerya
# @Desc    :   None

import logging
import pathlib
import sys
from typing import Optional
from contextvars import ContextVar, Token

from loguru import logger


# 创建上下文变量来存储trace_uuid
trace_context: ContextVar[Optional[str]] = ContextVar("trace_uuid", default=None)


class TraceFilter:
    """
    为loguru添加trace_uuid的过滤器
    """
    def __call__(self, record):
        trace_uuid = trace_context.get()
        record["extra"]["trace_uuid"] = trace_uuid or "NO_TRACE"
        return record


class InterceptHandler(logging.Handler):
    """
    拦截标准库logging的handler，转发给loguru
    """
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

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class LogManager:
    def __init__(
        self,
        base_path,
        log_path,
        log_name,
        log_format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | "
                   "<yellow>[{extra[trace_uuid]}]</yellow>  | <cyan>{module} {function}:{line}</cyan> - <level>{message}</level>",
        file_log_level="INFO",
        console_log_level="INFO",
        rotation="32 MB",
        compression="zip",
        log_encode="utf-8",
        enqueue=True,
    ):
        """
        初始化logger参数

        Args:
            base_path (str): 日志目录的基础目录, 可以是项目根目录, **绝对路径**
            log_path (str): 存放日志文件的目录, 举个例子, 可以设置为logs,  `base_path` 的相对子级路径
            log_name (str): 日志文件的名称, 比如task.log
            log_format (str, optional): 日志内容的格式默认为. Defaults to "{time:YYYY-MM-DD HH:mm:ss} {module} {function} {level} {message} {line}"
            file_log_level (str, optional): 文件日志的级别. Defaults to "INFO".
            console_log_level (str, optional): 终端窗口日志的级别. Defaults to "INFO".
            rotation (str, optional): 日志的回转分卷配置. Defaults to "32 MB".
            compression (str, optional): 历史日志压缩格式, 以降低存储空间. Defaults to "zip".
            log_encode (str, optional): 日志的编码格式. Defaults to "utf-8".
            enqueue (bool, optional): 多线程安全设置. Defaults to True.
        """
        # 创建日志目录
        log_dir = pathlib.Path(base_path).joinpath(log_path)
        log_dir.mkdir(parents=True, exist_ok=True)

        self.__config = {
            "handlers": [
                {
                    "sink": log_dir.joinpath(log_name),
                    "colorize": False,
                    "format": log_format,
                    "level": file_log_level,
                    "rotation": rotation,
                    "compression": compression,
                    "enqueue": enqueue,
                    "encoding": log_encode,
                    "filter": TraceFilter(),
                },
                {
                    "sink": sys.stdout,
                    "format": log_format,
                    "colorize": True,
                    "level": console_log_level,
                    "enqueue": enqueue,
                    "filter": TraceFilter(),
                },
            ]
        }
        logger.configure(**self.__config)

    def get_config(self):
        """获取logger参数"""
        return self.__config


class TracedLogger:
    """
    封装logger类，提供更便捷的日志追踪方法
    """
    @staticmethod
    def info(message: str, **kwargs):
        logger.info(message, **kwargs)

    @staticmethod
    def error(message: str, **kwargs):
        logger.error(message, **kwargs)

    @staticmethod
    def warning(message: str, **kwargs):
        logger.warning(message, **kwargs)

    @staticmethod
    def debug(message: str, **kwargs):
        logger.debug(message, **kwargs)

    @staticmethod
    def trace(message: str, **kwargs):
        logger.trace(message, **kwargs)

    @staticmethod
    def get_trace_uuid() -> Optional[str]:
        """
        获取当前会话的trace_uuid
        Returns:

        """
        return trace_context.get()

    @staticmethod
    def set_trace_uuid(trace_uuid: str) -> Token:
        """
        手动设置trace_uuid 用于异步任务等场景
        Args:
            trace_uuid:

        Returns:

        """
        return trace_context.set(trace_uuid)

    @staticmethod
    def reset_trace_uuid(trace_token: Token):
        """
        清理上下文
        Returns:

        """
        return trace_context.reset(trace_token)
