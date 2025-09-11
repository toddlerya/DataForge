#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/04 17:00
# @Author   : guoqun X2590
# @Desc     : 数据库管理器（支持 PostgreSQL / MySQL / SQLite），线程安全，
#             支持 with 语句（仅限单线程/非并发场景）


# scoped_session（作用域会话）
# 定义：
# scoped_session 是一个线程/上下文安全的会话管理器，它封装了 session_factory，
# 并自动在每个线程或上下文中维护一个唯一的 Session 实例。
# 特点：
# 基于 session_factory 构建。
# 提供线程/上下文隔离：每个线程或上下文只有一份 Session 实例。
# 自动管理 Session 的创建和销毁（通过 remove()）。
# 通常用于 Web 框架（如 Flask、FastAPI）中，避免在多线程中共享 Session。


import datetime
from typing import Any, Dict, List, Optional, Type

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy.orm.decl_api import DeclarativeBase
from sqlalchemy.schema import UniqueConstraint

from config import (
    ENV_DB_MODE,
    SQLALCHEMY_AUTO_COMMIT,
    SQLALCHEMY_AUTO_FLUSH,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_URL,
)
from utils.log import logger


class DatabaseManager:
    """
    数据库管理器：统一管理不同数据库的连接与会话
    支持 PostgreSQL / MySQL / SQLite
    使用 scoped_session 实现线程/上下文隔离
    """

    def __init__(
        self,
        url: str = SQLALCHEMY_URL,
        echo: bool = SQLALCHEMY_ECHO,
        auto_flush: bool = SQLALCHEMY_AUTO_FLUSH,
        auto_commit: bool = SQLALCHEMY_AUTO_COMMIT,
    ):
        if not url:
            raise ValueError("Database URL is required")
        if ENV_DB_MODE == "POSTGRESQL":
            self.db = PostgreSQLDB(
                url=url, echo=echo, auto_flush=auto_flush, auto_commit=auto_commit
            )
        elif ENV_DB_MODE == "MYSQL":
            self.db = MySQLDB(
                url=url, echo=echo, auto_flush=auto_flush, auto_commit=auto_commit
            )
        elif ENV_DB_MODE == "SQLITE":
            self.db = SQLiteDB(
                url=url, echo=echo, auto_flush=auto_flush, auto_commit=auto_commit
            )
        else:
            raise ValueError(f"Unsupported database mode: {ENV_DB_MODE}")

    def get_session(self):
        """获取当前上下文的 Session 实例（推荐使用方式）"""
        return self.db.session()

    def close(self):
        """关闭当前会话（不调用 remove, 由框架或业务逻辑管理）"""
        try:
            self.db.session.close()
            logger.info("Session closed")
        except Exception as err:
            logger.warning(f"Failed to close session: {err}")
        try:
            if hasattr(self.db, "_engine") and self.db._engine:
                self.db._engine.dispose()
                logger.info("Engine disposed")
        except Exception as err:
            logger.warning(f"Failed to dispose engine: {err}")

    def __enter__(self):
        """支持 with 语句（仅限单线程/非并发场景，不推荐在 Web 框架中使用）"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """with 退出时关闭会话"""
        self.close()


# ==================== 各数据库实现 ====================


class SQLiteDB:
    def __init__(
        self,
        url: str = "",
        echo: bool = False,
        auto_flush: bool = False,
        auto_commit: bool = True,
    ):
        # 启用Sqlite的WAL模式
        self._engine = create_engine(
            url=url,
            echo=echo,
            future=True,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            # 自动检测连接有效性
            pool_pre_ping=True,
            # SQLite多线程支持
            connect_args={"check_same_thread": False},
        )
        session_factory = sessionmaker(
            bind=self._engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # 使用scoped_session 来创建会话管理者, 它接受一个 session_factory 作为参数
        # 默认的作用域是 thread-local
        self.session = scoped_session(session_factory)

    def get_session(self):
        return self.session()


class PostgreSQLDB:
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
        self._engine = create_engine(
            url=url,
            echo=echo,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            # 每小时回收连接
            pool_recycle=3600,
        )
        # 创建一个session工厂
        session_factory = sessionmaker(
            bind=self._engine, autoflush=auto_flush, autocommit=auto_commit
        )
        # 使用scoped_session 来创建会话管理者, 它接受一个 session_factory 作为参数
        # 默认的作用域是 thread-local
        self.session = scoped_session(session_factory)

    def get_session(self):
        return self.session()


class MySQLDB:
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
        self._engine = create_engine(
            url=url,
            echo=echo,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        session_factory = sessionmaker(
            bind=self._engine, autoflush=auto_flush, autocommit=auto_commit
        )
        self.session = scoped_session(session_factory)

    def get_session(self):
        return self.session()


class GenericUpsert:
    def __init__(
        self, db: PostgreSQLDB | MySQLDB | SQLiteDB, updated_at: str = "update_time"
    ) -> None:
        self.db = db
        self.updated_at: str = updated_at
        self.session = db.get_session()
        self.db_dialect = self.db._engine.dialect.name
        # 缓存约束信息
        self._constraint_cache = {}

    def _deduplicate_constraints(self, constraints: List[List[str]]) -> List[List[str]]:
        """去除重复的约束定义"""
        seen = set()
        result = []

        for constraint in constraints:
            # 排序后转为元组用于去重
            constraint_tuple = tuple(sorted(constraint))
            if constraint_tuple not in seen:
                seen.add(constraint_tuple)
                result.append(constraint)

        return result

    def get_unique_constraints(
        self, model_class: Type[DeclarativeBase]
    ) -> List[List[str]]:
        """
        获取表的所有唯一约束

        Returns:
            List[List[str]]: 唯一约束列表，每个子列表包含构成一个唯一约束的列名
        """
        table = model_class.__table__
        table_name = table.name  # type: ignore

        # 检查缓存
        if table_name in self._constraint_cache:
            return self._constraint_cache[table_name]

        unique_constraints = []

        # 1. 收集主键约束
        if table.primary_key.columns:  # type: ignore
            pk_columns = [col.name for col in table.primary_key.columns]  # type: ignore
            unique_constraints.append(pk_columns)
            logger.trace(f"  🔑 主键约束: {pk_columns}")

        # 2. 收集单列unique=True约束
        for column in table.columns:
            if column.unique:
                unique_constraints.append([column.name])
                logger.trace(f"  🏷️ 单列唯一约束: [{column.name}]")

        # 3. 收集多列UniqueConstraint约束
        for constraint in table.constraints:  # type: ignore
            if isinstance(constraint, UniqueConstraint):
                constraint_columns = [col.name for col in constraint.columns]
                unique_constraints.append(constraint_columns)
                logger.trace(
                    f"  🔗 多列唯一约束: {constraint_columns} (名称: {constraint.name})"
                )

        # 4. 收集唯一索引
        for index in table.indexes:  # type: ignore
            if index.unique:
                index_columns = [col.name for col in index.columns]
                unique_constraints.append(index_columns)
                logger.trace(f"  📊 唯一索引: {index_columns} (名称: {index.name})")

        # 去重（可能存在重复的约束定义）
        unique_constraints = self._deduplicate_constraints(unique_constraints)

        # 缓存结果
        self._constraint_cache[table_name] = unique_constraints

        return unique_constraints

    def find_best_conflict_columns(
        self, model_class: Type[DeclarativeBase], data: Dict[str, Any]
    ) -> Optional[List[str]]:
        """
        根据提供的数据自动选择最佳的冲突检测列

        Args:
            model_class: SQLAlchemy模型类
            data: 要插入的数据

        Returns:
            最佳的冲突检测列，如果找不到合适的返回None
        """
        unique_constraints = self.get_unique_constraints(model_class)
        data_columns = set(data.keys())

        suitable_constraints = []

        for constraint in unique_constraints:
            constraint_set = set(constraint)
            # 检查数据中是否包含该约束的所有列
            if constraint_set.issubset(data_columns):
                # 检查所有约束列的值都不为None
                if all(data.get(col) is not None for col in constraint):
                    suitable_constraints.append(constraint)

        if not suitable_constraints:
            return None

        # 选择最佳约束：优先选择列数较少的约束
        best_constraint = min(suitable_constraints, key=len)
        logger.trace(f"  ✅ 自动选择冲突检测列: {best_constraint}")

        return best_constraint

    def smart_insert_or_update_single(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data: Dict[str, Any],
        conflict_columns: Optional[List[str]] = None,
        auto_detect: bool = True,
    ) -> Any:
        """
        智能的单条记录插入或更新

        Args:
            session: 数据库会话
            model_class: SQLAlchemy模型类
            data: 要插入或更新的数据
            conflict_columns: 手动指定的冲突检测列（优先级高于自动检测）
            auto_detect: 是否启用自动检测约束
        """
        table_name = model_class.__table__.name  # type: ignore
        logger.trace(f"\n📋 处理表 '{table_name}' 的数据: {data}")

        # 1. 如果没有手动指定conflict_columns且启用自动检测
        if conflict_columns is None and auto_detect:
            logger.trace(f"🔍 自动检测表 '{table_name}' 的唯一约束:")
            conflict_columns = self.find_best_conflict_columns(model_class, data)

            if conflict_columns is None:
                logger.trace("⚠️ 无法找到合适的唯一约束，回退到主键")
                conflict_columns = [
                    col.name
                    for col in model_class.__table__.primary_key.columns  # type: ignore
                ]

        # 2. 如果仍然没有conflict_columns，使用主键
        if conflict_columns is None:
            conflict_columns = [
                col.name
                for col in model_class.__table__.primary_key.columns  # type: ignore
            ]
            logger.trace(f"🔑 使用主键作为冲突检测: {conflict_columns}")

        # 3. 执行插入或更新
        return self._execute_upsert(session, model_class, data, conflict_columns)

    def _execute_upsert(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data: Dict[str, Any],
        conflict_columns: List[str],
    ) -> Any:
        """执行具体的UPSERT操作"""
        if self.db_dialect == "postgresql":
            return self._postgresql_smart_upsert(
                session, model_class, data, conflict_columns
            )
        elif self.db_dialect == "sqlite":
            return self._sqlite_smart_upsert(
                session, model_class, data, conflict_columns
            )
        else:
            return self._generic_smart_upsert(
                session, model_class, data, conflict_columns
            )

    def _postgresql_smart_upsert(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data: Dict[str, Any],
        conflict_columns: List[str],
    ) -> Any:
        """PostgreSQL智能UPSERT"""
        from sqlalchemy.dialects.postgresql import insert

        stmt = insert(model_class.__table__).values(**data)  # type: ignore

        update_dict = {
            key: stmt.excluded[key]
            for key in data.keys()
            if key not in conflict_columns
        }

        if hasattr(model_class, self.updated_at):
            update_dict[self.updated_at] = datetime.datetime.now()  # type: ignore

        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_dict
        ).returning(model_class.__table__)
        try:
            result = session.execute(stmt)
            row = result.fetchone()
            session.commit()
        except Exception as err:
            logger.error(err)
            session.rollback()

        return session.get(model_class, row._asdict().get("id"))  # type: ignore

    def _sqlite_smart_upsert(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data: Dict[str, Any],
        conflict_columns: List[str],
    ) -> Any:
        """SQLite智能UPSERT"""
        from sqlalchemy.dialects.sqlite import insert

        stmt = insert(model_class.__table__).values(**data)  # type: ignore

        update_dict = {key: stmt.excluded[key] for key in data.keys()}
        if hasattr(model_class, self.updated_at):
            update_dict[self.updated_at] = datetime.datetime.now()  # type: ignore

        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_dict
        )

        session.execute(stmt)
        session.commit()

        filter_conditions = {col: data[col] for col in conflict_columns if col in data}
        return session.query(model_class).filter_by(**filter_conditions).first()

    def _generic_smart_upsert(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data: Dict[str, Any],
        conflict_columns: List[str],
    ) -> Any:
        """通用智能UPSERT"""
        filter_conditions = {col: data[col] for col in conflict_columns if col in data}
        existing = session.query(model_class).filter_by(**filter_conditions).first()

        if existing:
            for key, value in data.items():
                if key not in conflict_columns:
                    setattr(existing, key, value)

            if hasattr(existing, "updated_at"):
                existing.updated_at = datetime.datetime.now()  # type: ignore

            session.commit()
            return existing
        else:
            new_instance = model_class(**data)
            session.add(new_instance)
            session.commit()
            return new_instance

    def batch_smart_insert_or_update(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data_list: List[Dict[str, Any]],
        conflict_columns: Optional[List[str]] = None,
        auto_detect: bool = True,
        batch_size: int = 1000,
    ) -> int:
        """
        智能批量插入或更新
        """
        if not data_list:
            return 0

        # 使用第一条记录检测约束
        if conflict_columns is None and auto_detect:
            conflict_columns = self.find_best_conflict_columns(
                model_class, data_list[0]
            )

        if conflict_columns is None:
            conflict_columns = [
                col.name
                for col in model_class.__table__.primary_key.columns  # type: ignore
            ]

        logger.trace(
            f"📦 批量处理 {len(data_list)} 条记录，使用约束: {conflict_columns}"
        )

        total_processed = 0
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i : i + batch_size]

            if self.db_dialect == "postgresql":
                total_processed += self._postgresql_batch_smart_upsert(
                    session, model_class, batch, conflict_columns
                )
            elif self.db_dialect == "sqlite":
                total_processed += self._sqlite_batch_smart_upsert(
                    session, model_class, batch, conflict_columns
                )
            else:
                for data in batch:
                    self._generic_smart_upsert(
                        session, model_class, data, conflict_columns
                    )
                total_processed += len(batch)

        return total_processed

    def _postgresql_batch_smart_upsert(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data_list: List[Dict[str, Any]],
        conflict_columns: List[str],
    ) -> int:
        """PostgreSQL批量智能UPSERT"""
        from sqlalchemy.dialects.postgresql import insert

        for data in data_list:
            if hasattr(model_class, "created_at") and "created_at" not in data:
                data["created_at"] = datetime.datetime.now(datetime.timezone.utc)
            if hasattr(model_class, self.updated_at) and "updated_at" not in data:
                data[self.updated_at] = datetime.datetime.now(datetime.timezone.utc)

        stmt = insert(model_class.__table__).values(data_list)  # type: ignore

        sample_data = data_list[0]
        update_dict = {
            key: stmt.excluded[key]
            for key in sample_data.keys()
            if key not in conflict_columns
        }

        if hasattr(model_class, self.updated_at):
            update_dict[self.updated_at] = datetime.datetime.now(datetime.timezone.utc)  # type: ignore

        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_dict
        )

        session.execute(stmt)
        session.commit()
        return len(data_list)

    def _sqlite_batch_smart_upsert(
        self,
        session: Session,
        model_class: Type[DeclarativeBase],
        data_list: List[Dict[str, Any]],
        conflict_columns: List[str],
    ) -> int:
        """SQLite批量智能UPSERT"""
        from sqlalchemy.dialects.sqlite import insert

        for data in data_list:
            if hasattr(model_class, "created_at") and "created_at" not in data:
                data["created_at"] = datetime.datetime.now(datetime.timezone.utc)
            if hasattr(model_class, self.updated_at) and "updated_at" not in data:
                data[self.updated_at] = datetime.datetime.now(datetime.timezone.utc)

        stmt = insert(model_class.__table__).values(data_list)  # type: ignore

        sample_data = data_list[0]
        update_dict = {key: stmt.excluded[key] for key in sample_data.keys()}
        update_dict[self.updated_at] = datetime.datetime.now(datetime.timezone.utc)  # type: ignore

        stmt = stmt.on_conflict_do_update(
            index_elements=conflict_columns, set_=update_dict
        )

        session.execute(stmt)
        session.commit()
        return len(data_list)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：直接使用
    db = DatabaseManager()
    session = db.get_session()
    try:
        # 执行数据库操作
        # session.execute("SELECT 1")
        # session.commit()
        logger.info("Database connected successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
    finally:
        db.close()
    # 示例：with 语句（仅限单线程）
    with DatabaseManager() as db:
        session = db.get_session()
        logger.info("Using with statement")
