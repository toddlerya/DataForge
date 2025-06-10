#!/usr/bin/env python
# coding: utf-8
# @File    :   db.py
# @Time    :   2023/11/03 18:27:50
# @Author  :   toddlerya
# @Desc    :   None

from typing import Any

from sqlalchemy import ForeignKeyConstraint, Index, UniqueConstraint, create_engine
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql.schema import ColumnDefault

from config import (
    ENV_DB_MODE,
    SQLALCHEMY_AUTO_COMMIT,
    SQLALCHEMY_AUTO_FLUSH,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_URL,
)
from utils.log import logger


class Database:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = None,
        echo: bool = None,
        auto_flush: bool = None,
        auto_commit: bool = None,
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
            self.db = SQLiteDB(
                url=url, echo=echo, auto_flush=auto_flush, auto_commit=auto_commit
            )
        self.session = self.db.session

    def insert_or_update(self, model_name, **kwargs):
        """
        使用SQL的ON DUPLICATE KEY UPDATE语法

        Args:
            model_name (Any): 模型类名
        """
        if ENV_DB_MODE == "POSTGRESQL":
            PostgreSQLDB.insert_or_update(self, model_name=model_name, **kwargs)
        elif ENV_DB_MODE == "MYSQL":
            MySQLDB.insert_or_update(self, model_name=model_name, **kwargs)
        else:
            SQLiteDB.insert_or_update(self, model_name=model_name, **kwargs)


