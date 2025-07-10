#!/usr/bin/env python
# coding: utf-8
# @File    :   state.py
# @Time    :   2025/05/08 15:43:55
# @Author  :   toddlerya
# @Desc    :   None

from typing import (
    Annotated,
    ClassVar,
    Dict,
    List,
    Set,
    TypedDict,
)
from pathlib import Path

from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field, field_validator

from database_models.schema import TableRawFieldSchema, GenTableFieldSchema
from agent.dg_configs import DG_FIELD_CATEGORY_CONFIG


class DataGenUserIntentSchema(BaseModel):
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


class PydanticDataGeniusCategoryRecommendation(BaseModel):
    """
    用于定义LLM输出的结构，包含推荐的类别、置信度分数和推荐理由。
    """

    category: str = Field(description=f"推荐的类别名称，必须在允许的类别列表中。")
    score: int = Field(ge=0, le=100, description="置信度分数，0-100之间")
    reason: str = Field(description="推荐理由说明")

    # 类变量，存储允许的类别
    _allowed_categories: ClassVar[Set[str]] = None

    @classmethod
    def get_allowed_categories(cls) -> Set[str]:
        """获取允许的类别列表"""
        if cls._allowed_categories is None:
            all_categories = set()
            # 直接遍历字典列表，提取 category 字段
            for item in DG_FIELD_CATEGORY_CONFIG:
                if isinstance(item, dict) and "category" in item:
                    all_categories.add(item["category"])
            cls._allowed_categories = all_categories
        return cls._allowed_categories

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = cls.get_allowed_categories()
        if v not in allowed:
            raise ValueError(
                f"category '{v}' is not in allowed categories: {', '.join(sorted(allowed))}"
            )
        return v


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

    rule_name: str = Field(
        default="DataGenius规则配置名称json文件名",
        description="DataGenius规则配置名称json文件名",
    )
    type_: str = Field(
        default="规则",
        description="DataGenius 生成的模型类型",
    )
    rows: int = Field(1, gt=0, description="需要生成的数据条数")
    separator: str = Field(
        default="\t",
        description="生成数据的分隔符，默认为制表符 ('\t')。",
    )
    rules: List[PydanticDataGeniusRule] = Field(
        description="规则列表，表中的每个字段对应一个规则。"
    )
    output: str = Field(
        default="DataGenius规则配置输出文件名",
        description="DataGenius规则配置输出文件名",
    )
    model: str = Field(default="DataGenius模型名称", description="DataGenius模型名称")
    cols: int = Field(1, gt=0, description="需要生成的列数")


class DataGenState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_input: str
    session_id: str
    client_ip: str
    user_intent: DataGenUserIntentSchema
    human_intent_feedback: str
    table_metadata_array: list[TableMetadataSchema]
    table_metadata_error: list[str]
    pydantic_data_genius_plan: PydanticDataGeniusPlan
    data_genius_headers: dict
    create_data_genius_task_error: str
    query_data_genius_task_error: str
    data_genius_plan_task_id: str
    data_genius_plan_run_duration: str
    data_genius_plan_output_url: str
    data_genius_plan_output_filesize: str
    data_genius_plan_edit_url: str
    error_message: Annotated[List[AnyMessage], add_messages]
    max_retries: int


class DataGenSQLModeUserIntentSchema(BaseModel):
    sql: str = Field(..., min_length=15, description="SQL内容")
    data_count: int = Field(..., ge=1, description="期望数据条数")


class SQLModeFieldSchema(BaseModel):
    en_name: str = Field(..., min_length=1, description="字段英文名称")
    alias_name: str = Field("", description="字段别名")
    cn_name: str = Field("", description="字段注释")


class SQLModeTableInfoSchema(BaseModel):
    table_en_name: str = Field(
        description="表英文名称", alias="table_en_name", default=""
    )
    fields_info: List[SQLModeFieldSchema] = Field(
        description="字段信息", alias="fields_info", default=[]
    )


