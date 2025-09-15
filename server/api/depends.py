#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/22 17:13
# @Author   : guoqun X2590
# @FileName : depends.py.py
# @Project  : DataForge

import uuid

from fastapi import HTTPException
from loguru import logger

from config import (
    SQLALCHEMY_AUTO_COMMIT,
    SQLALCHEMY_AUTO_FLUSH,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_URL,
)
from utils.db import Database
from utils.db_manager import DatabaseManager
from utils.log import TracedLogger


@logger.catch(reraise=True)
def get_db():
    db = Database(
        url=SQLALCHEMY_URL,
        echo=SQLALCHEMY_ECHO,
        auto_flush=SQLALCHEMY_AUTO_FLUSH,
        auto_commit=SQLALCHEMY_AUTO_COMMIT,
    )
    try:
        yield db
    finally:
        db.session.close()


@logger.catch(reraise=True)
def get_db_manager():
    db_manager = DatabaseManager(
        url=SQLALCHEMY_URL,
        echo=SQLALCHEMY_ECHO,
        auto_flush=SQLALCHEMY_AUTO_FLUSH,
        auto_commit=SQLALCHEMY_AUTO_COMMIT,
    )
    try:
        yield db_manager
    finally:
        db_manager.close()


# 异步事务依赖项
async def get_transaction_logger():
    # 直接返回单例实例
    # yield TracedLogger()

    # 生成唯一的 trace_uuid
    trace_uuid = uuid.uuid4().hex
    token = TracedLogger.set_trace_uuid(trace_uuid)
    try:
        yield TracedLogger()
    except Exception as e:
        print(f"[ERROR] Transaction failed: {e}")
        raise HTTPException(status_code=500, detail="Transaction failed")
    finally:
        TracedLogger.reset_trace_uuid(token)
