# coding: utf-8
# @Time:     2025/5/7 16:48
# @Author:   toddlerya
# @FileName: chatbot.py
# @Project:  DataForge

import asyncio

import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from langchain_core.runnables.config import RunnableConfig
from loguru import logger

from agent.data_graph import data_gen_graph
from agent.state import DataGenUserIntentSchema, PydanticDataGeniusPlan
from common.initialization import init_env, setup_logging
from config import DG_PLAN_PATH, PROJECT_PATH
from utils.log import LogManager, TracedLogger

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="DataForgeDataGenApp.log",
    file_log_level="INFO",
)
setup_logging(log_config.get_config().get("handlers"))
traced_logger = TracedLogger()
init_env()

# 加载 .env 文件
load_dotenv(PROJECT_PATH.absolute())


@cl.on_chat_start
async def start_chat():
    if hasattr(cl.context.session, "environ") and cl.context.session.environ:
        client_port_tuple = cl.context.session.environ.get("asgi.scope", {}).get(
            "client"
        )
        if client_port_tuple and len(client_port_tuple) == 2:
            logger.info(f"client_port_tuple: {client_port_tuple}")
            cl.user_session.set("client_ip", client_port_tuple[0])
    else:
        cl.user_session.set("client_ip", "127.0.0.1")

    text_content = f"""{cl.user_session.get("client_ip")},
    您好！我是您的测试数据生成助手\n
目前支持的表为盘古或数据域管理的表。
请输入需要构造的表名称，期望生成的数据条数。
若需字段对字段有特殊的约束条件, 比如期望某些字段满足特定的固定值或枚举值,
请在工具运行完成后端DG任务链接页面按照DG规则进行配置。\n
====输入内容示例====\n
数据库表名称 (必填): massdata.ADM_REL_MOBILE
期望生成数据条数 (必填): 5
"""
    elements = [cl.Text(name="说明", content=text_content, display="inline")]
    await cl.Message(
        author="Assistant", content="请输入测试数据构造需求", elements=elements
    ).send()


