# coding: utf-8
# @Time:     2025/5/7 10:19
# @Author:   toddlerya
# @FileName: llm.py
# @Project:  DataForge

import os

from dotenv import load_dotenv
from langchain_ollama import ChatOllama

# 加载 .env 文件
load_dotenv()


ollama_llm = ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL"),
    # model="qwen3:0.6b-fp16",
    # model="qwen3:30b-a3b-thinking-2507-q4_K_M",
    model="qwen3:30b-a3b-instruct-2507-q4_K_M",
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
