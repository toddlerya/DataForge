import sqlglot
from sqlglot import exp


def extract_table_where_combinations(sql):
    """
    提取 SQL 中的表名和 WHERE 条件的组合
    :param sql: 输入的 SQL 字符串
    :return: 包含表名和 WHERE 条件的字典列表
    """
    # 解析 SQL
    parsed = sqlglot.parse_one(sql)

    # 存储结果
    results = []

    # 提取所有表名
    tables = [table.name for table in parsed.find_all(exp.Table)]

    # 提取所有 WHERE 条件
    where_conditions = []
    for where_node in parsed.find_all(exp.Where):
        condition = where_node.this.sql()
        where_conditions.append(condition)

    # 组合表名和 WHERE 条件
    for table in tables:
        results.append(
            {
                "table": table,
                "where_conditions": where_conditions,  # 假设所有 WHERE 条件都与表相关
            }
        )

    return results


# 示例 SQL
demo_sql = """INSERT INTO
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
  DOMAIN IS NOT NULL"""

# 提取表名和 WHERE 条件的组合
results = extract_table_where_combinations(demo_sql)
for result in results:
    print(f"表名: {result['table']}, WHERE 条件: {result['where_conditions']}")
