# coding: utf-8
# @Time:     2025/09/25 11:39
# @Author:   toddlerya
# @FileName: app.py
# @Project:  DataForge

import asyncio
import json
from typing import cast

import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langgraph.types import Command
from loguru import logger

from agent.agent_graph import main_graph
from agent.llm import chat_llm
from agent.state import (
    PydanticDataGeniusPlan,
    SQLModeTableInfoSchema,
    TableMetadataSchema,
)
from common.initialization import init_env, setup_logging
from config import DG_PLAN_PATH, PROJECT_PATH
from utils.log import LogManager, TracedLogger

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="AgentApp.log",
    file_log_level="TRACE",
    console_log_level="INFO",
)
setup_logging(log_config.get_config().get("handlers"))
traced_logger = TracedLogger()
init_env()

# 加载 .env 文件
load_dotenv(PROJECT_PATH.absolute())


next_sub_graph_name_map = {
    "meta_mode_data_gen_graph": "测试数据生成(元数据模式)",
    "expolore_graph": "表元数据信息探索",
    "sql_mode_data_gen_graph": "测试数据生成(SQL模式)",
    "unkown_node": "未知意图",
}


async def create_simple_dataframe_element(data: list[dict]) -> list[cl.Dataframe]:
    """将嵌套的JSON数据展示为DataFrame"""
    df = pd.DataFrame(data=data)
    element = cl.Dataframe(name="表格信息", data=df, display="inline")
    return [element]


async def create_table_metadata_dataframe_element_array(
    df_list: list[pd.DataFrame],
    table_en_name_list: list[str],
    table_cn_name_list: list[str],
) -> list[cl.Dataframe]:
    """将多个表元数据JSON展示为DataFrame"""
    logger.info(f"df_list count: {len(df_list)}")
    elements = []

    for index, df in enumerate(df_list):
        each_table_metadata_elements = cl.Dataframe(
            data=df,
            display="side",
            name=(f"{table_en_name_list[index]} {table_cn_name_list[index]}"),
        )
        elements.append(each_table_metadata_elements)
    return elements


