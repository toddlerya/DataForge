#!/usr/bin/env python
# coding: utf-8
# @File    :   state.py
# @Time    :   2025/05/08 15:43:55
# @Author  :   toddlerya
# @Desc    :   None

from enum import Enum
from typing import (
    Annotated,
    Any,
    Dict,
    List,
    Literal,
    LiteralString,
    Optional,
    TypedDict,
    Union,
)

from langchain_core.messages import ToolMessage
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from database_models.schema import TableRawFieldSchema
from faker_utils.dg_configs import DG_FIELD_CATEGORY_CONFIG


class UserIntentSchema(BaseModel):
    table_en_names: List[str] = Field(..., description="表英文名称, 不可为空")
    table_conditions: Dict[str, str] = Field(
        {},
        description="表字段的约束条件，key为表名，value为条件表达式字符串",
    )
    table_data_count: Dict[str, int] = Field(
        ...,
        description="表期望生成的数据条数，key为表名，value为正整数",
    )


class TableMetadataSchema(BaseModel):
    table_en_name: str = Field(
        description="表英文名称", alias="table_en_name", default=""
    )
    table_cn_name: str = Field(
        description="表中文名称", alias="table_cn_name", default=""
    )
    raw_fields_info: List[TableRawFieldSchema] = Field(
        description="原始字段信息", alias="raw_fields_info", default=[]
    )


class TableFieldDefintion(TypedDict):
    en_name: str
    cn_name: str
    # 字段类型, e.g., "INT", "VARCHAR", "DATE", "BOOLEAN"
    field_type: str
    # 字段样例值
    sample_value: str
    # 字段约束条件列表, e.g., ["age > 18", "name is not null"]
    constraints: List[str]


class FakerExecutionInstruction(TypedDict):
    field_en_name: str
    faker_provider: str
    faker_func: str
    faker_parameters: Dict[str, Any]
    is_nullable: bool
    null_probability: float
    dependencies: List[str]
    custom_logic_description: str
    string_format_template: Optional[str]


class FakerExecutionPlan(TypedDict):
    plan_description: str
    faker_locale: Optional[str]
    table_en_name: str
    row_count: int
    instructions_for_fields: List[FakerExecutionInstruction]


class DataForgeState(TypedDict):
    messages: Annotated[List[ToolMessage], add_messages]
    user_input: str
    user_intent: UserIntentSchema
    confirmed: bool
    table_metadata_array: list[TableMetadataSchema]
    input_table_definitions: List[TableFieldDefintion]
    llm_faker_plan: FakerExecutionPlan
    table_metadata_error: list[str]
    num_rows_to_generate: int
    fake_data: dict[str, list]
    error_message: Optional[str]
    current_retries: int
    max_retries: int


# Pydantic models for LLM output as defined in section 3.2.3
class PydanticFakerInstruction(BaseModel):
    """LLM 输出的单个字段Faker指令 Pydantic模型"""

    field_name: str = Field(description="需要生成数据的字段的英文名称。")
    faker_provider: str = Field(
        default="",
        description="要使用的 Python Faker provider (例如 'internet', 'address', 'ChineseIdCardProvider'。 没有需要映射的可以为空)。",
    )
    faker_func: str = Field(
        description="要使用的 Python Faker provider 方法 (例如 'pyint', 'name', 'address', 'date_between')。如果无法直接映射，则使用 'custom_logic'。"
    )
    faker_parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="传递给 Faker provider 方法的参数字典。例如：pyint 的 {'min_value': 0, 'max_value': 99}。对于 date_between，可使用 {'start_date': '-1y', 'end_date': 'today'}。",
    )
    is_nullable: bool = Field(
        default=False,
        description="该字段是否可以为 null。如果为 True，还需考虑 null_probability。",
    )
    null_probability: Optional[float] = Field(
        default=0.0,
        description="如果 is_nullable 为 True，则此字段生成 null 值的概率 (0.0 到 1.0)。",
    )
    dependencies: Optional[List[str]] = Field(
        default_factory=list,
        description="此字段生成所依赖的其他 field_name 列表 (用于复杂的字段间约束)。",
    )
    custom_logic_description: Optional[str] = Field(
        default=None,
        description="如果 Faker 无法通过 provider 和参数直接处理，则需要自定义逻辑或验证的自然语言描述。例如：'确保值是质数'，或 '结束日期必须在开始日期字段之后'。",
    )
    string_format_template: Optional[str] = Field(
        default=None,
        description="如果字段类型是字符串但需要特定格式 (例如 'ID-####')，请提供模板。使用 # 表示数字，? 表示字母。示例：'USER_??_####'。",
    )


class PydanticFakerPlan(BaseModel):
    """LLM 输出的Faker执行计划 Pydantic模型"""

    plan_description: str = Field(
        default="使用 Python Faker 生成伪造数据的执行计划。",
        description="此计划的简要描述。",
    )
    faker_locale: Optional[str] = Field(
        default=None,
        description="Faker 使用的区域设置，例如 'en_US', 'zh_CN'。如果可能，从输入上下文中确定。",
    )
    table_en_name: str = Field(..., description="表名称")
    row_count: int = Field(1, gt=0, description="需要生成的数据条数")
    instructions_for_fields: List[PydanticFakerInstruction] = Field(
        description="指令列表，表中的每个字段对应一个指令。"
    )


class PydanticDataGeniusCategoryRecommendation(BaseModel):
    """
    用于定义LLM输出的结构，包含推荐的类别、置信度分数和推荐理由。
    """

    category: str = Field(
        description="推荐的类别名称，必须是预定义 DG_FIELD_CATEGORY_CONFIG 中的 category 值之一"
    )
    score: int = Field(ge=0, le=100, description="置信度分数，0-100之间")
    reason: str = Field(description="推荐理由说明")

    @classmethod
    def allowed_categories(cls):
        all_category_values = set()
        for main_category_list in DG_FIELD_CATEGORY_CONFIG.values():
            for item in main_category_list:
                if "category" in item:
                    all_category_values.add(item["category"])
        return set(all_category_values)

    @classmethod
    def __get_validators__(cls):
        yield from super().__get_validators__()
        yield cls.validate_category

    @staticmethod
    def validate_category(value):
        allowed = PydanticDataGeniusCategoryRecommendation.allowed_categories()
        if value not in allowed:
            raise ValueError(
                f"category '{value}' is not in allowed categories: {allowed}"
            )
        return value


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
    value: str = Field("", description="字段示例数据值")
    args: Dict[str, str] = Field(
        default_factory=dict, description="规则参数字典，包含生成数据所需的参数。"
    )


class PydanticDataGeniusPlan(BaseModel):
    """DataGenius 输出的计划 Pydantic模型"""

    plan_description: str = Field(
        default="DataGenius 生成的伪造数据计划。",
        description="此计划的简要描述。",
    )
    type_: str = Field(
        default="自定义模型",
        description="DataGenius 生成的模型类型，固定为 '自定义模型'",
    )
    rows: int = Field(1, gt=0, description="需要生成的数据条数")
    separator: str = Field(
        default="\t",
        description="生成数据的分隔符，默认为制表符 ('\t')。",
    )
    table_en_name: str = Field(..., description="表名称")
    cols: int = Field(1, gt=0, description="需要生成的列数")
    rules: List[PydanticDataGeniusRule] = Field(
        description="规则列表，表中的每个字段对应一个规则。"
    )


if __name__ == "__main__":
    print(CategoryLiteral, type(CategoryLiteral))
