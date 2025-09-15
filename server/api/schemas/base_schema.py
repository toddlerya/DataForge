#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 14:53
# @Author   : guoqun X2590
# @FileName : base_schema.py
# @Project  : DataForge


from typing import Any, Optional

from pydantic import BaseModel, Field

from utils.err_code import error_code


class ResponseBaseSchema(BaseModel):
    """响应体结构定义"""

    description: str = Field(..., description="描述信息")
    code: Optional[str] = Field(
        default=error_code.DEFAULT.get("code", ""), description="响应数据系统状态码"
    )
    message: Optional[str] = Field(
        default=error_code.DEFAULT.get("description", ""), description="错误信息"
    )
    data: Optional[Any] = Field(default=None, description="响应数据内容")
    session_id: Optional[str] = Field(default="", description="会话ID")
