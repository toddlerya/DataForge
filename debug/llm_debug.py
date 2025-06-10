#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/7 11:36
# @Author   : guoqun X2590
# @FileName : llm_debug.py
# @Project  : DataForge


from pydantic import BaseModel, Field
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

model_config = Test_QWen3_4b_q4_K_M()

llm_client = ChatOpenAI(
    base_url=model_config.base_url,
    api_key=model_config.auth_key,
    model=model_config.model,
    temperature=model_config.temperature,
)


class Joke(BaseModel):
    title: str = Field(description="标题")
    author: str = Field(description="作者")
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
        [HumanMessage(content="讲个200字的冷笑话，要符合中国人的理解，并分析笑点.")]
    )
    print(joke)
    print(joke.model_dump_json())
