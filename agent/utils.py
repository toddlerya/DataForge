#!/usr/bin/env python
# coding: utf-8
# @File    :   utils.py
# @Time    :   2025/05/09 15:23:17
# @Author  :   toddlerya
# @Desc    :   None

import json
from typing import Any

import aiofiles
from pydantic import BaseModel, create_model


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
