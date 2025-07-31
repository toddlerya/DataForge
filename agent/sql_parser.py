#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/9 15:45
# @Author   : guoqun X2590
# @FileName : sql_parser.py
# @Project  : DataForge
import re
from typing import Dict, List

import sqlglot
from sqlglot import exp, parse_one


def build_alias_context(query_expr: exp.Query | exp.Expression) -> dict:
    """为当前查询层级构建别名->表达式的映射"""
    context = {}
    # 查找FROM和JOIN子句中所有的数据源
    sources = []
    if query_expr.args.get("from"):
        from_exp = query_expr.args["from"]
        source_from = from_exp.this
        print(f"解析到的表名: {source_from.name}")  # 调试输出
        sources.append(source_from)
    for join in query_expr.args.get("joins", []):
        sources.append(join.this)

    for source in sources:
        context[source.alias_or_name] = source
    return context


def trace_column_origin(
        column_expr: exp.Column, alias_content: dict
) -> tuple[str, str] or None:
    """
    递归追踪一个字段表达式，直到找到最终的物理表
    :param column_expr: 要追踪的字段表达式(e.g., a.col1)
    :param alias_content: 当前查询层级的别名->表达式映射
    :return: 一个元组（物理表明，物理字段名）或None
    """
    print(f"column_expr: {column_expr} {type(column_expr)} {column_expr.name}")
    if not isinstance(column_expr, exp.Column):
        return None

    table_alias = column_expr.table
    column_name = column_expr.name

    if not table_alias:
        # 如果字段没有指定表别名，且当前上下文只有一个数据源，则归属于该数据源
        if len(alias_content) == 1:
            source_alias = list(alias_content.keys())[0]
            source_expr = alias_content[source_alias]
        else:
            # 无法确定来源，返回None
            return None
    else:
        source_expr = alias_content.get(table_alias)

    if not source_expr:
        return None

    # 情况1：来源是物理表，追踪结束
    if isinstance(source_expr, exp.Table):
        full_table_name = (
            f"{source_expr.db}.{source_expr.name}"
            if source_expr.db
            else source_expr.name
        )
        return full_table_name, column_name

    # 情况2：来源是子查询，需要递归深入
    if isinstance(source_expr, exp.Subquery):
        subquery_select = source_expr.this

        # 在子查询的SELECT列表中寻找匹配的字段
        for projection in subquery_select.expressions:
            if projection.alias_or_name == column_name:
                # 找到了匹配的字段，现在对这个子查询的内部字段进行递归追踪
                # 我们需要为子查询构建它自己的别名上下文
                inner_alias_context = build_alias_context(subquery_select)
                return trace_column_origin(projection.this, inner_alias_context)


def advanced_column_lineage_parser(sql: str) -> tuple[dict, Exception | None]:
    """
    高级SQL解析器，能够处理多层、多个子查询、并追踪列级血缘
    :param sql:
    :return:
    """
    try:
        parsed = sqlglot.parse_one(sql)
    except Exception as err:
        return {}, err

    final_map = {}

    # 1. 为最外层查询构建别名上下文
    if isinstance(parsed, exp.Select):
        root_context = build_alias_context(parsed)
    else:
        # 如不是Select节点，可能是个子查询或其他结构
        root_context = build_alias_context(parsed)

    print(f"root_context: {list(root_context.keys())[0]}")
    # 2. 遍历最外层SELECT的每个字段
    for projection in parsed.expressions:
        if isinstance(projection, exp.Star):
            # 跳过SELECT *的情况
            continue

        column_expr = projection.this
        if isinstance(column_expr, exp.Identifier):
            print(f"column_expr: {column_expr.alias_or_name}")
            # final_map[table_name].append(
            #     {
            #         "en_name": original_column_name,
            #         "alias_name": projection.alias_or_name,
            #         "comment": "".join(c.strip() for c in projection.comments)
            #         if projection.comments
            #         else "",
            #     }
            # )
        # 3. 对每个字段进行递归追踪
        origin = trace_column_origin(
            column_expr=column_expr, alias_content=root_context
        )
        if origin:
            table_name, original_column_name = origin
            if table_name not in final_map:
                final_map[table_name] = []

            final_map[table_name].append(
                {
                    "en_name": original_column_name,
                    "alias_name": projection.alias_or_name,
                    "comment": "".join(c.strip() for c in projection.comments)
                    if projection.comments
                    else "",
                }
            )

    return final_map, None


def parse_simple_select(sql: str) -> tuple[bool, str, dict]:
    """
    解析单表SELECT
    :param sql:
    :return:
    """
    # 去除多余空白，方便正则抓取行尾注释
    sql = " ".join(sql.split())

    # 解析语法树
    tree = parse_one(sql, dialect="spark")
    if not isinstance(tree, exp.Select):
        return False, "仅支持解析SELECT语句", {}

    # 拒绝select *
    for sel in tree.expressions:
        if isinstance(sel, exp.Star):
            return False, "不支持SELECT *语句，请显示提供字段列表", {}

    # 找表，只支持单表
    from_ = tree.find(exp.From)
    if not from_:
        return False, "找不到FROM子句", {}
    table_expr = from_.this
    if isinstance(table_expr, exp.Table):
        real_table = table_expr.name
    else:
        return False, "暂时只支持单张物理表", {}

    # 收集字段信息
    columns = []
    for sel in tree.expressions:
        # 原字段名
        col_name = sel.name if isinstance(sel, exp.Column) else str(sel)
        # 别名
        alias_name = sel.alias_or_name if sel.alias else col_name
        # 行尾注释, 在SQL中出现--的注释
        comment = ""
        expr_sql = sel.sql()
        pattern = re.escape(expr_sql) + r"(?:\s*(--[^\r\n]*))?(?:,|\sFROM\b)"
        m = re.search(pattern, sql, flags=re.IGNORECASE)
        if m and m.group(1):
            comment = m.group(1).lstrip("--").strip()
        columns.append({
            "en_name": col_name,
            "alias_name": alias_name,
            "comment": comment
        })
    return True, "ok", {real_table: columns}


if __name__ == "__main__":
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
             from  massdata.NB_MASS_RESOURCE_ARTICLE a where a.CAPTURE_TIME>=UNIX_TIMESTAMP()-1*24*3600 AND
             a.APP_TYPE='100000595'       and a.AUTH_ACCOUNT<>''"""

    demo_sql_2 = """select F859 as F2079, F860 as F2085, F861 as F2091, F862 as F2097, STR_SRC_IP as F2103, F863 as F2109, STR_DST_IP as F2115, F864 as F2121, F865 as F2127, F866 as F2133, F867 as F2139, F868 as F2145, F869 as F2151, F870 as F2157, F871 as F2163, F872 as F2169, F873 as F2175, F874 as F2181, F875 as F2187, F876 as F2193, F877 as F2199, PASSWORD as F2205, TITLE as 
F2211, ARTICLE_ID as F2217, CONTENT_S as F2223, F878 as F2229, F879 as F2235 from massdata.NB_MASS_RESOURCE_REGISTER"""

    demo_sql_3 = "select xuhao from phy_adm_vmodel_res_ce_shi_wen_jian_shang_chuan_001c4b40999f016c1ad8d4581dec6b18"

    import json

    result, err = advanced_column_lineage_parser(demo_sql_3)
    print(err)
    print(result)
    print(json.dumps(result, ensure_ascii=False))

    print("=== 使用sqlglot解析 ===")
    parsed = parse_simple_select(demo_sql_3)
    print(parsed)
