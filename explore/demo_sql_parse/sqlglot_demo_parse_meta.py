import json

import sqlglot
import sqlglot.expressions

# 定义SQL语句
sql = """
INSERT INTO
  fmdbmeta.ADM_DOMAIN_KNOWLEDGE
SELECT
  daw_udf_md5(
    DOMAIN,
    '\t',
    FIRST_CATEGORY,
    '\t',
    SECOND_CATEGORY,
    '\t',
    CATEGORY_RULE
  ) AS MD_ID,
  DOMAIN AS DOMAIN,
  FIRST_CATEGORY AS FIRST_CATEGORY,
  SECOND_CATEGORY AS SECOND_CATEGORY,
  CATEGORY_RULE AS CATEGORY_RULE,
  UPDATETIME AS UPDATETIME,
  CREATOR AS CREATOR,
  UPLOAD_AREA_CODE AS UPLOAD_AREA_CODE
FROM(
    SELECT
      daw_domain_udf_get_format_domain(DOMAIN, cast_to_int('40')) AS DOMAIN,
      '0002' AS FIRST_CATEGORY,
      daw_udf_generic_dic_map(
        string_concat(FIRST_CATEGORY, SECOND_CATEGORY, ''),
        'zcbcategory.dic'
      ) as SECOND_CATEGORY,
      '1' AS CATEGORY_RULE,
      CREATE_TIME AS UPDATETIME,
      null as CREATOR,
      cast_to_int(local_city_code()) as UPLOAD_AREA_CODE
    FROM
      massdata.ADM_DOMAIN_CATEGORY
    where
      FIRST_CATEGORY = '003'
      and (
        SECOND_CATEGORY = '0012'
        or SECOND_CATEGORY = '0013'
        or SECOND_CATEGORY = '0014'
        or SECOND_CATEGORY = '0015'
        or SECOND_CATEGORY = '0016'
        or SECOND_CATEGORY = '0031'
      )
    UNION ALL
    SELECT
      daw_domain_udf_get_format_domain(
        string_concat(SERVER_IPV4_STR, PORT, ':'),
        cast_to_int('40')
      ) AS DOMAIN,
      '0008' AS FIRST_CATEGORY,
      '00080001' SECOND_CATEGORY,
      '1' AS CATEGORY_RULE,
      cast_to_long(UPDATE_TIME) AS UPDATETIME,
      null as CREATOR,
      cast_to_int(local_city_code()) as UPLOAD_AREA_CODE
    FROM
      fmdbmeta.DAW_ODS_PROXY_URL_COLLECT
    WHERE
      STATUS = '1'
  ) t
WHERE
  DOMAIN IS NOT NULL
"""

# 解析SQL
parsed_sql = sqlglot.parse_one(sql, read="spark")

# 提取表信息
tables_info = []


def extract_table_info(select_node):
    table_info = {
        "table_name": None,
        "selected_columns": [],
        "filters": [],
        "udf_functions": [],
    }

    # 获取表名
    if isinstance(select_node, sqlglot.expressions.Select):
        from_clause = select_node.args.get("from")
        if from_clause:
            table_expr = from_clause.this
            if isinstance(table_expr, sqlglot.expressions.Table):
                table_info["table_name"] = table_expr.sql()

        # 提取查询字段和UDF函数
        for expr in select_node.expressions:
            if isinstance(expr, sqlglot.expressions.Alias):
                table_info["selected_columns"].append(expr.alias)
                # 检查表达式是否包含UDF函数
                if isinstance(expr.this, sqlglot.expressions.Func):
                    table_info["udf_functions"].append(expr.this.sql())
            elif isinstance(expr, sqlglot.expressions.Column):
                table_info["selected_columns"].append(expr.name)

        # 提取过滤条件
        where_clause = select_node.args.get("where")
        if where_clause:
            table_info["filters"].append(where_clause.sql())

    return table_info


# 遍历子查询
for subquery in parsed_sql.find_all(sqlglot.expressions.Select):
    tables_info.append(extract_table_info(subquery))

# 输出JSON格式结果
output_json = json.dumps(tables_info, indent=2, ensure_ascii=False)
print(output_json)
