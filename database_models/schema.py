#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 16:41 
# @Author   : guoqun X2590
# @FileName : schema.py
# @Project  : DataForge

from pydantic import BaseModel, Field


class TableRawFieldSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    en_name: str = Field(default="", description="字段英文名称")
    cn_name: str = Field(default="", description="字段中文名称")
    desc: str = Field(default="", description="字段描述")
    field_type: str = Field(default="", description="字段类型")
    dict_key: str = Field(default="", description="字典")
    example: str = Field(default="", description="数据样例")


class TableMetaDataSchema(BaseModel, extra="forbid", str_strip_whitespace=True):
    table_en_name: str = Field(description="表英文名称", default="")
    table_cn_name: str = Field(description="表中文名称", default="")
    description: str = Field("", description="表描述")
    table_fields: list[TableRawFieldSchema] = Field(..., description="表字段信息")
    position_type: str = Field("", description="数据库类型")
    storage_type: str = Field("", description="表数据格式")
    area_code: str = Field("", description="地市来源")
    source: str = Field("", description="数据来源")
