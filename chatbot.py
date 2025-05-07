# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import os
import time
import uuid
import json

import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from agent.field_map_fill_agent.mapping_agent import mapping_graph


# 加载 .env 文件
load_dotenv()


os.environ["CHAINLIT_MAX_MESSAGE_SIZE"] = "10"  # 以MB为单位


@cl.on_chat_start
async def start_chat():
    # Store thread ID in user session for later use
    cl.user_session.set("thread_id", str(uuid.uuid4()))

    text_content = "目前支持的表为盘古或数据域管理的表."
    elements = [
        cl.Text(name="说明", content=text_content, display="inline")
    ]
    await cl.Message(content="你想构造的数据库表名是什么？", elements=elements).send()


@cl.step(type="tool", name="查询表元数据信息")
async def get_table_metadata(table_en_name: str) -> list:
    # 查询知识库获取表的字段配置信息
    await cl.sleep(2)
    # 模拟查询
    from agent.field_map_fill_agent.mock_data import MockTableMetadata

    if table_en_name.upper() in MockTableMetadata().__dir__():
        raw_fields_info = MockTableMetadata().__getattribute__(table_en_name.upper())
    else:
        raw_fields_info = ["未查询到该表的字段配置信息"]
    cl.user_session.set("raw_fields_info", raw_fields_info)
    return raw_fields_info


@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    logger.info(thread_id + ":" + message.content)
    thread = {"configurable": {"thread_id": thread_id}}
    if message.content.strip() == "正确":
        start_time = time.time()
        mapping_graph.update_state(
            thread, {"human_mapping_feedback": None}, as_node="human_feedback"
        )
        event = await cl.make_async(mapping_graph.invoke)(
            None, thread, stream_mode="values"
        )
        raw_fields_info = event.get("raw_fields_info", [])
        logger.info("完成")
        end_time = time.time()
        elapsed_time = end_time - start_time
        cost_msg = f"程序逻辑运行耗时: {elapsed_time:.2f} 秒"
        logger.info(cost_msg)
        await cl.Message(content="准备生成测试数据...").send()
    else:
        try:
            table_en_name = message.content.strip().upper()
            cl.user_session.set("table_en_name", table_en_name)
            raw_fields_info = await get_table_metadata(table_en_name)

            # 发送响应给用户
            if len(raw_fields_info) > 1:
                df = pd.DataFrame(raw_fields_info)[["ename", "name", "desc"]]
                elements = [cl.Dataframe(data=df, display="inline",
                                         name=f"{cl.user_session.get('table_en_name')}表字段信息")]
                await cl.Message(content=f"{cl.user_session.get('table_en_name')}表字段信息",
                                 elements=elements).send()
            else:
                await cl.Message(
                    content=f"# {cl.user_session.get('table_en_name')}表字段配置信息:\n"
                            f"{json.dumps(raw_fields_info, ensure_ascii=False, indent=2)}",
                    language="python",
                ).send()

            await cl.Message(
                content="上述表元数据信息是否正确？如果正确，请输入“正确”，即将开始数据生成任务。"
            ).send()

        except Exception as e:
            error_message = f"生成表字段配置信息时发生错误: {str(e)}"
            await cl.Message(content=error_message).send()
