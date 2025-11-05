#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/28 14:58
# @Author   : guoqun X2590
# @FileName : app.py.py
# @Project  : DataForge


import json
import time
from datetime import datetime

import chainlit as cl
from dotenv import load_dotenv
from loguru import logger

from agent.state import TableMetadataSchema
from common.initialization import init_env, setup_logging
from config import FMDB_INSERT_SQL_PATH, PROJECT_PATH
from utils.log import LogManager, TracedLogger

log_config = LogManager(
    base_path=str(PROJECT_PATH.absolute()),
    log_path="logs",
    log_name="DataForgeFMDBInsertSQLGenApp.log",
    file_log_level="INFO",
)
setup_logging(log_config.get_config().get("handlers"))
traced_logger = TracedLogger()
init_env()
# 加载 .env 文件
load_dotenv(PROJECT_PATH.absolute())

global table_meta_data
global dg_lines_data


@cl.on_chat_start
async def start_chat():  # noqa: C901
    session_id = cl.context.session.id
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

    text_content = f"""{cl.user_session.get("client_ip")}，您好！我是您的测试数据生成助手\n\n
上传你的表元数据配置JSON和DG生成的数据TXT文件"""  # noqa: E501
    elements = [cl.Text(name="说明", content=text_content, display="inline")]
    await cl.Message(author="Assistant", content="功能介绍", elements=elements).send()

    # 等待用户上传表元数据信息
    table_meta_json_files = None
    while table_meta_json_files is None:
        table_meta_json_files = await cl.AskFileMessage(
            content="请上传表元数据JSON配置文件",
            accept={"text/plain": [".json"]},
            max_size_mb=5,
            max_files=1,
            timeout=600,
        ).send()
    table_meta_json_file = table_meta_json_files[0]
    try:
        with open(
            table_meta_json_file.path, mode="r", encoding="utf-8"
        ) as table_meta_file:
            upload_table_meta_data = json.load(table_meta_file)
            table_meta_data: TableMetadataSchema = TableMetadataSchema(
                **upload_table_meta_data
            )
            cl.user_session.set("table_meta_data", table_meta_data)
            cl.user_session.set("col_number", len(table_meta_data.raw_fields_info))
            await cl.Message(
                content=f"表名称为: {table_meta_data.table_en_name}, 有{len(table_meta_data.raw_fields_info)}列字段"  # noqa: E501
            ).send()
    except Exception as err:
        await cl.Message(
            content=f"上传的表元数据文件: {table_meta_json_file.name} 解析校验异常: {err}"  # noqa: E501
        ).send()
    else:
        await cl.Message(
            content=f"上传的表元数据文件: {table_meta_json_file.name} 解析校验通过"
        ).send()

    # 等待用户上传DG生成的txt数据文件
    dg_table_data_txt_files = None
    while dg_table_data_txt_files is None:
        dg_table_data_txt_files = await cl.AskFileMessage(
            content="请上传DG生成的表数据txt文件",
            accept={"text/plain": [".txt"]},
            max_size_mb=10,
            max_files=5,
        ).send()
    dg_lines_data = []
    for dg_table_data_txt_file in dg_table_data_txt_files:
        try:
            with open(
                dg_table_data_txt_file.path, mode="r", encoding="utf-8"
            ) as data_txt_file:
                raw_lines_data = data_txt_file.readlines()
                cleaned_lines_data = [
                    line.rstrip("\n").split("\t") for line in raw_lines_data
                ]
                lines_col_count = [len(line) for line in cleaned_lines_data]
                if len(set(lines_col_count)) == 1 and list(set(lines_col_count))[
                    0
                ] == cl.user_session.get("col_number"):
                    dg_lines_data.extend(cleaned_lines_data)
                else:
                    await cl.Message(
                        content=f"上传的数据文件: {dg_table_data_txt_file.name} 解析校验异常, 列数量不一致, 期望{cl.user_session.get('col_number')}列, 实际{list(set(lines_col_count))}列"  # noqa: E501
                    ).send()
                    continue
        except Exception as err:
            await cl.Message(
                content=f"上传的数据文件: {dg_table_data_txt_file.name} 读取异常: {err}"
            ).send()
        else:
            await cl.Message(
                content=f"上传的数据文件: {dg_table_data_txt_file.name} 读取校验通过, 共{len(cleaned_lines_data)}条数据"  # noqa: E501
            ).send()
    await cl.Message(
        content=f"{len(dg_table_data_txt_files)}个文件，共计读取到{len(dg_lines_data)}条数据"
    ).send()
    cl.user_session.set("dg_lines_data", dg_lines_data)

    partition_res = await cl.AskUserMessage(
        content="是否存在分区字段(p1,p2,p3,p4)，请回答Y或N", timeout=600
    ).send()
    if partition_res:
        partition_answer = partition_res.get("output", "")
        if partition_answer.upper() == "Y":
            cl.user_session.set("partiton", True)
        else:
            cl.user_session.set("partiton", False)
    else:
        cl.user_session.set("partiton", False)

    # 开始生成
    partition_sql = ""
    if cl.user_session.get("partiton"):
        current_p3_timestamp = int(time.time()) - 3600
        current_p4_date = datetime.strftime(datetime.now(), "%Y%m%d")
        partition_sql = f"PARTITION (p1='final', p2='update', p3={current_p3_timestamp}, p4={current_p4_date}) \n"  # noqa: E501

    logger.info(
        f"session_id={cl.context.session.id} ip={cl.user_session.get('client_ip')} "
        f"table_meta_data={table_meta_data.model_dump_json()}"
    )

    # 开始拼接SQL
    insert_sql_prefix = f"INSERT INTO {table_meta_data.table_en_name} \n"
    if partition_sql:
        insert_sql_prefix += partition_sql
    insert_sql_prefix += "VALUES \n"
    if len(dg_lines_data) <= 50:
        insert_sql_values = ""
        for index, line in enumerate(dg_lines_data, start=1):
            line_value_tuple = tuple(line)
            insert_sql_values += str(line_value_tuple)
            if index < len(dg_lines_data):
                insert_sql_values += ", \n"
            else:
                insert_sql_values += ";"
        await cl.Message(
            content=insert_sql_prefix + insert_sql_values, language="sql"
        ).send()
    else:
        # 数据量太大，生成sql分片
        chunk_size = 2000
        dg_line_data_chunks = [
            dg_lines_data[i : i + chunk_size]
            for i in range(0, len(dg_lines_data), chunk_size)
        ]
        await cl.Message(
            content=(
                f"共计有{len(dg_lines_data)}条数据，按照{chunk_size}条数据一组，分为{len(dg_line_data_chunks)}个SQL文件"
            ),
        ).send()
        for chunk_index, each_dg_line_data_chunk in enumerate(
            dg_line_data_chunks, start=1
        ):
            insert_sql_values = ""
            for index, line in enumerate(each_dg_line_data_chunk, start=1):
                line_value_tuple = tuple(line)
                insert_sql_values += str(line_value_tuple)
                if index < len(dg_lines_data):
                    insert_sql_values += ", \n"
                else:
                    insert_sql_values += ";"
            insert_sql_file_path = FMDB_INSERT_SQL_PATH.joinpath(
                f"fmdb_insert_{session_id}_chunk_{chunk_index}.sql"
            ).absolute()
            logger.info(f"fmdb_insert_sql_path: {insert_sql_file_path}")
            with open(insert_sql_file_path, mode="w", encoding="utf-8") as w:
                w.write(insert_sql_prefix + insert_sql_values)
            download_fmdb_insert_sql_element = cl.File(
                name=f"{insert_sql_file_path.name}",
                path=str(insert_sql_file_path),
                display="inline",
            )
            await cl.Message(
                content=(f"FMDB INSERT SQL FILE CHUNK {chunk_index}"),
                elements=[download_fmdb_insert_sql_element],
            ).send()

    # 完成会话清空trace_uuid
    trace_token = cl.user_session.get("trace_token")
    if trace_token is None:
        logger.warning(
            f"session_id={session_id} trace_token not found, skipping reset."
        )
    else:
        # 这里 Pylance 知道 trace_token 是 Token 类型，且不是 None
        logger.trace(
            f"traced_logger.reset_trace_uuid(trace_token) trace_uuid={session_id}"
        )
        traced_logger.reset_trace_uuid(trace_token)


if __name__ == "__main__":
    from chainlit.cli import run_chainlit

    run_chainlit(__file__)
