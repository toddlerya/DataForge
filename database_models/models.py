#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 16:24
# @Author   : guoqun X2590
# @FileName : models.py
# @Project  : DataForge


import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    Integer,
    Float,
    String,
    Text,
    Boolean,
)
from sqlalchemy.orm import (
    declarative_base,
    declarative_mixin,
    declared_attr,
    relationship,
)
from sqlalchemy.orm.attributes import instance_dict
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


@declarative_mixin
class CommonTableArgsMixin:
    """
    公共表参数基础类
    """

    @declared_attr
    def __table_args__(cls):
        args = list()
        __args_map__ = {}
        if cls.__dict__.get("__table_args_map__"):
            __args_map__.update(cls.__table_args_map__)
        if cls.__dict__.get("__table_args_array__"):
            args.extend(cls.__table_args_array__)
        args.append(__args_map__)
        return tuple(args)


@declarative_mixin
class CommonColumnMixin:
    """
    公共字段基础类
    """

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键")
    remark = Column(Text, default="", comment="备注")
    create_time = Column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        comment="创建时间",
    )
    update_time = Column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        comment="更新时间",
    )


class TableMetaDataInfo(CommonTableArgsMixin, CommonColumnMixin, Base):
    __tablename__ = "table_meta_data_info"
    __table_args_map__ = {
        "comment": "表元数据信息",
    }
    __table_args_array__ = [UniqueConstraint("uuid", name="uk_tb_meta")]
    uuid = Column(
        String(length=36),
        nullable=False,
        comment="表唯一ID, md5(table_en_name+source+area_code+area_name)",
    )
    table_en_name = Column(
        String(length=128), nullable=False, default="", comment="表英文名称"
    )
    table_cn_name = Column(
        String(length=256), nullable=False, default="", comment="表中文名称"
    )
    description = Column(Text, nullable=True, default="", comment="表描述")
    position_type = Column(String(length=128), default="", comment="数据库类型")
    storage_type = Column(String(length=128), default="", comment="表数据格式")
    table_fields = Column(JSON, nullable=False, comment="表字段信息")
    area_code = Column(
        String(length=64), nullable=True, default="", comment="来源地市编码"
    )
    area_name = Column(
        String(length=64), nullable=True, default="", comment="来源地市名称"
    )
    source = Column(String(length=64), default="", comment="数据来源")

    def to_dict(self):
        """
        将 EnvironmentInfo 对象转换为字典

        Returns:
            dict: 字典表示的 EnvironmentInfo 对象
        """
        info_dict = instance_dict(self)
        if info_dict.get("_sa_instance_state", None):
            info_dict.pop("_sa_instance_state")
        return info_dict


class TableExampleDataInfo(CommonTableArgsMixin, CommonColumnMixin, Base):
    __tablename__ = "table_example_data_info"
    __table_args_map__ = {
        "comment": "表样例数据信息",
    }
    __table_args_array__ = [UniqueConstraint("uuid", name="uk_tb_example")]
    uuid = Column(
        String(length=36), nullable=False, comment="数据唯一ID, md5(example_data)"
    )
    table_uuid = Column(
        String(length=36),
        nullable=False,
        comment="表唯一ID，md5(table_en_name+source+area_code+area_name)",
    )
    example_data = Column(JSON, nullable=True, comment="表样例数据")


class EnvironmentInfo(CommonTableArgsMixin, CommonColumnMixin, Base):
    __tablename__ = "environment_info"
    __table_args_map__ = {
        "comment": "环境信息",
    }
    __table_args_array__ = [
        UniqueConstraint("uuid", name="uk_environment")
    ]
    uuid = Column(String(length=36), nullable=False,
                  comment="环境唯一ID, md5(apollo_web_ip+pangu_web_ip+vmodel_web_ip+metadata_db_ip+vmodel_db_ip)")
    env_name = Column(String(length=32), nullable=False, default="未知", comment="环境信息")
    apollo_web_ip = Column(String(length=64), nullable=True, comment="阿波罗界面IP")
    pangu_web_ip = Column(String(length=128), nullable=True, comment="盘古界面IP: pangu_web_ip")
    metadata_db_ip = Column(String(length=64), nullable=True, comment="盘古元数据库IP: Metadata_Dbn_ip")
    metadata_db_port = Column(Integer, nullable=True, comment="盘古元数据库端口: Metadata_Dbn_dbPort")
    metadata_db_user = Column(String(length=128), nullable=True, comment="盘古元数据库用户名: Metadata_Dbn_dbUser")
    metadata_db_password = Column(String(length=128), nullable=True,
                                  comment="盘古元数据库密码: Metadata_Dbn_dbPassword")
    metadata_db_name = Column(String(length=128), nullable=True, comment="盘古数据库名称: Metadata_Dbn_dbName")

    def to_dict(self):
        """
        将 EnvironmentInfo 对象转换为字典

        Returns:
            dict: 字典表示的 EnvironmentInfo 对象
        """
        info_dict = instance_dict(self)
        if info_dict.get("_sa_instance_state", None):
            info_dict.pop("_sa_instance_state")
        return info_dict
