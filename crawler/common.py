#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/22 17:28 
# @Author   : guoqun X2590
# @FileName : common.py
# @Project  : DataForge


from typing import List, Dict

from database_models.schema import TableRawFieldSchema, TableMetaDataSchema
from database_models.sys_enum import MetaDataSource
from config import pangu_field_type_map


def table_metadata_verify2model(table_metadata_fields: List[Dict], source: str) -> TableMetaDataSchema:
    """
    元数据校验转换
    Args:
        table_metadata_fields:
        source:

    Returns:

    """
    table_fields_slice = list()
    for field in table_metadata_fields:
        if source == MetaDataSource.data_scope:
            field_model = TableRawFieldSchema(
                en_name=field.get("ename", ""),
                cn_name=field.get("name", ""),
                desc=field.get("description", ""),
                field_type=field.get("fieldType", "").lower(),
                dict_key=field.get("dictkey", "")
            )
            table_fields_slice.append(field_model)
        elif source == MetaDataSource.pangu:
            field_model = TableRawFieldSchema(
                en_name=field.get("ename", ""),
                cn_name=field.get("name", ""),
                desc=field.get("description", ""),
                field_type=pangu_field_type_map.get(field.get("fieldType", -1)),
                dict_key=field.get("dictkey", "")
            )
            table_fields_slice.append(field_model)
    table_metadata_model = TableMetaDataSchema(table_fields=table_fields_slice)
    return table_metadata_model