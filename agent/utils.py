#!/usr/bin/env python
# coding: utf-8
# @File    :   utils.py
# @Time    :   2025/05/09 15:23:17
# @Author  :   toddlerya
# @Desc    :   None

import json
from typing import Any, List, Dict

import sqlglot
import aiofiles
from pydantic import BaseModel, create_model, Field


async def save_json_data_async(save_json_path, fake_data):
    async with aiofiles.open(save_json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(fake_data, ensure_ascii=False, indent=2))


def create_model_from_dict(
        data: dict, model_name: str = "row_field_model"
) -> type[BaseModel]:
    # 构建字段注解
    annotations = {key: (Any, None) for key in data}
    model = create_model(
        model_name,
        **annotations,
    )
    return model


FIELD_TYPE_MAP = {"int": int, "string": str}


def create_table_model(table_name: str, fields: list[dict]):
    """
    创建输出表输出模型定义
    Args:
        table_name:
        fields:

    Returns:

    """
    field_definitions = {}
    for field in fields:
        field_name = field.get("en_name")
        field_type = FIELD_TYPE_MAP.get(field.get("field_type"), str)
        field_kwargs = {}

        field_definitions[field_name] = (field_type, Field(**field_kwargs))

    return create_model(table_name, **field_definitions)


def build_main_model(table_models: Dict[str, List[BaseModel]] | List):
    """
    构建输出数据结构主模型
    Args:
        table_models:

    Returns:

    """
    main_model_fields = {
        table_name: (List[table_model])
        for table_name, table_model in table_models.items()
    }
    return create_model("LLMOutputData", **main_model_fields)


def sqlglot_parse_sql(sql: str) -> tuple[Dict[str, List[str]], Exception | None]:
    """
    使用 sqlglot 解析SQL语句，提取表名、查询列和WHERE条件

    参数:
        sql: 要解析的SQL字符串

    返回:
        包含解析结果的字典，键为'tables', 'columns', 'conditions'
    """
    try:
        parsed = sqlglot.parse_one(sql)
    except Exception as err:
        return {}, err

    table_column_map = dict()
    table_aliases = dict()

    # 1. 识别所有数据源（包括物理表和子查询）的别名
    # 遍历FROM和JOIN子句中所有数据源
    for source in parsed.find_all(sqlglot.exp.From, sqlglot.exp.Join):
        expression = source.this

        # 情况1：数据源是普通表
        if isinstance(expression, sqlglot.exp.Table):
            full_table_name = f"{expression.db}.{expression.name}" if expression.db else expression.name
            table_aliases[expression.alias_or_name] = full_table_name

        # 情况2：数据源是子查询（Derived Table）
        elif isinstance(expression, sqlglot.exp.Subquery):
            subquery_alias = expression.alias_or_name
            # 在子查询内部查找真实的物理表
            # 注意：此简化逻辑假设子查询内部有一个主要物理表
            inner_table = expression.find

    for table in parsed.find_all(sqlglot.exp.Table):
        full_table_name = f"{table.db}.{table.name}" if table.db else table.name
        table_aliases[table.alias_or_name] = full_table_name
    print(f"table_aliases: {table_aliases}")

    # 2. 比那里查询中所有的SELECT表达式
    for projection in parsed.find_all(sqlglot.exp.Select):
        for expression in projection.expressions:
            # 跳过SELECT *的情况
            if isinstance(expression, sqlglot.exp.Star):
                continue

            column_expr = expression.this
            column_alias = expression.alias if isinstance(expression, sqlglot.exp.Alias) else None

            # 只处理字段表达式
            if isinstance(column_expr, sqlglot.exp.Column):
                column_name = column_expr.name
                table_alias = column_expr.table

                # 提取注释
                comments = [comment.strip() for comment in expression.comments] if expression.comments else []
                comment = comments[0] if comments else None

                print(
                    f"table_alias: {table_alias} column_name: {column_name} table_alias: {table_alias} comment: {comment} ")

                # 确定字段所属的表
                if table_alias in table_aliases:
                    table_name = table_aliases[table_alias]
                    if table_name not in table_column_map:
                        table_column_map[table_name] = []

                    table_column_map[table_name].append(
                        {
                            "column": column_name,
                            "alias": column_alias,
                            "comment": comment
                        }
                    )
    return table_column_map, None


