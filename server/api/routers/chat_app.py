#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/3 16:56
# @Author   : guoqun X2590
# @FileName : chat_app.py
# @Project  : DataForge

from chainlit.cli import run_chainlit

import uuid
from typing import Optional

from fastapi import APIRouter, Request

from utils.log import logger
from server.api.schemas.base_schema import ResponseBaseSchema
from server.api.schemas.agent_data_gen import (
    InitDataGenSchema,
    HumanIntentFeedBackSchema,
)
from config import PROJECT_PATH
from agent.state import DataGenUserIntentSchema
from utils.err_code import error_code

router = APIRouter(
    prefix="/chat",
    tags=["数据生成", "chat"],
    responses={404: {"description": "ChatApp Not Found"}},
)


@router.get("/data_gen/{path:path}")
@router.post("/data_gen/{path:path}")
@router.websocket("/data_gen/{path:path}")
async def data_gen_app(path: str):
    return await run_chainlit(
        str(PROJECT_PATH.joinpath("app_data_gen", "chatbot.py").absolute())
    )


@router.get("/table_gen/{path:path}")
@router.post("/table_gen/{path:path}")
@router.websocket("/table_gen/{path:path}")
async def table_gen_app(path: str):
    return await run_chainlit(
        str(PROJECT_PATH.joinpath("app_table_gen", "app.py").absolute())
    )
