# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import asyncio
import pathlib

import chainlit as cl

import pandas as pd
from dotenv import load_dotenv
from loguru import logger
from config import PROJECT_PATH

# 加载 .env 文件
load_dotenv(PROJECT_PATH.absolute())


@cl.on_chat_start
async def start_chat():
    print(cl.context.session)
    if hasattr(cl.context.session, "environ") and cl.context.session.environ:
        client_port_tuple = cl.context.session.environ.get("asgi.scope", {}).get("client")
        if client_port_tuple and len(client_port_tuple) == 2:
            logger.info(f"client_port_tuple: {client_port_tuple}")
            cl.user_session.set("client_ip", client_port_tuple[0])
    else:
        cl.user_session.set("client_ip", "127.0.0.1")

    text_content = f"""{cl.user_session.get('client_ip')}，您好"""
    await cl.Message(author="Assistant", content=text_content).send()


if __name__ == '__main__':
    from chainlit.cli import run_chainlit
    run_chainlit(__file__)