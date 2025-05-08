# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import json
import os
import time
import uuid
from typing import List

import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from agent.intent_agent import intent_graph
from agent.state import TableRawFiled, UserIntentSchema

# 加载 .env 文件
load_dotenv()


os.environ["CHAINLIT_MAX_MESSAGE_SIZE"] = "10"  # 以MB为单位


@cl.on_chat_start
async def start_chat():

    if not cl.user_session.get("thread_id"):
        cl.user_session.set("thread_id", str(uuid.uuid4()))

    text_content = """目前支持的表为盘古或数据域管理的表。\n
请输入需要构造的表名称，期望的表字段约束条件，期望生成的数据条数。\n
====输入内容示例====\n
数据库表名称: \n1. adm_test\n2. ods_test\n
期望表约束条件: \n
1. adm_test: from_city_code != to_city_code and datetime = 20250508 and ods_test.phone = adm_test.phone\n
2. ods_test: idcard is not null and phone is not null\n
期望生成数据条数: \n
1. adm_test: 10
2. ods_test: 20"""
    elements = [cl.Text(name="说明", content=text_content, display="inline")]
    await cl.Message(content="请输入测试数据构造需求", elements=elements).send()


@cl.step(type="tool", name="查询表元数据信息")
async def get_table_metadata(table_en_name: str) -> List[TableRawFiled]:
    # 查询知识库获取表的字段配置信息
    # 模拟查询
    from agent.mock_data import MockTableMetadata

    await cl.sleep(2)
    if table_en_name.upper() in MockTableMetadata().__dir__():
        raw_fields_info = MockTableMetadata().__getattribute__(table_en_name.upper())
        raw_fields_data = [
            TableRawFiled(**ele).model_dump()
            for ele in raw_fields_info
            if isinstance(ele, dict)
        ]
    else:
        raw_fields_info = ["未查询到该表的字段配置信息"]
        raw_fields_data = [TableRawFiled().model_dump()]
    cl.user_session.set("raw_fields_data", raw_fields_data)
    return raw_fields_data


@cl.step(type="llm", name="意图分析")
async def input_intent_analyze(user_input: str, thread: dict) -> UserIntentSchema:
    # 调用大模型对用户输入信息进行意图识别拆解
    event = await cl.make_async(intent_graph.invoke)(
        {"user_input": user_input}, thread, stream_mode="values"
    )
    return event["user_intent"]


@cl.on_message
async def main(message: cl.Message):
    thread_id = cl.user_session.get("thread_id")
    logger.info(thread_id + ":" + message.content)
    thread = {"configurable": {"thread_id": thread_id}}

    if message.command == "Picture":
        # User is using the Picture command
        pass

    if message.content.strip() == "正确":
        start_time = time.time()
        intent_graph.update_state(thread, {"confirmed": True}, as_node="confirm")

        # 查询表的字段配置信息
        table_en_names = cl.user_session.get("user_intent").table_en_names
        for each_table_en_name in table_en_names:
            each_table_raw_fields_info = await get_table_metadata(each_table_en_name)
            if len(each_table_raw_fields_info) > 1:
                logger.debug(
                    f"each_table_raw_fields_info: {each_table_raw_fields_info}"
                )
                df = pd.DataFrame(each_table_raw_fields_info)[
                    ["cn_name", "en_name", "desc", "field_type"]
                ].rename(
                    columns={
                        "cn_name": "中文名称",
                        "en_name": "英文名称",
                        "desc": "描述",
                        "field_type": "字段类型",
                    }
                )
                elements = [
                    cl.Dataframe(
                        data=df,
                        display="inline",
                        name=f"{each_table_en_name}表字段信息",
                    )
                ]
                await cl.Message(
                    content=f"{each_table_en_name}表字段信息",
                    elements=elements,
                ).send()
            else:
                await cl.Message(
                    content=f"# {each_table_en_name}表字段配置信息:\n"
                    f"{json.dumps(each_table_raw_fields_info, ensure_ascii=False, indent=2)}",
                    language="python",
                ).send()
        # event = await cl.make_async(mapping_graph.invoke)(
        #     None, thread, stream_mode="values"
        # )
        # raw_fields_info = event.get("raw_fields_info", [])
        logger.info("完成")
        end_time = time.time()
        elapsed_time = end_time - start_time
        cost_msg = f"程序逻辑运行耗时: {elapsed_time:.2f} 秒"
        logger.info(cost_msg)
        await cl.Message(content="准备生成测试数据...").send()
    else:
        try:
            user_input = message.content.strip()
            cl.user_session.set("user_input", user_input)
            user_intent = await input_intent_analyze(user_input, thread)
            cl.user_session.set("user_intent", user_intent)
            await cl.Message(
                content=user_intent.model_dump_json(indent=2), language="python"
            ).send()
            # 发送响应给用户

            await cl.Message(
                content="上述意图识别结果是否正确？若不正确请调整输入信息再次尝试意图识别；若正确，请输入“正确”，将开始数据生成任务。"
            ).send()

        except Exception as e:
            error_message = f"意图分析异常: {e}"
            await cl.Message(content=error_message).send()