async def handle_graph_event(node: str, state: dict, run_config: RunnableConfig):  # noqa: C901
    """处理图事件的同一函数"""
    if node == "analyze_intent":
        logger.info("[entry] analyze_intent")
        await cl.Message(content="意图分析中").send()
        next_sub_graph_name = state.get("next_sub_graph_name")
        logger.info(f"next_sub_graph_name==>{next_sub_graph_name}")
        if next_sub_graph_name:
            await cl.Message(
                content=(
                    f"### 意图路由: "
                    f"{next_sub_graph_name_map.get(next_sub_graph_name, '未知意图')}"
                ),
            ).send()
    elif node == "filter_and_summarize_data":
        logger.info("[entry] filter_and_summarize_data")
        await cl.Message(content="正在收集整理信息...").send()
        tool_name = state.get("tool_name")
        tool_call_result = state.get("tool_call_result")
        if tool_call_result and tool_name == "metadata_table_statistic_tool":
            with cl.Step(
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
                    step.elements = dataframe_elements  # type: ignore
                else:
                    logger.warning("dataframe_elements is None, just show raw json")
                    step.output = tool_call_result
                    step.language = "json"
        elif tool_call_result and tool_name == "metadata_table_filter_tool":
            df_list: list[pd.DataFrame] = []
            table_en_name_list: list[str] = []
            table_cn_name_list: list[str] = []
            for each_table_metadata in json.loads(tool_call_result):
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
                df_list.append(df)
                table_en_name_list.append(
                    each_table_metadata.get("table_en_name", "not_tb_en_name")
                )
                table_cn_name_list.append(
                    each_table_metadata.get("table_cn_name", "no_tb_cn_name")
                )
            dataframe_elements = await create_table_metadata_dataframe_element_array(
                df_list=df_list,
                table_en_name_list=table_en_name_list,
                table_cn_name_list=table_cn_name_list,
            )
            logger.info(
                f"create_table_metadata_dataframe_element_array created "
                f"dataframe_elements count: {len(dataframe_elements)}"
            )
            if dataframe_elements:
                await cl.Message(
                    content=(
                        f"查询到{len(dataframe_elements)}个结果如下, 可点击展开查看详情"
                    ),
                ).send()
                for each_table_element in dataframe_elements:
                    await cl.Message(
                        content=each_table_element.name,
                        elements=[each_table_element],
                    ).send()
            else:
                await cl.Message(
                    content="工具查询到的表字段信息文本: \n" + tool_call_result,
                ).send()
        # else:
        #     await cl.Message(
        #         author="Tool",
        #         content="未查询到相关信息",
        #     ).send()
    elif node == "summary_node":
        logger.info("[entry] summary_node")
        summary = state.get("summary", "")
        await cl.Message(content=summary).send()
    elif node == "analyze_meta_intent" or node == "analyze_sql_intent":
        logger.info("[entry] analyze_meta_intent or analyze_sql_intent")
        user_intent = state.get("user_intent")
        if not user_intent:
            logger.info("还没有出现意图呢...")
            return False
        await cl.Message(
            content=user_intent.model_dump_json(indent=2),
            language="python",
        ).send()
    elif node == "__interrupt__":
        logger.info("[entry] __interrupt__")
        return await handle_interrupt(run_config=run_config)
    elif node == "query_table_raw_field_info":
        logger.info("[entry] query_table_raw_field_info")
        end_time = asyncio.get_event_loop().time()
        cl.user_session.set("end_time", end_time)
        await cl.Message(content="已获取表元数据信息...").send()
        table_metadata_info = state.get("table_metadata_info")
        table_metadata_error = state.get("table_metadata_error")
        if table_metadata_error:
            logger.error(f"table_metadata_error: {table_metadata_error}")
            # await cl.Message(content="\n".join(table_metadata_error)).send()
            return True
        if table_metadata_info:
            table_metadata_info = cast(TableMetadataSchema, table_metadata_info)
            df = pd.DataFrame(
                [ele.model_dump() for ele in table_metadata_info.raw_fields_info]
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
                    name=f"{table_metadata_info.table_en_name}表字段信息",
                )
            ]
            if table_metadata_elements:
                await cl.Message(
                    content=f"{table_metadata_info.table_en_name}表字段信息",
                    elements=table_metadata_elements,
                ).send()
            else:
                await cl.Message(
                    content="工具查询到的表字段信息文本: \n"
                    + json.dumps(
                        [
                            ele.model_dump()
                            for ele in table_metadata_info.raw_fields_info
                        ],
                        ensure_ascii=True,
                    ),
                ).send()
            await cl.Message(content="正在生成DataGenius执行计划...").send()
    elif node == "table_meta_and_rag_failed":
        logger.info("[entry] table_meta_and_rag_failed")
        messages = state.get("messages")
        if messages:
            last_message = messages[-1]
            logger.info(f"last_message: {last_message}")
            await cl.Message(content=last_message.content).send()
            return True
    elif node == "sql_parse_to_table_info":
        logger.info("[entry] sql_parse_to_table_info")
        end_time = asyncio.get_event_loop().time()
        cl.user_session.set("end_time", end_time)
        await cl.Message(content="已解析SQL为表结构信息...").send()
        table_info_error = state.get("table_info_error")
        table_info_data = state.get("table_info_data")
        if table_info_error:
            logger.error(f"table_info_error: {table_info_error}")
            await cl.Message(content=table_info_error).send()
            return True
        elif table_info_data:
            table_info_data = cast(SQLModeTableInfoSchema, table_info_data)
            df = pd.DataFrame(
                [ele.model_dump() for ele in table_info_data.fields_info]
            )[
                [
                    "en_name",
                    "alias_name",
                    "comment",
                ]
            ].rename(
                columns={
                    "en_name": "字段英文名称",
                    "alias_name": "字段别名",
                    "comment": "字段注释",
                }
            )
            table_metadata_elements = [
                cl.Dataframe(
                    data=df,
                    display="side",
                    name=f"{table_info_data.table_en_name}表字段信息",
                )
            ]
            await cl.Message(
                content=f"{table_info_data.table_en_name}表字段信息",
                elements=table_metadata_elements,
            ).send()
    elif node == "dg_rule_processor":
        logger.info("[process] dg_rule_processor")
        pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
        if pydantic_data_genius_plan:
            pydantic_data_genius_plan = cast(
                PydanticDataGeniusPlan, pydantic_data_genius_plan
            )
            await cl.Message(
                content=("已生成DataGenius任务配置, 将开始数据生成任务"),
            ).send()
            # await cl.Message(
            #     content=pydantic_data_genius_plan.model_dump_json(indent=2),
            #     language="json",
            # ).send()
        else:
            logger.error(
                f"pydantic_data_genius_plan为空: value={pydantic_data_genius_plan}"
            )
            await cl.Message(
                content="pydantic_data_genius_plan为空, 请联系开发者",
            ).send()
            return True
    elif node == "save_dg_plan2json":
        logger.info("[process] save_dg_plan2json")
        pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
        if pydantic_data_genius_plan:
            pydantic_data_genius_plan = cast(
                PydanticDataGeniusPlan, pydantic_data_genius_plan
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
                content=("可下载DataGenius计划配置备用, 比如上传到DataGenius二次修改"),
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
                content="可下载表的元数据配置信息，入库测试数据时可能会用到",
                elements=download_dg_plan_table_metadata_json_elements,
            ).send()
        else:
            logger.error(
                f"pydantic_data_genius_plan为空: value={pydantic_data_genius_plan}"
            )
            await cl.Message(
                content="pydantic_data_genius_plan为空, 请联系开发者",
            ).send()
            return True
    elif node == "create_dg_task":
        logger.info("[process] create_dg_task")
        pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
        if pydantic_data_genius_plan:
            pydantic_data_genius_plan = cast(
                PydanticDataGeniusPlan, pydantic_data_genius_plan
            )
            await cl.Message(
                content=f"已在DataGenius创建任务，任务名称：{pydantic_data_genius_plan.rule_name}",
            ).send()
        else:
            logger.error(
                f"pydantic_data_genius_plan为空: value={pydantic_data_genius_plan}"
            )
            await cl.Message(
                content="pydantic_data_genius_plan为空, 请联系开发者",
            ).send()
            return True
    elif node == "query_dg_task_status":
        logger.info("[process] query_dg_task_status")
        pydantic_data_genius_plan = state.get("pydantic_data_genius_plan")
        if pydantic_data_genius_plan:
            pydantic_data_genius_plan = cast(
                PydanticDataGeniusPlan, pydantic_data_genius_plan
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
                return True
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
            await cl.Message(content=done_message).send()
        else:
            logger.error(
                f"pydantic_data_genius_plan为空: value={pydantic_data_genius_plan}"
            )
            await cl.Message(
                content="pydantic_data_genius_plan为空, 请联系开发者",
            ).send()
            return True
    elif node == "unkown_node":
        logger.info("[entry] unkown_node")
        messages = state.get("messages", [])
        logger.trace(f"messages: {messages}")
        if len(messages) >= 1:
            last_message = messages[-1].content
        else:
            last_message = (
                "抱歉，我暂时还不具备处理您提到的问题的能力。"
                "请提供更具体的信息或尝试其他问题。"
            )
        await cl.Message(content=last_message).send()
        return True
    elif node == "END":
        start_time = cl.user_session.get("start_time") or 0.0
        end_time = cl.user_session.get("end_time") or 0.0
        # 确保是 float 类型
        if isinstance(start_time, (int, float)) and isinstance(end_time, (int, float)):
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
        await cl.Message(content=final_message).send()


async def handle_interrupt(run_config: RunnableConfig) -> bool:
    """处理中断, 返回还是继续运行"""
    if human_intent_feedback := cl.user_session.get("human_intent_feedback"):
        logger.warning(
            f"用户已经反馈过并完成了一次任务, 清空用户反馈。"
            f"human_intent_feedback={human_intent_feedback}"
        )
        cl.user_session.set("human_intent_feedback", None)
        return True
    res = await cl.AskUserMessage(
        content=(
            "上述意图识别结果是否正确？"
            "若不正确请调整输入信息再次尝试意图识别; "
            "若正确, 请输入“正确“或”Y”, 将开始任务。"
        ),
        timeout=300,
    ).send()
    if res and "output" in res:
        start_time = asyncio.get_event_loop().time()
        cl.user_session.set("start_time", start_time)

        res_text = res["output"].strip()
        logger.info(f"human_intent_feedback: {res_text}")
        cl.user_session.set("human_intent_feedback", res_text)
        resume_map = {"human_intent_feedback": res_text}

        # 继续运行
        async for event in main_graph.astream(
            Command(resume=resume_map),
            run_config,
            stream_mode="updates",
            subgraphs=True,
        ):
            event = cast(tuple[tuple, dict], event)
            for node, state in event[1].items():
                logger.trace(f"current_node={node} current_state={state}")
                await handle_graph_event(node=node, state=state, run_config=run_config)
        return True
    return False


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
                # cl.Starter(
                #     label="当前对接了哪些环境配置",
                #     message="当前对接了哪些环境配置?",
                #     icon="public/icons/setting.svg",
                # ),
                cl.Starter(
                    label="与VPN相关的表有哪些",
                    message="与VPN相关的表有哪些?",
                    icon="public/icons/mobile-phone.svg",
                ),
                cl.Starter(
                    label="生成10条massdata.ADM_REL_MOBILE表的测试数据",
                    message="生成10条massdata.ADM_REL_MOBILE表的测试数据",
                    icon="public/icons/table.svg",
                ),
                cl.Starter(
                    label="使用select MD_ID from massdata.ADM_REL_MOBILE生成10条数据",
                    message="使用select MD_ID from massdata.ADM_REL_MOBILE生成10条数据",
                    icon="public/icons/database.svg",
                ),
                cl.Starter(
                    label="哪些表包含身份证号码字段",
                    message="哪些表包含身份证号码字段?",
                    icon="public/icons/fingerprint.svg",
                ),
            ],
        )
    ]


