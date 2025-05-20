tables_metadata = [
    {
        "name": "User",
        "fields": [
            {"name": "id", "type": "int", "required": True},
            {"name": "name", "type": "str", "required": True, "max_length": 50},
            {"name": "email", "type": "EmailStr", "required": True},
            {"name": "created_at", "type": "datetime", "required": False},
        ],
    },
    {
        "name": "Order",
        "fields": [
            {"name": "id", "type": "int", "required": True},
            {"name": "user_id", "type": "int", "required": True},
            {
                "name": "amount",
                "type": "Decimal",
                "required": True,
                "max_digits": 10,
                "decimal_places": 2,
            },
            {"name": "status", "type": "str", "required": False, "default": "pending"},
        ],
    },
]

FIELD_TYPE_MAP = {
    "int": int,
    "string": str,
}


from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import EmailStr, Field, create_model


def create_table_model(table_name: str, fields: list):
    field_definitions = {}
    for field in fields:
        field_name = field["en_name"]
        field_type = FIELD_TYPE_MAP.get(field["field_type"], str)
        field_kwargs = {}

        # 处理字段约束（如 max_length, max_digits 等）
        if "max_length" in field:
            field_kwargs["max_length"] = field["max_length"]
        if "max_digits" in field and "decimal_places" in field:
            field_kwargs["max_digits"] = field["max_digits"]
            field_kwargs["decimal_places"] = field["decimal_places"]

        field_definitions[field_name] = (field_type, Field(**field_kwargs))

    return create_model(table_name, **field_definitions)


def build_main_model(table_models: dict):
    main_model_fields = {
        table_name: (List[table_model], [])
        for table_name, table_model in table_models.items()
    }
    print(main_model_fields)
    return create_model("DomainDataResponse", **main_model_fields)


if __name__ == "__main__":

    from agent.mock_data import mock_tables_metadata

    # 动态生成所有表模型
    table_models = {
        table["name"]: create_table_model(table["name"], table["fields"])
        for table in mock_tables_metadata
    }

    # 构建主模型
    MainModel = build_main_model(table_models)
    # print(MainModel().model_dump())
    # print(MainModel.model_json_schema())