async def process_step(event, graph):
    """
    辅助函数, 用于处理和显示Langgraph的每一步
    Args:
        graph:
        event:

    Returns:

    """
    for node, state in event.items():
        logger.debug(f"node: {node} state: {state} ")
        if node == "analyze_data_intent":
            logger.info("[process] analyze_data_intent")
            user_intent: DataGenUserIntentSchema = state.get("user_intent")
            await cl.Message(
                author="AI",
                content=user_intent.model_dump_json(indent=2),
                language="python",
            ).send()
            res = await cl.AskUserMessage(
                author="Assistant",
                content=(
                    "上述意图识别结果是否正确？"
                    "若不正确请调整输入信息再次尝试意图识别; "
                    "若正确, 请输入“正确“或”Y”, 将开始数据生成任务。"
                ),
                timeout=300,
            ).send()
            if res and "output" in res:
                res_text = res["output"].strip()
                logger.info(f"human_intent_feedback: {res_text}")
                cl.user_session.set("human_intent_feedback", res_text)
                graph.update_state(
                    cl.user_session.get("configs"),
                    {"human_intent_feedback": res_text},
                    as_node="intent_human_feedback_node",
                )
                start_time = asyncio.get_event_loop().time()
                cl.user_session.set("start_time", start_time)
                await cl.Message(content="正在获取表元数据信息...").send()
        elif node == "query_table_raw_field_info":
            logger.info("[process] query_table_raw_field_info")
            end_time = asyncio.get_event_loop().time()
            cl.user_session.set("end_time", end_time)
            await cl.Message(content="已获取表元数据信息...").send()
            table_metadata = state.get("table_metadata_info")
            table_metadata_error = state.get("table_metadata_error")
            if table_metadata_error:
                logger.error(f"table_metadata_error: {table_metadata_error}")
                await cl.Message(
                    author="Tool", content="\n".join(table_metadata_error)
                ).send()
            else:
                df = pd.DataFrame(
                    [ele.model_dump() for ele in table_metadata.raw_fields_info]
                )[
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
                table_metadata_elements = [
                    cl.Dataframe(
                        data=df,
                        display="side",
                        name=f"{table_metadata.table_en_name}表字段信息",
                    )
                ]
                await cl.Message(
                    author="Database",
                    content=f"{table_metadata.table_en_name}表字段信息",
                    elements=table_metadata_elements,
                ).send()
                await cl.Message(content="正在生成DataGenius执行计划...").send()
        elif node == "dg_category_recommend":
            logger.info("[process] dg_category_recommend")
            pydantic_data_genius_plan: PydanticDataGeniusPlan = state.get(
                "pydantic_data_genius_plan"
            )
            await cl.Message(
                author="Assistant",
                content="当前生成的DataGenius数据生成计划配置如下, 将开始数据生成任务",
            ).send()
            await cl.Message(
                author="AI",
                content=pydantic_data_genius_plan.model_dump_json(indent=2),
                language="python",
            ).send()

        elif node == "save_dg_plan2json":
            logger.info("[process] save_dg_plan2json")
            pydantic_data_genius_plan: PydanticDataGeniusPlan = state.get(
                "pydantic_data_genius_plan"
            )
            dg_plan_json_path = DG_PLAN_PATH.joinpath(
                f"{pydantic_data_genius_plan.rule_name}.json"
            ).absolute()
            logger.info(f"dg_plan_json_path: {dg_plan_json_path}")
            download_dg_plan_json_elements = [
                cl.File(
                    name=f"{pydantic_data_genius_plan.rule_name}.json",
                    path=str(dg_plan_json_path),
                    display="inline",
                ),
            ]
            await cl.Message(
                author="Assistant",
                content="可下载DataGenius计划配置备用，比如上传到DataGenius二次修改",
                elements=download_dg_plan_json_elements,
            ).send()

            # 表元数据文件信息
            dg_plan_table_metadata_json_path = DG_PLAN_PATH.joinpath(
                f"{pydantic_data_genius_plan.rule_name}_table_metadata.json"
            ).absolute()
            logger.info(
                f"dg_plan_table_metadata_json_path: {dg_plan_table_metadata_json_path}"
            )
            download_dg_plan_table_metadata_json_elements = [
                cl.File(
                    name=f"{pydantic_data_genius_plan.rule_name}_table_metadata.json",
                    path=str(dg_plan_table_metadata_json_path),
                    display="inline",
                ),
            ]
            await cl.Message(
                author="Assistant",
                content="可下载表的元数据配置信息，入库测试数据时可能会用到",
                elements=download_dg_plan_table_metadata_json_elements,
            ).send()

        elif node == "create_dg_task":
            logger.info("[process] create_dg_task")
            pydantic_data_genius_plan: PydanticDataGeniusPlan = state.get(
                "pydantic_data_genius_plan"
            )
            await cl.Message(
                author="Assistant",
                content=f"已在DataGenius创建任务，任务名称：{pydantic_data_genius_plan.rule_name}",
            ).send()

        elif node == "query_dg_task_status":
            logger.info("[process] query_dg_task_status")

            pydantic_data_genius_plan: PydanticDataGeniusPlan = state.get(
                "pydantic_data_genius_plan"
            )
            data_genius_plan_task_id = state.get("data_genius_plan_task_id")
            data_genius_plan_edit_url = state.get("data_genius_plan_edit_url")
            data_genius_plan_run_duration = state.get("data_genius_plan_run_duration")
            data_genius_plan_output_filesize = state.get(
                "data_genius_plan_output_filesize"
            )
            data_genius_plan_output_url = state.get("data_genius_plan_output_url")
            query_data_genius_task_error = state.get("query_data_genius_task_error")
            if query_data_genius_task_error:
                done_message = query_data_genius_task_error
                logger.error(query_data_genius_task_error)
            else:
                done_message = (
                    "DataGenius任务已完成。\n"
                    f"- **DG任务名称**: {pydantic_data_genius_plan.rule_name}\n"
                    f"- **DG运行耗时**: {data_genius_plan_run_duration}\n"
                    f"- **生成数据大小**: {data_genius_plan_output_filesize}\n"
                    f"- **数据下载地址**: {data_genius_plan_output_url}\n"
                    f"- **DG任务编辑地址**: "
                    f"[{data_genius_plan_task_id}]({data_genius_plan_edit_url})"
                )
                logger.info(done_message)
            await cl.Message(author="Assistant", content=done_message).send()

        elif node == "END":
            start_time = cl.user_session.get("start_time") or 0.0
            end_time = cl.user_session.get("end_time") or 0.0
            # 确保是 float 类型
            if isinstance(start_time, (int, float)) and isinstance(
                end_time, (int, float)
            ):
                elapsed_time = end_time - start_time
                logger.info(f"Total execution time: {elapsed_time:.2f} seconds")
            else:
                logger.warning("Invalid time values in session.")
                elapsed_time = 0.0
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
        f"session_id={cl.context.session.id} ip={cl.user_session.get('client_ip')} "
        f"message: {message.content}"
    )
    config: RunnableConfig = {
        "configurable": {"thread_id": cl.context.session.id},
        "recursion_limit": 50,
    }
    cl.user_session.set("configs", config)

    current_state = data_gen_graph.get_state(config)

    logger.debug(
        f"session_id={cl.context.session.id} ip={cl.user_session.get('client_ip')} "
        f"current_state: {current_state}"
    )
    if not current_state.values.get("user_input"):
        logger.info(
            f"初始化: session_id={cl.context.session.id} "
            f"client_ip={cl.user_session.get('client_ip')}"
        )
        init_state = {
            "user_input": message.content.strip(),
            "table_metadata_error": [],
            "max_retries": 5,
            "session_id": cl.context.session.id,
            "client_ip": cl.user_session.get("client_ip"),
        }
        async for event in data_gen_graph.astream(init_state, config):
            await process_step(event, data_gen_graph)

    async for step_output in data_gen_graph.astream(None, config):
        await process_step(step_output, data_gen_graph)
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
