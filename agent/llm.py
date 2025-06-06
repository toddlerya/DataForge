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
    model="Qwen3-30B-A3B",
    # model="DeepSeek-R1-Distill-Qwen-14B-AWQ",
    # model="fiberhome-chat",
    # model="DeepSeek-R1-Distill-Qwen-32B",
    temperature=0.6,
    top_p=0.95,
)

ollama_llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    model="qwen3:0.6b-fp16",
    # model="qwen3:4b-q4_K_M",
    # model="qwen3:8b-q4_K_M",
    # model="qwen3:30b-a3b",
    # model="THUDM_GLM-Z1-9B-0414:Q6_K_L",
    temperature=0.6,
    top_p=0.95,
)

# local_ollama_llm = ChatOllama(
#     model="qwen3:0.6b-fp16",
#     temperature=0.0
# )

chat_llm = ollama_llm
