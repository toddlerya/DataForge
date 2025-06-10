# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import asyncio
import json
import pathlib
import uuid
from typing import List

import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from loguru import logger

from agent_v1.gen_faker_data_agent import gen_fake_data_graph
from agent_v1.intent_agent import intent_graph
from agent_v1.mapping_agent import mapping_graph
from agent_v1.state import TableMetadataSchema, UserIntentSchema
from agent_v1.utils import save_json_data_async

# 加载 .env 文件
load_dotenv()


@cl.on_chat_start
async def start_chat():
    if not cl.user_session.get("thread_id"):
        cl.user_session.set("thread_id", str(uuid.uuid4()))

    text_content = """您好！我是您的测试数据生成助手\n\n目前支持的表为盘古或数据域管理的表。\n
请输入需要构造的表名称，期望的表字段约束条件，期望生成的数据条数。\n
====输入内容示例====\n
数据库表名称 (必填):
ADM_DOMAIN_WHOIS
期望表约束条件 (可选):
ADM_DOMAIN_WHOIS: DOMAIN IS NOT NULL AND ADM_DOMAIN_WHOIS.DOMAIN = ODS_TC_DOMAIN_WHOIS.DOMAIN AND ADM_DOMAIN_WHOIS.LAST_TIME >= '2025-04-08'
期望生成数据条数 (必填):
ADM_DOMAIN_WHOIS: 5
"""
    elements = [cl.Text(name="说明", content=text_content, display="inline")]
    await cl.Message(content="请输入测试数据构造需求", elements=elements).send()


@cl.step(type="tool", name="查询表元数据信息")
async def get_table_metadata() -> List[TableMetadataSchema]:
    event = await cl.make_async(mapping_graph.invoke)(
        {
            "user_input": cl.user_session.get("user_input"),
            "user_intent": cl.user_session.get("user_intent"),
            "table_metadata_array": [],
            "table_metadata_error": [],
        },
        cl.user_session.get("thread"),
        stream_mode="values",
    )
    cl.user_session.set("table_metadata_array", event["table_metadata_array"])
    cl.user_session.set("table_metadata_error", event["table_metadata_error"])
    return event["table_metadata_array"]


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
    thread = {"configurable": {"thread_id": thread_id}, "recursion_limit": 50}
    cl.user_session.set("thread", thread)
    if message.content.strip() == "正确":
        await cl.Message(content="正在获取表元数据信息...").send()
        start_time = asyncio.get_event_loop().time()
        intent_graph.update_state(
            thread,
            {
                "confirmed": True,
                "table_metadata_array": [],
            },
            as_node="confirm",
        )
        # 查询表的字段配置信息
        table_metadata_array = await get_table_metadata()
        logger.trace(f"table_metadata_array: {table_metadata_array}")
        table_metadata_error = cl.user_session.get("table_metadata_error")
        if table_metadata_error:
            logger.error(f"table_metadata_error: {table_metadata_error}")
            await cl.Message(content=table_metadata_error).send()
        elif len(table_metadata_array) >= 1:
            for table_metadata in table_metadata_array:
                df = pd.DataFrame(
                    [ele.model_dump() for ele in table_metadata.raw_fields_info]
                )[
                    ["cn_name", "en_name", "desc", "field_type", "dict_key", "example"]
                ].rename(
                    columns={
                        "cn_name": "中文名称",
                        "en_name": "英文名称",
                        "desc": "描述",
                        "field_type": "字段类型",
                        "dict_key": "字典",
                        "example": "样例数据",
                    }
                )
                table_metadata_elements = [
                    cl.Dataframe(
                        data=df,
                        display="side",
                        name=f"{table_metadata.table_en_name}表字段信息",
                    )
                ]
                await cl.Message(
                    content=f"{table_metadata.table_en_name}表字段信息",
                    elements=table_metadata_elements,
                ).send()

            await cl.Message(content="正在生成测试数据...").send()
            event = await cl.make_async(gen_fake_data_graph.invoke)(
                {
                    "user_input": cl.user_session.get("user_input"),
                    "user_intent": cl.user_session.get("user_intent"),
                    "table_metadata_array": cl.user_session.get("table_metadata_array"),
                    "fake_data": {},
                    "max_retries": 5,
                    "current_retries": 0,
                },
                thread,
                stream_mode="values",
            )
            fake_data: dict[list] = event["fake_data"]
            logger.info("完成")
            end_time = asyncio.get_event_loop().time()
            elapsed_time = end_time - start_time
            cost_msg = f"运行耗时: {elapsed_time: .2f} 秒"
            logger.info(cost_msg)
            for item_table_en_name, item_fake_data in fake_data.items():
                logger.info(f"表名称: {item_table_en_name}")
                # logger.info(f"生成数据: {item_fake_data}")
                fake_df = pd.DataFrame(item_fake_data)
                fake_elements = [
                    cl.Dataframe(
                        data=fake_df,
                        name=f"{item_table_en_name}仿真测试数据",
                        display="side",
                    )
                ]
                await cl.Message(
                    elements=fake_elements,
                    content=f"{item_table_en_name}仿真测试数据",
                ).send()
            await cl.Message(
                content=f"仿真测试数据生成完成，耗时{elapsed_time:.2f}秒",
            ).send()
            # 保存生成的测试数据
            save_json_path = pathlib.Path(r"F:\GITLAB\DataForge\data\output").joinpath(
                f"fake_data_{thread_id}.json"
            )
            await save_json_data_async(save_json_path, fake_data)
            download_json_elements = [
                cl.File(
                    name=f"fake_data_{thread_id}.json",
                    path=str(save_json_path.absolute()),
                    display="inline",
                ),
            ]
            await cl.Message(
                elements=download_json_elements,
                content="请下载生成的仿真测试数据",
            ).send()
    else:
        try:
            user_input = message.content.strip()
            cl.user_session.set("user_input", user_input)
            user_intent = await input_intent_analyze(user_input, thread)
            cl.user_session.set("user_intent", user_intent)
            await cl.Message(
                content=user_intent.model_dump_json(indent=2), language="python"
            ).send()
            await cl.Message(
                content="上述意图识别结果是否正确？若不正确请调整输入信息再次尝试意图识别；若正确，请输入“正确”，将开始数据生成任务。"
            ).send()

        except Exception as e:
            error_message = f"意图分析异常: {e}"
            await cl.Message(content=error_message).send()
