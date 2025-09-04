#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/04 17:00
# @Author   : guoqun X2590
# @Desc     :


# scoped_session（作用域会话）
# 定义：
# scoped_session 是一个线程/上下文安全的会话管理器，它封装了 session_factory，
# 并自动在每个线程或上下文中维护一个唯一的 Session 实例。
# 特点：
# 基于 session_factory 构建。
# 提供线程/上下文隔离：每个线程或上下文只有一份 Session 实例。
# 自动管理 Session 的创建和销毁（通过 remove()）。
# 通常用于 Web 框架（如 Flask、FastAPI）中，避免在多线程中共享 Session。


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from config import (
    ENV_DB_MODE,
    SQLALCHEMY_AUTO_COMMIT,
    SQLALCHEMY_AUTO_FLUSH,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_URL,
)
from utils.log import logger


class DatabasebManager:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = SQLALCHEMY_URL,
        echo: bool = SQLALCHEMY_ECHO,
        auto_flush: bool = SQLALCHEMY_AUTO_FLUSH,
        auto_commit: bool = SQLALCHEMY_AUTO_COMMIT,
    ):
        if ENV_DB_MODE == "POSTGRESQL":
            self.db = PostgreSQLDB(
                url=url, echo=echo, auto_flush=auto_flush, auto_commit=auto_commit
            )
        elif ENV_DB_MODE == "MYSQL":
            self.db = MySQLDB(
                url=url, echo=echo, auto_flush=auto_flush, auto_commit=auto_commit
            )
        else:
            self.db = SQLiteDB(url=url, auto_flush=auto_flush, auto_commit=auto_commit)
        self.session = self.db.session


class SQLiteDB:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = "",
        auto_flush: bool = False,
        auto_commit: bool = True,
    ):
        """
        初始化sqlalchemy数据库对象化

        Args:
            url (str, optional): 数据库连接串. Defaults to None.
            echo (bool, optional): 是否打印SQL执行详情. Defaults to None.
            auto_flush (bool, optional): 是否自动flush. Defaults to None.
            auto_commit (bool, optional): 是否自动commit. Defaults to None.
        """
        # 启用Sqlite的WAL模式
        # QueuePool limit of size 20 overflow 10 reached, connection time out, timeout 30.00
        self.__engine = create_engine(
            url=url,
            future=True,
            pool_size=30,
            max_overflow=60,
            pool_timeout=30,
        )
        session_factory = sessionmaker(
            bind=self.__engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # 使用scoped_session 来创建会话管理者, 它接受一个 session_factory 作为参数
        # 默认的作用域是 thread-local
        self.session = scoped_session(session_factory)


class PostgreSQLDB:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = "",
        echo: bool = False,
        auto_flush: bool = False,
        auto_commit: bool = True,
    ):
        """
        初始化sqlalchemy数据库对象化

        Args:
            url (str, optional): 数据库连接串. Defaults to None.
            echo (bool, optional): 是否打印SQL执行详情. Defaults to None.
            auto_flush (bool, optional): 是否自动flush. Defaults to None.
            auto_commit (bool, optional): 是否自动commit. Defaults to None.
        """
        self.__engine = create_engine(url=url, echo=echo, future=True)
        # 创建一个session工厂
        session_factory = sessionmaker(
            bind=self.__engine, autoflush=auto_flush, autocommit=auto_commit
        )

        self.session = scoped_session(session_factory)


class MySQLDB:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = "",
        echo: bool = False,
        auto_flush: bool = False,
        auto_commit: bool = True,
    ):
        """
        初始化sqlalchemy数据库对象化

        Args:
            url (str, optional): 数据库连接串. Defaults to None.
            echo (bool, optional): 是否打印SQL执行详情. Defaults to None.
            auto_flush (bool, optional): 是否自动flush. Defaults to None.
            auto_commit (bool, optional): 是否自动commit. Defaults to None.
        """
        self.__engine = create_engine(url=url, echo=echo, future=True)
        session_factory = sessionmaker(
            bind=self.__engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # 使用scoped_session 来创建会话管理者, 它接受一个 session_factory 作为参数
        # 默认的作用域是 thread-local
        self.session = scoped_session(session_factory)
