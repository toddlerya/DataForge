#!/usr/bin/env python
# coding: utf-8
# @File    :   state.py
# @Time    :   2025/05/08 15:43:55
# @Author  :   toddlerya
# @Desc    :   None

from pathlib import Path
from typing import Annotated, ClassVar, Dict, List, Literal, Optional, Set, TypedDict

from langchain_core.messages import AnyMessage, BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, ConfigDict, Field, field_validator

from agent.dg_configs import DG_FIELD_CATEGORY_CONFIG
from database_models.schema import (
    GenTableFieldSchema,
    PydanticDataGeniusRule,
    RecommendPanGuDictSchema,
    TableRawFieldSchema,
    TaskDataSchema,
)


class DataGenUserIntentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    table_en_name: str = Field(..., description="表英文名称, 不可为空")
    data_count: int = Field(..., ge=1, description="期望数据条数")
    # TODO: 考虑让env_name是枚举类型，根据数据库信息动态更新
    env_name: str = Field(default="", description="环境名称")
    dont_run_dg_task: bool = Field(
        default=False, description="只进行AI推荐不创建DG任务"
    )


class TableMetadataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    table_en_name: str = Field(
        description="表英文名称", alias="table_en_name", default=""
    )
    table_cn_name: str = Field(
        description="表中文名称", alias="table_cn_name", default=""
    )
    raw_fields_info: List[TableRawFieldSchema] = Field(
        description="原始字段信息", alias="raw_fields_info", default=[]
    )
    source: str = Field(default="", description="来源")


class DGCategoryConfig:
    DG_FIELD_CATEGORY_CONFIG = DG_FIELD_CATEGORY_CONFIG


init_dg_category_config = DGCategoryConfig()


class PydanticDataGeniusCategoryRecommendation(BaseModel):
    """
    用于定义LLM输出的结构, 包含推荐的类别、置信度分数和推荐理由。
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    category: str = Field(description="推荐的类别名称，必须在允许的类别列表中。")
    score: int = Field(ge=0, le=100, description="置信度分数，0-100之间")
    reason: str = Field(description="推荐理由说明")

    # 类变量，存储允许的类别
    _allowed_categories: ClassVar[Optional[Set[str]]] = None

    @classmethod
    def get_allowed_categories(cls) -> Set[str]:
        """获取允许的类别列表"""
        if cls._allowed_categories is None:
            all_categories = set()
            # 直接遍历字典列表，提取 category 字段
            for item in init_dg_category_config.DG_FIELD_CATEGORY_CONFIG:
                if isinstance(item, dict) and "category" in item:
                    category = item["category"]
                    if isinstance(category, str):
                        all_categories.add(item["category"])
            cls._allowed_categories = all_categories
        return cls._allowed_categories

    @classmethod
    def reset_allowed_categories(cls):
        # 如果已经生成过实例了，需要调用此方法清空缓存更新
        cls._allowed_categories = None

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = cls.get_allowed_categories()
        if v not in allowed:
            raise ValueError(
                f"category '{v}' is not in allowed categories: "
                f"{', '.join(sorted(allowed))}"
            )
        return v


class PydanticDataGeniusPlan(BaseModel):
    """DataGenius 输出的计划 Pydantic模型"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

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


class CommonState(TypedDict):
    messages: Annotated[List[AnyMessage | BaseMessage], add_messages]
    session_id: str
    client_ip: str
    max_retries: int


# 基类：公共字段
class DataGenBaseState(CommonState):
    user_input: str
    human_intent_feedback: str
    table_metadata_info: TableMetadataSchema
    table_metadata_error: list[str]
    DG_FIELD_CATEGORY_CONFIG: list[dict[str, str]]
    table_dict_category_code_map: dict[str, str]
    table_dictkey_map: dict[str, list[RecommendPanGuDictSchema]]
    pydantic_data_genius_plan: PydanticDataGeniusPlan
    data_genius_headers: dict
    data_genius_task_id: str
    create_data_genius_task_error: str
    query_data_genius_task_error: str
    data_genius_plan_task_id: str
    data_genius_plan_run_duration: str
    data_genius_plan_output_url: str
    data_genius_plan_output_filesize: str
    data_genius_plan_edit_url: str
    error_message: Annotated[List[AnyMessage], add_messages]
    task_data: TaskDataSchema
    env_name: str


class DataGenState(DataGenBaseState):
    user_intent: DataGenUserIntentSchema
    pre_heat_mode: bool
    mode: Literal[1]
    dont_run_dg_task: bool


class DataGenSQLModeUserIntentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    sql: str = Field(..., min_length=15, description="SQL内容")
    data_count: int = Field(..., ge=1, description="期望数据条数")


class SQLModeFieldSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    en_name: str = Field(..., min_length=1, description="字段英文名称")
    alias_name: str = Field("", description="字段别名")
    comment: str = Field("", description="字段注释")


class SQLModeTableInfoSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    table_en_name: str = Field(
        description="表英文名称", alias="table_en_name", default=""
    )
    fields_info: List[SQLModeFieldSchema] = Field(
        description="字段信息", alias="fields_info", default=[]
    )


class SQLModeDataGenState(DataGenBaseState):
    user_intent: DataGenSQLModeUserIntentSchema
    table_info_error: str
    table_info_data: SQLModeTableInfoSchema
    mode: Literal[2]


class TableGenUserIntentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    categories: List[str] = Field(
        ..., description="期望生成的表类别, 例如: 人员属性,上网行为,位置轨迹等"
    )
    table_number: int = Field(30, description="需要生成的表数量", le=500)
    table_field_col_min: int = Field(5, description="每个表的最小字段数量>=5", ge=5)
    table_field_col_max: int = Field(
        500, description="每个表的最大字段数量<=1000", le=500
    )


class GenSourceTableMetadataSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    table_en_name: str = Field(description="表英文名称", default="")
    table_cn_name: str = Field(description="表中文名称", default="")
    source_fields_info: List[GenTableFieldSchema] = Field(
        description="原始字段信息", default=[]
    )


class StructuredDimensionMappingSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
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
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    table_ename: str = Field(
        ..., description="表英文名称", pattern="^[A-Z][A-Z_]+[A-Z]$"
    )


class DimensionTableFieldsRecommendation(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    material_table_en_name: str = Field(default="", description="素材表英文名称")
    material_table_cn_name: str = Field(default="", description="素材表中文名称")
    field_en_name_slice: List[str] = Field(
        description="推荐的字段名称清单，必须在允许的字段列表中",
        min_length=5,
        max_length=500,
    )
    score: int = Field(ge=0, le=100, description="置信度分数，0-100之间")
    reason: str = Field(description="推荐理由说明")
    top_num: int = Field(description="推荐的TopN提示词参数")


class DimensionTableFillFieldResult(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    recommend_category: str = Field(..., description="LLM推荐的表类别")
    dimension_table_en_name: str = Field(..., description="特征表英文名")
    dimension_table_cn_name: str = Field(..., description="特征表中文名")
    dimension_table_fields_recommendations: List[DimensionTableFieldsRecommendation] = (
        Field(description="推荐结果")
    )
    dimension_table_fields: List[GenTableFieldSchema] = Field(
        description="特征表字段信息"
    )


class TableGenState(CommonState):
    user_input: str
    user_intent: TableGenUserIntentSchema
    human_intent_feedback: str
    material_table_groups: List[List[Dict]]
    mapping_dimension_table_info_slice: List[StructuredDimensionMappingSchema]
    dimension_table_config_slice: List[DimensionTableFillFieldResult]
    session_temp_data_path: Path
    create_session_temp_data_path_message: str
    session_archive_file_path: Path
    archive_message: str


class ExploreState(CommonState):
    question: str
    tool_name: str
    tool_args: dict
    tool_call_result: str | list[str | dict]
    summarize_tool_call_result: list[dict]
    summary: str | list[str | dict]


class AppUserIntentSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    sub_graph_name: str = Field(
        ..., description="需要调用的子图的名称, 必须是已知的子图之一"
    )
    user_input: str = Field(..., description="用户意图输入文本")


class MainAppState(CommonState):
    user_intent: AppUserIntentSchema
    next_sub_graph_name: str
    user_input: str
    human_intent_feedback: str


if __name__ == "__main__":
    # 初始验证
    try:
        test1 = PydanticDataGeniusCategoryRecommendation(
            category="sports", score=90, reason="初始配置不包含 sports"
        )
        print(id(test1))
    except ValueError as e:
        print(
            "初始验证失败:", e
        )  # 输出: category 'sports' is not in allowed categories...

    # 动态更新配置
    init_dg_category_config.DG_FIELD_CATEGORY_CONFIG.append({"category": "sports"})
    PydanticDataGeniusCategoryRecommendation.reset_allowed_categories()

    # 再次验证
    try:
        instance = PydanticDataGeniusCategoryRecommendation(
            category="sports", score=90, reason="现在配置包含 sports"
        )
        print(id(instance))

        instance.category = "日期"
        print(id(instance))
        print("验证成功:", instance.category)  # 输出: sports
    except ValueError as e:
        print("验证失败:", e)

    print(hasattr(DataGenState, "metadata_gen"))
    print("metadata_gen" in DataGenState.__annotations__)
