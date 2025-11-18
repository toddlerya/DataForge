#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/15 15:31
# @Author   : guoqun X2590
# @FileName : llm_util.py
# @Project  : PreviewDataForge


import os
import time

from pydantic import BaseModel, Field
from langfuse import Langfuse
from langfuse.callback import CallbackHandler

# from langfuse.openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from utils.model_config import (
    Plan_Qwen2_5_Coder_32B,
    Dev_Qwen2_5_14B_Instruct_AWQ,
    Plan_Qwen_QwQ_32B,
    Test_DeepSeek_R1_Distill_Qwen_14B_AWQ,
    Dev_DeepSeek_R1_Distill_Qwen_32B,
    Test_QWen3_8b_q4_K_M,
    Test_QWen3_4b_q4_K_M,
)

os.environ["LANGFUSE_PUBLIC_KEY"] = "pk-lf-c1da7bf3-4e74-4dc6-9943-49e81326e5b1"
os.environ["LANGFUSE_SECRET_KEY"] = "sk-lf-6fad7b5e-830f-4f92-9dc1-382b26d94b49"
os.environ["LANGFUSE_HOST"] = "http://172.16.108.3:3000"

# Initialize Langfuse client
langfuse = Langfuse(
    public_key="pk-lf-c1da7bf3-4e74-4dc6-9943-49e81326e5b1",
    secret_key="sk-lf-6fad7b5e-830f-4f92-9dc1-382b26d94b49",
    host="http://172.16.108.3:3000",
)
langfuse_handler = CallbackHandler()

model_config = Dev_DeepSeek_R1_Distill_Qwen_32B()

llm_client = ChatOpenAI(
    base_url=model_config.base_url,
    api_key=model_config.auth_key,
    model=model_config.model,
    temperature=model_config.temperature,
)


class Joke(BaseModel):
    title: str = Field(description="标题")
    content: str = Field(description="内容")
    desc: str = Field(description="笑点解析")


if __name__ == "__main__":
    llm_client = ChatOpenAI(
        base_url=model_config.base_url,
        api_key=model_config.auth_key,
        model=model_config.model,
        temperature=model_config.temperature,
    )
    structured_llm = llm_client.with_structured_output(Joke)
    joke = structured_llm.invoke(
        [HumanMessage(content="讲个200字的冷笑话，并分析笑点.")]
    )
    print(joke)
