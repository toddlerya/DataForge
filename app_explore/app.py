# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import json

import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from loguru import logger

from agent.explore_graph import expolore_graph
from agent.llm import chat_llm
from common.initialization import init_env, setup_logging
from config import PROJECT_PATH
from utils.log import LogManager, TracedLogger

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="ExploreApp.log",
    file_log_level="INFO",
    console_log_level="DEBUG",
)
setup_logging(log_config.get_config().get("handlers"))
traced_logger = TracedLogger()
init_env()

# 加载 .env 文件
load_dotenv(PROJECT_PATH.absolute())


async def create_simple_dataframe_element(data: list[dict]) -> list[cl.Dataframe]:
    """将嵌套的JSON数据展示为DataFrame"""
    df = pd.DataFrame(data=data)
    element = cl.Dataframe(name="表格信息", data=df, display="inline")
    return [element]


async def create_table_metadata_dataframe_element_array(
    data: list[dict],
) -> list[cl.Dataframe]:
    """将多个表元数据JSON展示为DataFrame"""
    elements = []
    for each_table_metadata in data:
        df = pd.DataFrame(each_table_metadata.get("table_fields", [{}]))[
            [
                "cn_name",
                "en_name",
                "desc",
                "field_type",
                "dict_key",
                "example",
            ]
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
        each_table_metadata_elements = cl.Dataframe(
            data=df,
            display="side",
            name=f"{each_table_metadata.get('table_en_name')}({each_table_metadata.get('table_cn_name')})表字段信息",
        )
        elements.append(each_table_metadata_elements)
    return elements


@cl.set_chat_profiles  # type: ignore
async def chat_profile(current_user: cl.User):
    if current_user and current_user.metadata["role"]:
        logger.info(f"current_user.metadata: {current_user.metadata}")

    return [
        cl.ChatProfile(
            name="默认配置",
            icon="public/icons/fhai.ico",
            markdown_description=f"当前使用的模型名称: {chat_llm.model}",
            starters=[
                cl.Starter(
                    label="当前已对接多少元数据表",
                    message="当前已对接多少元数据表?",
                    icon="public/icons/text.svg",
                ),
                cl.Starter(
                    label="当前对接了哪些环境配置",
                    message="当前对接了哪些环境配置?",
                    icon="public/icons/setting.svg",
                ),
                cl.Starter(
                    label="与VPN相关的表有哪些",
                    message="与VPN相关的表有哪些?",
                    icon="public/icons/mobile-phone.svg",
                ),
                cl.Starter(
                    label="哪些表包含身份证号码字段",
                    message="哪些表包含身份证号码字段?",
                    icon="public/icons/fingerprint.svg",
                ),
                cl.Starter(
                    label="哪些表包含身份证号码字段",
                    message="哪些表包含身份证号码字段?",
                    icon="public/icons/table.svg",
                ),
            ],
        )
    ]


@cl.on_message
async def on_message(message: cl.Message):
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        trace_token = traced_logger.set_trace_uuid(trace_uuid=cl.context.session.id)
        cl.user_session.set("trace_token", trace_token)

    if hasattr(cl.context.session, "environ") and cl.context.session.environ:
        client_port_tuple = cl.context.session.environ.get("asgi.scope", {}).get(
            "client"
        )
        if client_port_tuple and len(client_port_tuple) == 2:
            logger.info(f"client_port_tuple: {client_port_tuple}")
            cl.user_session.set("client_ip", client_port_tuple[0])
    else:
        cl.user_session.set("client_ip", "127.0.0.1")

    logger.info(
        f"session_id={cl.context.session.id} ip={cl.user_session.get('client_ip')} "
        f"message: {message.content}"
    )

    init_state = {
        "messages": HumanMessage(content=message.content.strip()),
        "max_retries": 5,
        "session_id": cl.context.session.id,
        "client_ip": cl.user_session.get("client_ip"),
        "tool_call_result": None,
    }

    run_config = RunnableConfig(
        configurable={"thread_id": cl.context.session.id},
        recursion_limit=50,
    )

    async for event in expolore_graph.astream(init_state, run_config):
        for node, state in event.items():
            if node == "filter_and_summarize_data":
                logger.info("[entry] filter_and_summarize_data")
                await cl.Message(author="AI", content="正在处理, 请稍等...").send()
                tool_name = state.get("tool_name")
                tool_args = state.get("tool_args")
                tool_call_result = state.get("tool_call_result")
                if tool_call_result and tool_name == "metadata_table_statistic_tool":
                    with cl.Step(
                        name=f"🛠️ {tool_name}(kwargs=**{tool_args})",
                        type="tool",
                    ) as step:
                        step.input = tool_call_result
                        step.language = "json"
                        dataframe_elements = await create_simple_dataframe_element(
                            data=json.loads(tool_call_result)
                        )
                        if dataframe_elements:
                            logger.info(
                                f"use {create_simple_dataframe_element} created "
                                f"dataframe element count: {len(dataframe_elements)} "
                            )
                            step.elements = dataframe_elements
                        else:
                            logger.warning(
                                "dataframe_elements is None, just show raw json"
                            )
                            step.output = tool_call_result
                            step.language = "json"
                if tool_call_result and tool_name == "metadata_table_filter_tool":
                    dataframe_elements = (
                        await create_table_metadata_dataframe_element_array(
                            data=json.loads(tool_call_result)
                        )
                    )
                    logger.info(
                        f"create_table_metadata_dataframe_element_array created "
                        f"dataframe_elements count: {len(dataframe_elements)}"
                    )

                    if dataframe_elements:
                        await cl.Message(
                            content="查询到一些表字段信息如下",
                        ).send()
                        for each_table_element in dataframe_elements:
                            await cl.Message(
                                author="Tool",
                                content=each_table_element.name,
                                elements=[each_table_element],
                            ).send()
                    else:
                        await cl.Message(
                            author="Tool",
                            content="工具查询到的表字段信息文本: \n" + tool_call_result,
                        ).send()
            if node == "summary_node":
                logger.info("[entry] summary_node")
                summary = state.get("summary")
                await cl.Message(author="AI", content=summary).send()

    # 完成会话清空trace_uuid
    trace_token = cl.user_session.get("trace_token")
    if trace_token is None:
        logger.warning(
            f"session_id={cl.context.session.id} trace_token not found, skipping reset."
        )
    else:
        # 这里 Pylance 知道 trace_token 是 Token 类型，且不是 None
        traced_logger.reset_trace_uuid(trace_token)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
