#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 16:24
# @Author   : guoqun X2590
# @FileName : models.py
# @Project  : DataForge


import datetime

from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.attributes import instance_dict

Base = declarative_base()


# @declarative_mixin
# class CommonTableArgsMixin:
#     """
#     公共表参数基础类
#     """

#     @declared_attr
#     def __table_args__(cls):
#         args = []
#         __args_map__ = {}
#         if cls.__dict__.get("__table_args_map__"):
#             __args_map__.update(cls.__table_args_map__)
#         if cls.__dict__.get("__table_args_array__"):
#             args.extend(cls.__table_args_array__)
#         args.append(__args_map__)
#         return tuple(args)


# @declarative_mixin
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


class ToDictMixin:
    """
    通用的 to_dict 混入类，为所有继承它的模型提供 to_dict 方法。
    自动排除 SQLAlchemy 的 _sa_instance_state，保留所有字段。
    """

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


class TableMetaDataInfo(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "table_meta_data_info"
    __table_args__ = (
        UniqueConstraint("uuid", name="uk_tb_meta"),
        {"comment": "表元数据信息"},
    )

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


class TableExampleDataInfo(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "table_example_data_info"
    __table_args__ = (
        UniqueConstraint("uuid", name="uk_tb_example"),
        {"comment": "表样例数据信息"},
    )
    uuid = Column(
        String(length=36), nullable=False, comment="数据唯一ID, md5(example_data)"
    )
    table_uuid = Column(
        String(length=36),
        nullable=False,
        comment="表唯一ID，md5(table_en_name+source+area_code+area_name)",
    )
    example_data = Column(JSON, nullable=True, comment="表样例数据")


class RecommendPanGuFieldInfo(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "recommend_pangu_field_info"
    __table_args__ = ({"comment": "盘古字段元数据推荐"},)

    ename = Column(
        String(length=512), default="", index=True, unique=True, comment="字段英文名称"
    )
    cname = Column(String(length=512), default="", comment="字段出现次数最多的中文名称")
    cname_count = Column(Integer, default=0, comment="该字段在所有表中的总数")
    cname_percentage = Column(
        Float, default=0.0, comment="字段出现次数最多的中文名称占字段总数的百分比"
    )
    identifier = Column(
        String(length=512), default="", comment="出现次数最多的数据项标识符"
    )
    identifier_count = Column(
        Integer, default=0, comment="最多的数据项标识符最多出现次数"
    )
    identifier_percentage = Column(
        Float, default=0.0, comment="出现次数最多的数据项标识符占比"
    )
    description = Column(
        Text, default="", comment="出现次数最多的字段描述，对应COMMENT"
    )
    description_count = Column(Integer, default=0, comment="字段描述出现最多次数")
    description_percentage = Column(
        Float, default=0.0, comment="出现最多次数字段描述占比"
    )
    field_type_name = Column(
        String(length=128), default="", comment="出现次数最多的字段类型"
    )
    field_type_count = Column(Integer, default=0, comment="字段类型出现次数")
    field_type_percentage = Column(Float, default=0.0, comment="字段类型出现次数占比")
    dictkey = Column(
        String(length=255),
        default="",
        comment="出现次数最多的字典关联ID及层级 "
        "关联字典表BASE_DD_TAB的PARENTID和NLEVEL 格式PARENTID:NLEVEL",
    )
    dictkey_count = Column(Integer, default=0, comment="字典关联ID及层级出现次数")
    dictkey_percentage = Column(
        Float, default=0.0, comment="字典关联ID及层级出现次数占比"
    )
    field_length = Column(
        String(length=128), default="", comment="出现次数最多的字段长度"
    )
    field_length_count = Column(Integer, default=0, comment="字段长度出现次数")
    field_length_percentage = Column(Float, default=0.0, comment="字段长度出现次数占比")
    element_code_name = Column(
        String(length=512), default="", comment="出现次数最多的数据元标示符名称"
    )
    element_code_count = Column(Integer, default=0, comment="数据元标示符名称出现次数")
    element_code_name_percentage = Column(
        Float, default=0.0, comment="数据元标示符名称出现次数占比"
    )
    determiner_code_name = Column(
        String(length=512), default="", comment="出现次数最多的限定词标示符"
    )
    determiner_code_count = Column(Integer, default=0, comment="限定词标示符出现次数")
    determiner_code_percentage = Column(
        Float, default=0.0, comment="限定词标示符出现次数占比"
    )
    structure_type = Column(
        Integer,
        default=0,
        comment="出现次数最多的字段结构化类型，0(默认)：结构化；1：非结构化",
    )
    structure_type_count = Column(Integer, default=0, comment="字段结构化类型出现次数")
    structure_type_percentage = Column(
        Float, default=0.0, comment="字段结构化类型出现次数占比"
    )
    is_multi_value = Column(
        Integer, default=0, comment="出现次数最多的是否是多值列 1：是；0：否"
    )
    is_multi_value_count = Column(Integer, default=0, comment="是否是多值列出现次数")
    is_multi_value_percentage = Column(
        Float, default=0.0, comment="是否是多值列出现次数占比"
    )
    is_required = Column(
        Integer, default=0, comment="出现次数最多的是否必填 1-必填 0-非必填"
    )
    is_required_count = Column(Integer, default=0, comment="是否必填出现次数")
    is_required_percentage = Column(Float, default=0.0, comment="是否必填出现次数占比")
    core_flag = Column(
        String(length=128),
        default="",
        comment="出现次数最多的是否核心字段  1-核心  0-普通",
    )
    core_flag_count = Column(Integer, default=0, comment="是否核心字段出现次数")
    core_flag_percentage = Column(
        Float, default=0.0, comment="是否核心字段出现次数占比"
    )
    example_data = Column(Text, nullable=True, comment="样例数据")


class PanGuDictInfo(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "pangu_dict_info"
    __table_args__ = (
        UniqueConstraint("uuid", name="uuid"),
        UniqueConstraint(
            "dictkey_with_nlevel", "uuid", name="dictkey_with_nlevel_uuid_unique"
        ),
        {"comment": "盘古字典"},
    )
    uuid = Column(BigInteger, nullable=False, comment="字典的唯一编码")
    dictkey_with_nlevel = Column(
        String(length=128), nullable=False, index=True, comment="字段存储的字典key"
    )
    dict_category_code = Column(
        String(length=128), nullable=False, comment="字典类别key"
    )
    dict_category = Column(String(length=384), nullable=False, comment="字典类别名称")
    dict_level = Column(Integer, nullable=False, comment="字典层级")
    dict_id = Column(String(length=128), nullable=False, comment="字典项编码")
    dict_name = Column(Text, nullable=False, comment="字典项名称")


class FieldDGRuleCache(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "field_dg_rule_cache"
    __table_args__ = (
        UniqueConstraint("uuid", name="uuid"),
        UniqueConstraint("ename", "uuid", name="ename_uuid_unique"),
        {"comment": "字段的DG规则配置缓存"},
    )
    uuid = Column(
        String(length=36),
        nullable=False,
        comment="规则唯一ID, md5(ename+cname+description+field_type_name)",
    )
    scope = Column(String(length=256), nullable=True, comment="领域")
    ename = Column(
        String(length=512), nullable=False, index=True, comment="字段英文名称"
    )
    cname = Column(String(length=512), default="", comment="字段出现次数最多的中文名称")
    description = Column(Text, default="", comment="字段描述")
    field_type_name = Column(String(length=128), default="", comment="字段类型")
    dg_rule = Column(JSON, nullable=False, comment="DG规则配置")
    example_data = Column(Text, nullable=True, comment="样例数据")
    ttl = Column(
        Integer, nullable=False, default=86400 * 7, comment="缓存规则过期时间，默认7天"
    )


class TaskInfo(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "task_info"
    __table_args__ = (
        UniqueConstraint("task_uuid", name="task_uuid_unique"),
        Index("idx_table_en_name", "table_en_name"),
        {"comment": "任务信息表"},
    )
    task_uuid = Column(
        String(length=36),
        nullable=False,
        comment="任务唯一ID, 与session_uuid, trace_uuid一致",
    )
    table_en_name = Column(
        String(length=128), nullable=False, default="", comment="表英文名称"
    )
    data_row_count = Column(Integer, default=0, comment="任务生成的数据条数")
    source = Column(String(length=64), default="", comment="数据来源")
    client_ip = Column(String(length=15), default="127.0.0.1", comment="客户端IP")
    task_payload = Column(JSONB, default=None, comment="创建任务请求的请求体JSON")
    rule_name = Column(String(length=56), default="", comment="任务规则名称")
    task_rule = Column(JSON, default=None, comment="任务规则配置JSON")
    dg_task_name = Column(String(length=128), default="", comment="DG的任务名称")
    dg_task_status = Column(Integer, default=-1, comment="0正常,1异常,-1未知")
    dg_task_id = Column(String(length=36), default="", comment="DG的任务ID")
    dg_task_edit_url = Column(Text, default="", comment="DG任务的编辑URL")
    dg_task_download_url = Column(Text, default="", comment="DG任务结果的下载URL")
    dg_task_duration = Column(Integer, default=-1, comment="DG任务耗时")
    user_modified_rules = Column(JSON, default=None, comment="用户修改的字段规则")


# class AIGenTableFieldInfo(CommonColumnMixin, ToDictMixin, Base):
#     __tablename__ = "ai_gen_table_field_info"
#     __table_args__ = (
#         {"comment": "AI生成仿真表信息"},
#         UniqueConstraint("uuid", name="uk_tb_meta"),
#     )

#     uuid = Column(
#         String(length=36),
#         nullable=False,
#         comment="表唯一ID, md5(table_en_name+source+area_code+area_name)",
#     )
#     table_en_name = Column(
#         String(length=128), nullable=False, default="", comment="表英文名称"
#     )
#     table_cn_name = Column(
#         String(length=256), nullable=False, default="", comment="表中文名称"
#     )
#     description = Column(Text, nullable=True, default="", comment="表描述")
#     position_type = Column(String(length=128), default="", comment="数据库类型")
#     table_fields = Column(JSON, nullable=False, comment="表字段信息")
#     source = Column(String(length=64), default="", comment="数据来源")


class EnvironmentInfo(CommonColumnMixin, ToDictMixin, Base):
    __tablename__ = "environment_info"
    __table_args__ = (
        UniqueConstraint("uuid", name="uk_environment"),
        {"comment": "环境信息"},
    )
    uuid = Column(
        String(length=36),
        nullable=False,
        comment="环境唯一ID, md5(apollo_web_ip+pangu_web_ip+vmodel_web_ip+metadata_db_ip+vmodel_db_ip)",  # noqa: E501
    )
    env_name = Column(
        String(length=32), nullable=False, default="未知", comment="环境信息"
    )
    apollo_web_ip = Column(String(length=64), nullable=True, comment="阿波罗界面IP")
    pangu_web_ip = Column(
        String(length=128), nullable=True, comment="盘古界面IP: pangu_web_ip"
    )
    metadata_db_ip = Column(
        String(length=64), nullable=True, comment="盘古元数据库IP: Metadata_Dbn_ip"
    )
    metadata_db_port = Column(
        Integer, nullable=True, comment="盘古元数据库端口: Metadata_Dbn_dbPort"
    )
    metadata_db_user = Column(
        String(length=128),
        nullable=True,
        comment="盘古元数据库用户名: Metadata_Dbn_dbUser",
    )
    metadata_db_password = Column(
        String(length=128),
        nullable=True,
        comment="盘古元数据库密码: Metadata_Dbn_dbPassword",
    )
    metadata_db_name = Column(
        String(length=128), nullable=True, comment="盘古数据库名称: Metadata_Dbn_dbName"
    )


if __name__ == "__main__":
    print(TableMetaDataInfo.__table_args__)
