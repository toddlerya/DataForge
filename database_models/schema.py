#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 16:41
# @Author   : guoqun X2590
# @FileName : schemas.py
# @Project  : DataForge


from pydantic import BaseModel, Field


class RecommendPanGuFieldSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    ename: str = Field(..., description="字段英文名称")
    cname: str = Field(..., description="字段出现次数最多的中文名称")
    cname_count: int = Field(0, description="该字段在所有表中的总数")
    cname_percentage: float = Field(0.0, description="字段出现次数最多的中文名称占字段总数的百分比")
    identifier: str | None = Field("", description="出现次数最多的数据项标识符")
    identifier_count: int = Field(0, description="最多的数据项标识符最多出现次数")
    identifier_percentage: float = Field(0.0, description="出现次数最多的数据项标识符占比")
    description: str | None = Field("", description="出现次数最多的字段描述，对应COMMENT")
    description_count: int = Field(0, description="字段描述出现最多次数")
    description_percentage: float = Field(0.0, description="出现最多次数字段描述占比")
    field_type_name: str = Field("", description="出现次数最多的字段类型")
    field_type_count: int = Field(0, description_count="字段类型出现次数")
    field_type_percentage: float = Field(0.0, description_count="字段类型出现次数占比")
    dictkey: str | None = Field(":", description="出现次数最多的字典关联ID及层级 "
                                                 "关联字典表BASE_DD_TAB的PARENTID和NLEVEL 格式PARENTID:NLEVEL")
    dictkey_count: int = Field(0, description_count="字典关联ID及层级出现次数")
    dictkey_percentage: float = Field(0.0, description_count="字典关联ID及层级出现次数占比")
    field_length: str | None = Field("", description="出现次数最多的字段长度")
    field_length_count: int = Field(0, description_count="字段长度出现次数")
    field_length_percentage: float = Field(0.0, description_count="字段长度出现次数占比")
    element_code_name: str | None = Field("", description="出现次数最多的数据元标示符名称")
    element_code_count: int = Field(0, description_count="数据元标示符名称出现次数")
    element_code_name_percentage: float = Field(0.0, description_count="数据元标示符名称出现次数占比")
    determiner_code_name: str | None = Field("", description="出现次数最多的限定词标示符")
    determiner_code_count: int = Field(0, description_count="限定词标示符出现次数")
    determiner_code_percentage: float = Field(0.0, description_count="限定词标示符出现次数占比")
    structure_type: int | None = Field(0, description="出现次数最多的字段结构化类型，0(默认)：结构化；1：非结构化")
    structure_type_count: int = Field(0, description_count="字段结构化类型出现次数")
    structure_type_percentage: float = Field(0.0, description_count="字段结构化类型出现次数占比")
    is_multi_value: int | None = Field(0, description="出现次数最多的是否是多值列 1：是；0：否")
    is_multi_value_count: int = Field(0, description_count="是否是多值列出现次数")
    is_multi_value_percentage: float = Field(0.0, description_count="是否是多值列出现次数占比")
    is_required: int | None = Field(0, description="出现次数最多的是否必填 1-必填 0-非必填")
    is_required_count: int = Field(0, description_count="是否必填出现次数")
    is_required_percentage: float = Field(0.0, description_count="是否必填出现次数占比")
    core_flag: str = Field("", description="出现次数最多的是否核心字段  1-核心  0-普通")
    core_flag_count: int = Field(0, description_count="是否核心字段出现次数")
    core_flag_percentage: float = Field(0.0, description_count="是否核心字段出现次数占比")


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


class TableExampleSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    uuid: str = Field(..., description="数据唯一ID, md5(example_data)")
    table_uuid: str = Field(
        ..., description="表的唯一ID: md5(table_en_name+source+area_code+area_name)"
    )
    example_data: dict = Field(..., description="样例数据")