class SQLiteDB:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = None,
        echo: bool = None,
        auto_flush: bool = None,
        auto_commit: bool = None,
    ):
        """
        初始化sqlalchemy数据库对象化

        Args:
            url (str, optional): 数据库连接串. Defaults to None.
            echo (bool, optional): 是否打印SQL执行详情. Defaults to None.
            auto_flush (bool, optional): 是否自动flush. Defaults to None.
            auto_commit (bool, optional): 是否自动commit. Defaults to None.
        """
        if not url:
            url = SQLALCHEMY_URL
        if not echo:
            echo = SQLALCHEMY_ECHO
        if not auto_flush:
            auto_flush = SQLALCHEMY_AUTO_FLUSH
        if not auto_commit:
            auto_commit = SQLALCHEMY_AUTO_COMMIT
        # 启用Sqlite的WAL模式
        # QueuePool limit of size 20 overflow 10 reached, connection time out, timeout 30.00
        self.__engine = create_engine(
            url=url,
            echo=echo,
            future=True,
            pool_size=30,
            max_overflow=60,
            pool_timeout=30,
        )
        session_factory = sessionmaker(
            bind=self.__engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # self.session = session_factory()
        # https://farer.org/2017/10/28/sqlalchemy_scoped_session/
        self.session = scoped_session(session_factory)

    @logger.catch(reraise=True)
    def insert_or_update(self, model_name, **kwargs):
        """
        使用SQL的ON DUPLICATE KEY UPDATE语法
        https://stackoverflow.com/questions/6611563/sqlalchemy-on-duplicate-key-update
        Args:
            model_name (Any): 模型类名
        """
        if not kwargs:
            return
        insert_stmt = (
            sqlite.insert(getattr(model_name, "__table__"))
            .values(kwargs)
            .prefix_with("OR REPLACE")
        )
        logger.debug(f"sqlite insert_or_update insert_stmt => {insert_stmt}")
        # update_stmt = insert_stmt.on_duplicate_key_update(**kwargs)
        # insert_stmt = model_name().insert().values(**kwargs).prefix_with("OR REPLACE")
        self.session.execute(insert_stmt)


class MySQLDB:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = None,
        echo: bool = None,
        auto_flush: bool = None,
        auto_commit: bool = None,
    ):
        """
        初始化sqlalchemy数据库对象化

        Args:
            url (str, optional): 数据库连接串. Defaults to None.
            echo (bool, optional): 是否打印SQL执行详情. Defaults to None.
            auto_flush (bool, optional): 是否自动flush. Defaults to None.
            auto_commit (bool, optional): 是否自动commit. Defaults to None.
        """
        if not url:
            url = SQLALCHEMY_URL
        if not echo:
            echo = SQLALCHEMY_ECHO
        if not auto_flush:
            auto_flush = SQLALCHEMY_AUTO_FLUSH
        if not auto_commit:
            auto_commit = SQLALCHEMY_AUTO_COMMIT

        self.__engine = create_engine(url=url, echo=echo, future=True)
        session_factory = sessionmaker(
            bind=self.__engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # self.session = session_factory()
        # https://farer.org/2017/10/28/sqlalchemy_scoped_session/
        self.session = scoped_session(session_factory)

    @logger.catch(reraise=True)
    def insert_or_update(self, model_name, **kwargs):
        """
        使用SQL的ON DUPLICATE KEY UPDATE语法
        https://stackoverflow.com/questions/6611563/sqlalchemy-on-duplicate-key-update
        Args:
            model_name (Any): 模型类名
        """
        if not kwargs:
            return
        insert_stmt = mysql.insert(getattr(model_name, "__table__")).values(kwargs)
        update_stmt = insert_stmt.on_duplicate_key_update(**kwargs)
        self.session.execute(update_stmt)


class PostgreSQLDB:
    @logger.catch(reraise=True)
    def __init__(
        self,
        url: str = None,
        echo: bool = None,
        auto_flush: bool = None,
        auto_commit: bool = None,
    ):
        """
        初始化sqlalchemy数据库对象化

        Args:
            url (str, optional): 数据库连接串. Defaults to None.
            echo (bool, optional): 是否打印SQL执行详情. Defaults to None.
            auto_flush (bool, optional): 是否自动flush. Defaults to None.
            auto_commit (bool, optional): 是否自动commit. Defaults to None.
        """
        if not url:
            url = SQLALCHEMY_URL
        if not echo:
            echo = SQLALCHEMY_ECHO
        if not auto_flush:
            auto_flush = SQLALCHEMY_AUTO_FLUSH
        if not auto_commit:
            auto_commit = SQLALCHEMY_AUTO_COMMIT
        self.__engine = create_engine(
            url=url, echo=echo, future=True
        ).execution_options(isolation_level="AUTOCOMMIT")
        session_factory = sessionmaker(
            bind=self.__engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # self.session = session_factory()
        # https://farer.org/2017/10/28/sqlalchemy_scoped_session/
        self.session = scoped_session(session_factory)

    # @logger.catch(reraise=True)
    def insert_or_update(self, model_name, **kwargs):
        """
        使用SQL的CONFLICT (id) DO UPDATE 语法
        # https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#insert-update-returning
        Args:
            model_name (Any): 模型类名
        """
        if not kwargs:
            return
        # 找出所有的唯一键约束条件
        index_elements = list()
        model_dict = getattr(model_name, "__table__").__dict__
        for key, value in model_dict.items():
            if key == "constraints" or key == "indexes":
                for each in value:
                    if isinstance(each, UniqueConstraint):
                        for ele in each:
                            index_elements.append(ele.name)
                    if isinstance(each, Index):
                        for ele in each.expressions:
                            index_elements.append(ele.name)
                    if isinstance(each, ForeignKeyConstraint):
                        for column in each.table.columns:
                            # 找到onupdate列和值，补充到入参里
                            if column.onupdate and isinstance(
                                column.onupdate, ColumnDefault
                            ):
                                onupdate_arg = column.onupdate.arg
                                if column.onupdate.is_callable:
                                    kwargs[column.name] = getattr(
                                        onupdate_arg, "__wrapped__"
                                    )()
                                # 剩下的两种情况暂时没有用到，先不处理
                                elif column.onupdate.is_scalar:
                                    pass
                                elif column.onupdate.is_server_default:
                                    pass

        index_elements = list(set(index_elements))

        insert_stmt = postgresql.insert(getattr(model_name, "__table__")).values(kwargs)
        update_stmt = insert_stmt.on_conflict_do_update(
            index_elements=index_elements, set_=kwargs
        )
        self.session.execute(update_stmt)


def insert_or_update(db: Database, model_name: Any, record: dict) -> tuple[bool, str]:
    """
    封装插入或更新数据库操作

    Args:
        db (Database): _description_
        model_name (Any): _description_
        record (dict): _description_

    Returns:
        tuple[bool, str]: _description_
    """
    try:
        db.insert_or_update(model_name=model_name, **record)
    except Exception as err:
        db.session.rollback()
        message = f"数据库写操作错误: {err}"
        return False, message
    else:
        return True, "ok"
