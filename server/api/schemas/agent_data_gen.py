#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 11:18
# @Author   : guoqun X2590
# @FileName : agent_data_gen.py
# @Project  : DataForge


from pydantic import BaseModel, ConfigDict, Field


class InitDataGenSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    user_input: str = Field(..., min_length=10, description="用户输入数据生成任务需求")
    max_retries: int = Field(3, description="LLM最大生成重试次数")


class HumanIntentFeedBackSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    human_intent_feedback: str = Field(..., min_length=2, description="用户反馈")
    session_id: str = Field(..., description="会话ID")