class SQLModeDataGenState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_input: str
    session_id: str
    client_ip: str
    user_intent: DataGenSQLModeUserIntentSchema
    human_intent_feedback: str
    table_info_error: str
    table_info_data: SQLModeTableInfoSchema
    pydantic_data_genius_plan: PydanticDataGeniusPlan
    data_genius_headers: dict
    create_data_genius_task_error: str
    query_data_genius_task_error: str
    data_genius_plan_task_id: str
    data_genius_plan_run_duration: str
    data_genius_plan_output_url: str
    data_genius_plan_output_filesize: str
    data_genius_plan_edit_url: str
    error_message: Annotated[List[AnyMessage], add_messages]
    max_retries: int


class TableGenUserIntentSchema(BaseModel):
    categories: List[str] = Field(
        ..., description="期望生成的表类别, 例如: 人员属性,上网行为,位置轨迹等"
    )
    table_number: int = Field(30, description="需要生成的表数量", le=500)
    table_field_col_min: int = Field(5, description="每个表的最小字段数量>=5", ge=5)
    table_field_col_max: int = Field(
        500, description="每个表的最大字段数量<=1000", le=500
    )


class GenSourceTableMetadataSchema(BaseModel):
    table_en_name: str = Field(description="表英文名称", default="")
    table_cn_name: str = Field(description="表中文名称", default="")
    source_fields_info: List[GenTableFieldSchema] = Field(
        description="原始字段信息", default=[]
    )


class StructuredDimensionMappingSchema(BaseModel):
    recommend_category: str = Field(..., description="LLM推荐的表类别")
    recommend_dimension_table_en_name: str = Field(
        ..., description="LLM推荐的特征表英文名称"
    )
    recommend_reference_material_table_en_name_slice: List[str] = Field(
        ..., description="LLM推荐参考的素材表英文名", min_length=2, max_length=6
    )
    reference_material_table_en_name_slice: List[str] = Field(
        [], description="归一化后参考的素材表英文名", min_length=2, max_length=6
    )
    reference_material_table_metadata_slice: List[GenSourceTableMetadataSchema] = Field(
        [], description="参考的素材表字段信息", min_length=2, max_length=6
    )
    dimension_table_en_name: str = Field("", description="特征表英文名")
    dimension_table_cn_name: str = Field(..., description="特征表中文名")
    dimension_table_description: str = Field(..., description="特征表描述")
    reason: str = Field(description="推荐理由说明")
    score: int = Field(ge=0, le=100, description="置信度分数，0-100之间")


class StructuredTranslateTableEnameSchema(BaseModel):
    table_ename: str = Field(
        ..., description="表英文名称", pattern="^[A-Z][A-Z_]+[A-Z]$"
    )


class DimensionTableFieldsRecommendation(BaseModel):
    material_table_en_name: str = Field(default="", description="素材表英文名称")
    material_table_cn_name: str = Field(default="", description="素材表中文名称")
    field_en_name_slice: List[str] = Field(
        description=f"推荐的字段名称清单，必须在允许的字段列表中",
        min_length=5,
        max_length=500,
    )
    score: int = Field(ge=0, le=100, description="置信度分数，0-100之间")
    reason: str = Field(description="推荐理由说明")
    top_num: int = Field(description="推荐的TopN提示词参数")


class DimensionTableFillFieldResult(BaseModel):
    recommend_category: str = Field(..., description="LLM推荐的表类别")
    dimension_table_en_name: str = Field(..., description="特征表英文名")
    dimension_table_cn_name: str = Field(..., description="特征表中文名")
    dimension_table_fields_recommendations: List[DimensionTableFieldsRecommendation] = (
        Field(description="推荐结果")
    )
    dimension_table_fields: List[GenTableFieldSchema] = Field(
        description="特征表字段信息"
    )


class TableGenState(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    user_input: str
    session_id: str
    client_ip: str
    user_intent: TableGenUserIntentSchema
    human_intent_feedback: str
    material_table_groups: List[List[Dict]]
    mapping_dimension_table_info_slice: List[StructuredDimensionMappingSchema]
    dimension_table_config_slice: List[DimensionTableFillFieldResult]
    max_retries: int
    session_temp_data_path: Path
    create_session_temp_data_path_message: str
    session_archive_file_path: Path
    archive_message: str


if __name__ == "__main__":
    pdgcr = PydanticDataGeniusCategoryRecommendation(
        category="姓名", score=95, reason="根据姓名生成规则推测"
    )
    print(pdgcr)
