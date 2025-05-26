#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/22 17:28 
# @Author   : guoqun X2590
# @FileName : common.py
# @Project  : DataForge


from typing import List, Dict

from loguru import logger

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
            try:
                field_model = TableRawFieldSchema(
                    en_name=field.get("ename", ""),
                    cn_name=field.get("name", ""),
                    desc=field.get("description", ""),
                    field_type=pangu_field_type_map.get(field.get("fieldType", -1)),
                    is_require=field.get("isRequire", 0),
                    dict_name=field.get("dic", "")
                )
            except Exception as err:
                logger.error(f"field: {field} ERROR: {err}")
                raise err
            else:
                table_fields_slice.append(field_model)
    table_metadata_model = TableMetaDataSchema(table_fields=table_fields_slice)
    return table_metadata_model


def fill_one_example2model(table_metadata_model: TableMetaDataSchema,
                           example_slice: List[Dict]) -> TableMetaDataSchema:
    """
    从给定的样例数据切片中获取样例数据填充模型对象
    Args:
        table_metadata_model:
        example_slice:

    Returns:

    """
    if example_slice is None:
        logger.warning(f"没有样例数据: {table_metadata_model.table_en_name}")
        return table_metadata_model
    example_one_data = {}
    # 遍历每条数据
    for example in example_slice:
        # 遍历每个键值对
        for key, value in example.items():
            # 检查key和value都是非空
            if key and value:
                # 补充数据
                if key not in example_one_data:
                    example_one_data[key.upper()] = value
        # 如果所有需要的键都有了值，则中断循环
        if len(example_one_data) == len(table_metadata_model.table_fields):
            logger.debug(f"example_one_data: {example_one_data}")
            break
    logger.trace(
        f"len(example_one_data)={len(example_one_data)} "
        f"len(table_metadata_model.table_fields)={len(table_metadata_model.table_fields)}")
    for index, field in enumerate(table_metadata_model.table_fields):
        example_value = example_one_data.get(field.en_name.upper(), "")
        field.example = example_value
        table_metadata_model.table_fields[index] = field
    return table_metadata_model