@cl.on_message
async def on_message(message: cl.Message):
    session_id = cl.context.session.id
    cl.user_session.set("session_id", session_id)

    # 如果没有初始化trace_uuid则初始化trace_token
    if traced_logger.get_trace_uuid() is None:
        trace_token = traced_logger.set_trace_uuid(trace_uuid=session_id)
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
        f"session_id={session_id} ip={cl.user_session.get('client_ip')} "
        f"message: {message.content}"
    )

    run_config = RunnableConfig(
        configurable={"thread_id": session_id},
        recursion_limit=50,
    )
    init_state = {
        "messages": HumanMessage(content=message.content.strip()),
        "max_retries": 5,
        "session_id": session_id,
        "client_ip": cl.user_session.get("client_ip"),
        "tool_call_result": None,
    }

    logger.trace(f"init_state={init_state}")

    async for event in main_graph.astream(
        init_state, run_config, stream_mode="updates", subgraphs=True
    ):
        event = cast(tuple[tuple, dict], event)
        logger.trace(f"event={event}")
        for node, state in event[1].items():
            logger.trace(f"current_node={node} current_state={state} ")
            processed = await handle_graph_event(
                node=node, state=state, run_config=run_config
            )
            # if node == "__interrupt__" and processed:
            if processed:
                logger.info(f"processed={processed} node={node} will break astream")
                break

    # 完成会话清空trace_uuid
    trace_token = cl.user_session.get("trace_token")
    if trace_token is None:
        logger.warning(
            f"session_id={session_id} trace_token not found, skipping reset."
        )
    else:
        # 这里 Pylance 知道 trace_token 是 Token 类型，且不是 None
        traced_logger.reset_trace_uuid(trace_token)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
