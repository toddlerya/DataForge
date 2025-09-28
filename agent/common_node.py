#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/26 14:38
# @Author   : guoqun X2590
# @Desc     : 公共的Node

from typing import Union

from loguru import logger

from agent.state import MetaModeDataGenState, SQLModeDataGenState, TableMetadataSchema
from config import DG_PLAN_PATH
from utils.file import save_dict2jl


def save_dg_plan2json(
    state: Union[MetaModeDataGenState, SQLModeDataGenState],
) -> Union[MetaModeDataGenState, SQLModeDataGenState]:
    """
    存储DG执行计划任务配置
    Args:
        state:

    Returns:

    """
    logger.info("存储DataGenius任务规则")
    pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
    table_metadata_info: TableMetadataSchema = state.get("table_metadata_info")
    if pydantic_data_genius_plan:
        data = pydantic_data_genius_plan.model_dump()
        save_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}.json"
        ).absolute()
        save_dict2jl(json_data=data, save_path=str(save_json_path))
    if table_metadata_info:
        table_metadata_json_path = DG_PLAN_PATH.joinpath(
            f"{pydantic_data_genius_plan.rule_name}_table_metadata.json"
        )
        save_dict2jl(
            json_data=table_metadata_info.model_dump(),
            save_path=table_metadata_json_path,
        )
    return state
