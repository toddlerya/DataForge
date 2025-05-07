# coding: utf-8
# @Time:     2025/5/7 10:19
# @Author:   toddlerya
# @FileName: llm.py
# @Project:  DataForge


import os

from langchain_openai import ChatOpenAI

chat_llm = ChatOpenAI(
    base_url=os.getenv("SILICONFLOW_BASE_URL"),
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    model="Qwen/Qwen3-8B",
    # model="Qwen/Qwen3-235B-A22B",
    temperature=0,
)
