#!/usr/bin/env python
# coding: utf-8
# @File    :   prompt_demo.py
# @Time    :   2025/06/03 16:35:58
# @Author  :   toddlerya
# @Desc    :   None

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

system_prompt = SystemMessagePromptTemplate.from_template(
    "你是一位{role}，请用{language}回答"
)
human_prompt = HumanMessagePromptTemplate.from_template("{query}")

chat_prompt = ChatPromptTemplate.from_messages([system_prompt, human_prompt])

# 使用示例
inputs = {"role": "律师", "language": "文言文", "query": "合同违约怎么办？"}
messages = chat_prompt.format_messages(**inputs)

print(messages)
