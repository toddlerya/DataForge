# coding: utf-8
# @Time:     2025/5/7 10:19
# @Author:   toddlerya
# @FileName: llm.py
# @Project:  DataForge

import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

# 加载 .env 文件
load_dotenv()

web_llm = ChatOpenAI(
    base_url=os.getenv("SILICONFLOW_BASE_URL"),
    api_key=os.getenv("SILICONFLOW_API_KEY"),
    # model="Qwen/Qwen3-8B",
    model="THUDM/GLM-4-9B-0414",
    # model="Qwen/Qwen3-235B-A22B",
    temperature=0,
)


ollama_llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL"), model="qwen3:8b-q4_K_M", temperature=0
)

chat_llm = web_llm
