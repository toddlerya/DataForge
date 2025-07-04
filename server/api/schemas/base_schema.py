#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 14:53
# @Author   : guoqun X2590
# @FileName : base_schema.py
# @Project  : DataForge


from typing import Any

from pydantic import BaseModel, Field

from utils.err_code import error_code


class ResponseBaseSchema(BaseModel):
    """响应体结构定义"""

    description: str = Field(..., description="描述信息")
    code: str = Field(error_code.DEFAULT.get("code"), description="响应数据系统状态码")
    message: str = Field(error_code.DEFAULT.get("description"), description="错误信息")
    data: Any = Field(None, description="响应数据内容")
    session_id: str = Field("", description="会话ID")
