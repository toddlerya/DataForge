import json

import sqlglot
from sqlglot import exp


def find_column_origin(
    column_name: str,
    table_alias: str or None,
    context: dict,
    level: int = 0,
    debug: bool = False,
):
    """
    (全新重构版) 递归追踪一个字段的最终物理来源。

    Args:
        column_name: 要追踪的字段名。
        table_alias: 字段所属的表别名 (可能为None)。
        context: 当前查询层级的别名->表达式映射。
        level: (用于调试) 递归深度。
        debug: (用于调试) 是否打印调试信息。

    Returns:
        一个元组 (物理表名, 物理字段名) 或 None。
    """
    d_print = lambda msg: print("  " * level + msg) if debug else None

    d_print(
        f"🕵️‍♂️ Lvl {level}: Tracing '{table_alias}.{column_name if table_alias else column_name}'"
    )
    d_print(f"Context keys: {list(context.keys())}")

    source_expr = None
    clean_table_alias = table_alias.strip() if table_alias else None
    if clean_table_alias:
        # 情况A：字段有明确的表别名（如 a.ID），直接从上下文中查找
        source_expr = context.get(clean_table_alias)
        d_print(f"Found source for alias '{clean_table_alias}': {type(source_expr)}")
    elif len(context) == 1:
        # 情况B：字段没有表别名（如 ID），但当前上下文只有一个数据源，则字段归属于它
        source_alias = list(context.keys())[0]
        source_expr = context[source_alias]
        d_print(
            f"Column has no alias. Assigning to single source '{source_alias}': {type(source_expr)}"
        )

    if not source_expr:
        d_print(f"❌ Source not found for alias '{table_alias}'. Returning None.")
        return None

    # --- 递归终点：来源是物理表 ---
    if isinstance(source_expr, exp.Table):
        full_table_name = (
            f"{source_expr.db}.{source_expr.name}"
            if source_expr.db
            else source_expr.name
        )
        d_print(
            f"✅ Success! Found physical table: '{full_table_name}'. Column: '{column_name}'"
        )
        return full_table_name, column_name.strip()

    # --- 递归深入：来源是子查询 ---
    if isinstance(source_expr, exp.Subquery):
        d_print(f"Dive into subquery with alias '{source_expr.alias}'...")
        subquery_select = source_expr.this

        # 为子查询构建它自己的、全新的内部上下文
        inner_context = build_alias_context(subquery_select, debug)

        for proj in subquery_select.expressions:
            if proj.alias_or_name == column_name:
                # 找到了匹配的字段，现在对这个子查询内部的字段进行递归追踪
                inner_column_expr = proj.this
                if isinstance(inner_column_expr, exp.Column):
                    # 传入 proj.this (子查询中字段的原始表达式) 和新构建的内部上下文
                    return find_column_origin(
                        column_name=inner_column_expr.name,
                        table_alias=inner_column_expr.table,
                        context=inner_context,
                        level=level + 1,
                        debug=debug,
                    )
        d_print(
            f"❌ Column '{column_name}' not found in subquery's SELECT list. Returning None."
        )

    return None


def build_alias_context(query_expr: exp.Query, debug: bool = False) -> dict:
    """为当前查询层级构建别名->表达式的映射。"""
    context = {}
    sources = []
    if query_expr.args.get("from"):
        sources.append(query_expr.args["from"].this)
    for join in query_expr.args.get("joins", []):
        sources.append(join.this)

    for source in sources:
        if debug:
            print(
                f"  [ContextBuilder] Found source '{source.alias_or_name}' of type {type(source)}"
            )
        context[source.alias_or_name.strip()] = source
    return context


def parse_sql_lineage(sql: str, debug: bool = False) -> dict:
    """
    (主函数) 解析SQL，追踪所有SELECT字段的最终物理来源。
    """
    final_map = {}
    try:
        # 在解析前，先对整个SQL字符串进行一次清理，虽然不是必须，但是个好习惯
        cleaned_sql = " ".join(sql.split())
        parsed = sqlglot.parse_one(sql)
    except Exception as e:
        print(f"SQL 解析失败: {e}")
        return {}

    if debug:
        print("--- Building Root Context ---")
    root_context = build_alias_context(parsed, debug)
    if debug:
        print("--- Starting Column Trace ---")

    for projection in parsed.expressions:
        if not isinstance(projection, (exp.Alias, exp.Column)):
            continue

        column_expr = (
            projection.this if isinstance(projection, exp.Alias) else projection
        )

        if not isinstance(column_expr, exp.Column):
            continue

        origin = find_column_origin(
            column_name=column_expr.name,
            table_alias=column_expr.table,
            context=root_context,
            debug=debug,
        )

        if origin:
            table_name, original_column_name = origin
            if table_name not in final_map:
                final_map[table_name] = []

            final_map[table_name].append(
                {
                    "column": original_column_name,
                    "alias": projection.alias_or_name.strip(),
                    "comment": (
                        "".join(c.strip() for c in projection.comments)
                        if projection.comments
                        else None
                    ),
                }
            )

    return final_map


# --- 使用包含多个复杂子查询的 SQL 进行测试 ---
sql_query = """
SELECT
    user_info.uid, -- 来自用户子查询的用户ID
    user_info.reg_city, -- 来自注册信息表的城市
    latest_order.order_amt AS amount, -- 来自订单子查询的金额
    'some_literal' as literal_col
FROM
  (
    -- 子查询 'user_info'，内部包含JOIN
    SELECT
      u.id AS uid,
      r.city AS reg_city
    FROM db1.users u
    JOIN db1.registrations r ON u.id = r.user_id
    WHERE u.status = 'active'
  ) AS user_info
JOIN
  (
    -- 子查询 'latest_order'
    SELECT
      o.user_id,
      o.amount AS order_amt
    FROM db2.orders o
    WHERE o.order_date > '2025-01-01'
  ) AS latest_order
  ON user_info.uid = latest_order.user_id
"""

demo_sql = """SELECT
  a.ID AS ID, -- ID
  a.UPLOAD_AREA_CODE AS UPLOAD_AREA_CODE, -- 上报地市行政区划代码
  a.ISP_TYPE AS ISP_TYPE, -- 运营商信息代码
  a.CAPTURE_TIME AS CAPTURE_TIME, -- 截获时间
  a.RELE_DIRECTION_TYPE AS RELE_DIRECTION_TYPE, -- 认证关联方向
  a.DATA_SOURCE AS DATA_SOURCE, -- 数据来源
FROM
  (
    SELECT
      ID,
      UPLOAD_AREA_CODE,
      ISP_TYPE,
      CAPTURE_TIME,
      RELE_DIRECTION_TYPE,
      DATA_SOURCE
    FROM
      massdata.NB_MASS_RESOURCE_ARTICLE
  ) a
WHERE
  a.CAPTURE_TIME >= UNIX_TIMESTAMP () -1 * 24 * 3600"""

# 调用新函数并打印结果
lineage_info = parse_sql_lineage(demo_sql, True)
print(json.dumps(lineage_info, indent=4, ensure_ascii=False))
