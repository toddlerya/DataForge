# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import asyncio
from pathlib import Path

import chainlit as cl

from dotenv import load_dotenv
from loguru import logger

from config import PROJECT_PATH, GEN_TABLE_MODELS_TEMP_PATH
from agent.table_graph import table_gen_graph
from agent.state import TableGenUserIntentSchema

from common.initialization import init_env, setup_logging

from utils.log import LogManager, TracedLogger

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="DataForgeTableGenApp.log",
    file_log_level="INFO",
)
setup_logging(log_config.get_config().get("handlers"))
traced_logger = TracedLogger()
init_env()

# 加载 .env 文件
load_dotenv(PROJECT_PATH.absolute())


@cl.on_chat_start
async def start_chat():
    print(cl.context.session)
    if hasattr(cl.context.session, "environ") and cl.context.session.environ:
        client_port_tuple = cl.context.session.environ.get("asgi.scope", {}).get(
            "client"
        )
        if client_port_tuple and len(client_port_tuple) == 2:
            logger.info(f"client_port_tuple: {client_port_tuple}")
            cl.user_session.set("client_ip", client_port_tuple[0])
    else:
        cl.user_session.set("client_ip", "127.0.0.1")

    text_content = f"""{cl.user_session.get("client_ip")}，您好！我是您的仿真数据表生成助手\n\n
目前我会参考盘古和数据域已有的表信息生成新的表结构定义配置，请输入需要生成的表的类型，每个表期望的字段数量，生成多少个表配置。
====输入内容示例====
帮我生成一些人员属性、上网行为、位置轨迹类别的表，每个表的字段数量最少10个，最多100个，至少生成2张表
"""
    elements = [cl.Text(name="说明", content=text_content, display="inline")]
    await cl.Message(
        author="Assistant", content="请输入测试表构造需求", elements=elements
    ).send()


async def process_step(event, graph):
    """
    辅助函数，用于处理和显示Langgraph的每一步
    Args:
        graph:
        event:

    Returns:

    """
    for node, state in event.items():
        logger.debug(f"node: {node} state: {state} ")

        if node == "analyze_table_intent":
            logger.info(f"[process] analyze_table_intent")
            user_intent: TableGenUserIntentSchema = state.get("user_intent")
            await cl.Message(
                author="AI",
                content=user_intent.model_dump_json(indent=2),
                language="python",
            ).send()
            res = await cl.AskUserMessage(
                author="Assistant",
                content="上述意图识别结果是否正确？若不正确请调整输入信息再次尝试意图识别；若正确，请输入“正确”，将开始数据生成任务。",
                timeout=300,
            ).send()
            if res:
                res_text = res["output"].strip()
                logger.info(f"human_intent_feedback: {res_text}")
                cl.user_session.set("human_intent_feedback", res_text)
                graph.update_state(
                    cl.user_session.get("configs"),
                    {"human_intent_feedback": res_text},
                    as_node="table_intent_human_feedback",
                )
                start_time = asyncio.get_event_loop().time()
                cl.user_session.set("start_time", start_time)

                await cl.Message(content="正在准备素材表数据...").send()

        elif node == "material_table_group_strategy":
            logger.info("[process] material_table_group_strategy")
            end_time = asyncio.get_event_loop().time()
            cl.user_session.set("end_time", end_time)
            await cl.Message(content="已准备好素材表数据...").send()
            material_table_groups = state.get("material_table_groups")
            if material_table_groups:
                await cl.Message(
                    content=f"素材表分为{len(material_table_groups)}组用于生成仿真表"
                ).send()

        elif node == "material_tables_mapping_dimension_table":
            logger.info("[process] material_tables_mapping_dimension_table")
            mapping_dimension_table_info_slice = state.get(
                "mapping_dimension_table_info_slice"
            )
            await cl.Message(
                author="Assistant",
                content=f"当前已根据素材表由LLM推荐出{len(mapping_dimension_table_info_slice)}组特征表计划。",
            ).send()

        elif node == "translate_table_name":
            logger.info("[process] translate_table_name")
            await cl.Message(
                author="Assistant",
                content="已完成表英文名翻译校对",
            ).send()

        elif node == "save_mapping_dimension_table_info":
            logger.info("[process] save_mapping_dimension_table_info")
            create_session_temp_data_path_message = state.get(
                "create_session_temp_data_path_message"
            )
            if create_session_temp_data_path_message:
                await cl.Message(
                    author="Assistant",
                    content=f"创建存储特征表计划目录异常: {create_session_temp_data_path_message}",
                ).send()
            else:
                await cl.Message(
                    author="Assistant",
                    content=f"已存储特征表计划，准备生成特征表",
                ).send()

        elif node == "gen_dimension_table_config":
            logger.info("[process] gen_dimension_table_config")
            dimension_table_config_slice = state.get("dimension_table_config_slice")
            await cl.Message(
                author="Assistant",
                content=f"已生成{len(dimension_table_config_slice)}组特征表配置",
            ).send()

        elif node == "save_dimension_table_config":
            logger.info("[process] save_dimension_table_config")
            await cl.Message(
                author="Assistant",
                content=f"已存储特征表配置",
            ).send()

        elif node == "archive_table_data":
            logger.info("[process] archive_table_data")
            session_archive_file_path: Path = state.get("session_archive_file_path")
            if session_archive_file_path is None:
                archive_message = state.get("archive_message")
                await cl.Message(
                    author="Assistant", content=f"打包结果异常: {archive_message}"
                ).send()
            else:
                download_archive_elements = [
                    cl.File(
                        name=session_archive_file_path.name.strip(),
                        path=str(session_archive_file_path.absolute()),
                        display="inline",
                    ),
                ]
                await cl.Message(
                    author="Assistant",
                    content="请下载LLMs生成的仿真表配置文件",
                    elements=download_archive_elements,
                ).send()

        elif node == "END":
            elapsed_time = cl.user_session.get("end_time") - cl.user_session.get(
                "start_time"
            )
            cost_msg = f"{elapsed_time: .2f} 秒"
            final_message = (
                f"本次任务运行完成，总计耗时: {cost_msg}, 如需再次使用请开启新会话."
            )
            logger.info(final_message)
            await cl.Message(author="Assistant", content=final_message).send()


@cl.on_message
async def main(message: cl.Message):
    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        trace_token = traced_logger.set_trace_uuid(trace_uuid=cl.context.session.id)
        cl.user_session.set("trace_token", trace_token)

    logger.info(
        f"session_id={cl.context.session.id} ip={cl.user_session.get('client_ip')} message: {message.content}"
    )
    config = {
        "configurable": {"thread_id": cl.context.session.id},
        "recursion_limit": 50,
    }
    cl.user_session.set("configs", config)

    current_state = table_gen_graph.get_state(config)
    logger.debug(
        f"session_id={cl.context.session.id} ip={cl.user_session.get('client_ip')} current_state: {current_state}"
    )
    if not current_state.values.get("user_input"):
        init_state = {
            "user_input": message.content.strip(),
            "max_retries": 5,
            "session_id": cl.context.session.id,
            "client_ip": cl.user_session.get("client_ip"),
            "session_temp_data_path": GEN_TABLE_MODELS_TEMP_PATH.joinpath(
                cl.context.session.id
            ),
        }
        async for event in table_gen_graph.astream(init_state, config):
            await process_step(event, table_gen_graph)

    async for step_output in table_gen_graph.astream(None, config):
        await process_step(step_output, table_gen_graph)

    # 完成会话清空trace_uuid
    traced_logger.reset_trace_uuid(cl.user_session.get("trace_token"))


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
