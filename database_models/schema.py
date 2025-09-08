#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 16:41
# @Author   : guoqun X2590
# @FileName : schemas.py
# @Project  : DataForge

from typing import Any

from pydantic import BaseModel, Field


class TaskDataSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    task_uuid: str = Field(
        default="", description="任务唯一ID, 与session_uuid, trace_uuid一致"
    )
    table_en_name: str = Field(default="", description="表英文名称")
    data_row_count: int = Field(default=0, description="任务生成的数据条数")
    user_intent: dict = Field(default={}, description="用户意图")
    mode: int = Field(
        default=0, description="任务模式[0:未知 1: 元数据模式 2: SQL解析模式]"
    )
    client_ip: str = Field(default="127.0.0.1", description="客户端IP")
    task_payload: dict = Field(default={}, description="创建任务请求的请求体JSON")
    rule_name: str = Field(default="", description="任务规则名称")
    task_rule: list[dict[str, Any]] = Field(
        default=[{}], description="任务规则配置JSON"
    )
    dg_task_status: int = Field(
        default=-1, description="DG任务状态: 0正常,1异常,-1未知"
    )
    dg_task_message: str = Field(default="", description="DG任务状态信息")
    dg_task_id: str = Field(default="", description="DG的任务ID")
    dg_task_edit_url: str = Field(default="", description="DG任务的编辑URL")
    dg_task_rule_data_preview: list[dict] = Field(
        default=[{}], description="DG规则的预览数据"
    )
    dg_task_duration: str = Field(default="", description="DG任务耗时")
    user_modified_rules: dict = Field(default={}, description="用户修改的字段规则")
    env_uuid: str = Field("", description="环境UUID, 用于区分表元数据和字典等的版本")


class RecommendPanGuFieldSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    ename: str = Field(..., description="字段英文名称")
    cname: str = Field(..., description="字段出现次数最多的中文名称")
    cname_count: int = Field(0, description="该字段在所有表中的总数")
    cname_percentage: float = Field(
        0.0, description="字段出现次数最多的中文名称占字段总数的百分比"
    )
    identifier: str | None = Field("", description="出现次数最多的数据项标识符")
    identifier_count: int = Field(0, description="最多的数据项标识符最多出现次数")
    identifier_percentage: float = Field(
        0.0, description="出现次数最多的数据项标识符占比"
    )
    description: str | None = Field(
        "", description="出现次数最多的字段描述，对应COMMENT"
    )
    description_count: int = Field(0, description="字段描述出现最多次数")
    description_percentage: float = Field(0.0, description="出现最多次数字段描述占比")
    field_type_name: str = Field("", description="出现次数最多的字段类型")
    field_type_count: int = Field(0, description="字段类型出现次数")
    field_type_percentage: float = Field(0.0, description="字段类型出现次数占比")
    dictkey: str | None = Field(
        ":",
        description="出现次数最多的字典关联ID及层级 "
        "关联字典表BASE_DD_TAB的PARENTID和NLEVEL 格式PARENTID:NLEVEL",
    )
    dictkey_count: int = Field(0, description="字典关联ID及层级出现次数")
    dictkey_percentage: float = Field(0.0, description="字典关联ID及层级出现次数占比")
    field_length: str | None = Field("", description="出现次数最多的字段长度")
    field_length_count: int = Field(0, description="字段长度出现次数")
    field_length_percentage: float = Field(0.0, description="字段长度出现次数占比")
    element_code_name: str | None = Field(
        "", description="出现次数最多的数据元标示符名称"
    )
    element_code_count: int = Field(0, description="数据元标示符名称出现次数")
    element_code_name_percentage: float = Field(
        0.0, description="数据元标示符名称出现次数占比"
    )
    determiner_code_name: str | None = Field(
        "", description="出现次数最多的限定词标示符"
    )
    determiner_code_count: int = Field(0, description="限定词标示符出现次数")
    determiner_code_percentage: float = Field(
        0.0, description="限定词标示符出现次数占比"
    )
    structure_type: int | None = Field(
        0, description="出现次数最多的字段结构化类型，0(默认)：结构化；1：非结构化"
    )
    structure_type_count: int = Field(0, description="字段结构化类型出现次数")
    structure_type_percentage: float = Field(
        0.0, description="字段结构化类型出现次数占比"
    )
    is_multi_value: int | None = Field(
        0, description="出现次数最多的是否是多值列 1：是；0：否"
    )
    is_multi_value_count: int = Field(0, description="是否是多值列出现次数")
    is_multi_value_percentage: float = Field(
        0.0, description="是否是多值列出现次数占比"
    )
    is_required: int = Field(0, description="出现次数最多的是否必填 1-必填 0-非必填")
    is_required_count: int = Field(0, description="是否必填出现次数")
    is_required_percentage: float = Field(0.0, description="是否必填出现次数占比")
    core_flag: str = Field("", description="出现次数最多的是否核心字段  1-核心  0-普通")
    core_flag_count: int = Field(0, description="是否核心字段出现次数")
    core_flag_percentage: float = Field(0.0, description="是否核心字段出现次数占比")
    example_data: str | None = Field("", description="样例数据")
    env_uuid: str = Field("", description="环境UUID, 用于区分表元数据和字典等的版本")


class RecommendPanGuDictSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    uuid: int = Field(..., description="字典的唯一编码")
    dictkey_with_nlevel: str = Field(..., description="字段存储的字典key")
    dict_category_code: str = Field(..., description="字典类别key")
    dict_category: str = Field(..., description="字典类别名称")
    dict_level: int = Field(..., description="字典层级")
    dict_id: str = Field(..., description="字典项编码")
    dict_name: str = Field(..., description="字典项名称")
    env_uuid: str = Field("", description="环境UUID, 用于区分表元数据和字典等的版本")


class TableRawFieldSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    en_name: str = Field(default="", description="字段英文名称")
    cn_name: str = Field(default="", description="字段中文名称")
    desc: str = Field(default="", description="字段描述")
    field_type: str = Field(default="", description="字段类型")
    is_require: int = Field(default=0, description="是否必填")
    dict_key: str = Field(default="", description="字典编码")
    dict_name: str = Field(default="", description="字典名称")
    example: str | int | float = Field(default="", description="数据样例")


class GenTableFieldSchema(TableRawFieldSchema):
    source_table_en_name: str = Field(default="", description="来源表英文名")
    source_table_cn_name: str = Field(default="", description="来源表中文名")


class TableMetaDataSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    uuid: str = Field(
        default="",
        description="表的唯一ID: md5(table_en_name+source+area_code+area_name)",
    )
    table_en_name: str = Field(description="表英文名称", default="")
    table_cn_name: str = Field(description="表中文名称", default="")
    description: str = Field("", description="表描述")
    table_fields: list[TableRawFieldSchema] = Field(..., description="表字段信息")
    position_type: str = Field("", description="数据库类型")
    storage_type: str = Field("", description="表数据格式")
    area_code: str = Field("", description="地市来源编码")
    area_name: str = Field("", description="来源地市名称")
    source: str = Field("", description="数据来源")
    # env_uuid: str = Field("", description="环境UUID, 用于区分表元数据和字典等的版本")


class TableExampleSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    uuid: str = Field(..., description="数据唯一ID, md5(example_data)")
    table_uuid: str = Field(
        ..., description="表的唯一ID: md5(table_en_name+source+area_code+area_name)"
    )
    example_data: dict = Field(..., description="样例数据")
    env_uuid: str = Field("", description="环境UUID, 用于区分表元数据和字典等的版本")


class PydanticDataGeniusRule(BaseModel):
    """DataGenius 输出的规则 Pydantic模型"""

    col: int = Field(
        default=1,
        ge=1,
        description="字段在表中的列索引，从 0 开始计数。",
    )
    category: str = Field(
        default=...,
        description="规则类型，根据表的字段信息推测从指定的分类中选择。",
    )
    name: str = Field(..., description="规则名称")
    ename: str = Field(..., description="字段英文名称")
    cname: str = Field("", description="字段中文名称")
    preview: str = Field("", description="字段示例数据预览")
    value: str | int | float | list | dict = Field("", description="字段示例数据值")
    args: dict[str, str | list] = Field(
        default_factory=dict, description="规则参数字典，包含生成数据所需的参数。"
    )


class FieldDGRuleCacheSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    uuid: str = Field(
        ..., description="规则唯一ID, md5(ename+cname+description+field_type_name)"
    )
    ename: str = Field(..., description="字段英文名称")
    cname: str = Field(..., description="字段出现次数最多的中文名称")
    description: str = Field("", description="字段描述")
    field_type_name: str = Field(..., description="字段类型")
    dg_rule: PydanticDataGeniusRule = Field(..., description="DG规则配置")
    example_data: str = Field("", description="样例数据")
    ttl: int = Field(86400 * 7, description="缓存规则过期时间，默认7天")
