#!/usr/bin/env python
# coding: utf-8
# @File    :   utils.py
# @Time    :   2025/05/09 15:23:17
# @Author  :   toddlerya
# @Desc    :   None

import json
from typing import Any, List, Dict

import aiofiles
from pydantic import BaseModel, create_model, Field


async def save_json_data_async(save_json_path, fake_data):
    async with aiofiles.open(save_json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(fake_data, ensure_ascii=False, indent=2))


def create_model_from_dict(
    data: dict, model_name: str = "row_field_model"
) -> type[BaseModel]:
    # 构建字段注解
    annotations = {key: (Any, None) for key in data}
    model = create_model(
        model_name,
        **annotations,
    )
    return model


FIELD_TYPE_MAP = {"int": int, "string": str}


def create_table_model(table_name: str, fields: list[dict]):
    """
    创建输出表输出模型定义
    Args:
        table_name:
        fields:

    Returns:

    """
    field_definitions = {}
    for field in fields:
        field_name = field.get("en_name")
        field_type = FIELD_TYPE_MAP.get(field.get("field_type"), str)
        field_kwargs = {}

        field_definitions[field_name] = (field_type, Field(**field_kwargs))

    return create_model(table_name, **field_definitions)


def build_main_model(table_models: Dict[str, List[BaseModel]] | List):
    """
    构建输出数据结构主模型
    Args:
        table_models:

    Returns:

    """
    main_model_fields = {
        table_name: (List[table_model])
        for table_name, table_model in table_models.items()
    }
    return create_model("LLMOutputData", **main_model_fields)


if __name__ == "__main__":
    from pydantic import BaseModel

    data1 = {
        "CREATE_TIME": "",
        "LAST_TIME": "",
        "REGISTRANT": "",
    }

    data2 = {
        "MD_ID": "",
        "DOMAIN": "",
        "REGISTRY_DOMAIN_ID": "",
    }

    DynamicModel1 = create_model_from_dict(data1)
    print(DynamicModel1())
    print(DynamicModel1.model_json_schema())
    print(DynamicModel1.__annotations__)