if __name__ == "__main__":
    # from pydantic import BaseModel
    #
    # data1 = {
    #     "CREATE_TIME": "",
    #     "LAST_TIME": "",
    #     "REGISTRANT": "",
    # }
    #
    # data2 = {
    #     "MD_ID": "",
    #     "DOMAIN": "",
    #     "REGISTRY_DOMAIN_ID": "",
    # }
    #
    # DynamicModel1 = create_model_from_dict(data1)
    # print(DynamicModel1())
    # print(DynamicModel1.model_json_schema())
    # print(DynamicModel1.__annotations__)

    demo_sql_1 = """select 
            a.ID as ID, -- ID
            a.UPLOAD_AREA_CODE as UPLOAD_AREA_CODE, -- 上报地市行政区划代码
            a.ISP_TYPE as ISP_TYPE, -- 运营商信息代码
            a.CAPTURE_TIME as CAPTURE_TIME, -- 截获时间
            a.RELE_DIRECTION_TYPE as RELE_DIRECTION_TYPE, -- 认证关联方向
            a.DATA_SOURCE as DATA_SOURCE, -- 数据来源
            a.SRC_IP as SRC_IP, -- 源IP
            a.DST_IP as DST_IP, -- 宿IP
            a.SRC_IPV6 as SRC_IPV6, -- 源IPv6
            a.DST_IPV6 as DST_IPV6, -- 宿IPv6
            a.SRC_IPID_S as SRC_IPID_S, -- 源IPID
            a.DST_IPID_S as DST_IPID_S, -- 宿IPID
            a.SRC_PORT as SRC_PORT, -- 源端口
            a.DST_PORT as DST_PORT, -- 宿端口
            a.APP_TYPE as APP_TYPE, -- 应用类型
            a.ACTION_TYPE as ACTION_TYPE, -- 动作类别
            a.TOOL_TYPE as TOOL_TYPE, -- 上网工具类型代码
            a.TOOL_NAME as TOOL_NAME, -- 工具名称
            a.MOBILE as MOBILE, -- 无线认证手机号码
            a.AUTH_ACCOUNT as AUTH_ACCOUNT, -- 上网认证帐号
            a.AUTH_TYPE as AUTH_TYPE, -- 上网认证类型
            a.DOMAIN as DOMAIN, -- 域名
            a.URL as URL, -- URL
            a.USERID as USERID, -- 用户ID
            a.USERNAME as USERNAME, -- 用户名
            a.BIND_MOBILE as BIND_MOBILE, -- 用户绑定的手机号码
            a.BIND_EMAIL as BIND_EMAIL, -- 绑定邮箱
            a.REALNAME as REALNAME, -- 姓名
            a.NICKNAME as NICKNAME, -- 昵称
            a.SEND_ACCOUNT as SEND_ACCOUNT, -- 发送者账号
            a.SEND_USERID as SEND_USERID, -- 发送者用户ID
            a.SEND_USERNAME as SEND_USERNAME, -- 发送者用户名
            a.SEND_NICKNAME as SEND_NICKNAME, -- 发送者昵称
            a.SEND_TIME as SEND_TIME, -- 发送时间
            a.CONTENT_S as CONTENT_S, -- 内容
            a.REPLY_CONTENT_S as REPLY_CONTENT_S, -- 评价/评论内容
            a.FILE_NAME as FILE_NAME, -- 文件名称
            a.MAIN_FILE_PATH as MAIN_FILE_PATH, -- 全文路径
            a.PASSWORD as PASSWORD -- 密码
         from ( select DOMAIN,URL,USERID,USERNAME,BIND_MOBILE,BIND_EMAIL,REALNAME,NICKNAME,SEND_ACCOUNT,SEND_USERID,SEND_USERNAME,SEND_NICKNAME,SEND_TIME,CONTENT_S,REPLY_CONTENT_S,FILE_NAME,MAIN_FILE_PATH,PASSWORD,ID,UPLOAD_AREA_CODE,ISP_TYPE,CAPTURE_TIME,RELE_DIRECTION_TYPE,DATA_SOURCE,SRC_IP,DST_IP,SRC_IPV6,DST_IPV6,SRC_IPID_S,DST_IPID_S,SRC_PORT,DST_PORT,APP_TYPE,ACTION_TYPE,TOOL_TYPE,TOOL_NAME,MOBILE,AUTH_ACCOUNT,AUTH_TYPE from massdata.NB_MASS_RESOURCE_ARTICLE) a where a.CAPTURE_TIME>=UNIX_TIMESTAMP()-1*24*3600 AND
         a.APP_TYPE='100000595'
         and a.AUTH_ACCOUNT<>''"""

    print("=== 使用sqlglot解析 ===")
    parse_result = sqlglot_parse_sql(demo_sql_1)
    print(parse_result)
