#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/10 16:43
# @Author   : guoqun X2590
# @FileName : sql_parse.py
# @Project  : AIUsage

import json

import sqlglot

sql = r"""-- ************************************************************
-- SQL功能描述：IP域名求全全量过滤泛域名
-- SQL调度策略：周期
-- 输入表策略：
-- 1、fmdbmeta.DAW_DOMAIN_IP_TOTAL_MERGE ( 域名IP关系求全增量表 )：增量数据
-- 2、massdata.DAW_DOMAIN_IP_ALL_MERGE ( 域名IP关系求全总量中间表 )：全量数据
-- 输出表策略：
-- fmdbmeta.DAW_DOMAIN_IP_ALL_MERGE ( 域名IP关系求全总量中间表 )：全量数据
-- 作者：X7058
-- 更改记录
-- 1、X7058，20231123创建；
-- ************************************************************
INSERT INTO
  fmdbmeta."ADM_DOMAIN_IP_TOTAL"
SELECT
  MD_ID,
  IP,
  DOMAIN,
  null as IP_LOCATION,
  FIRST_TIME,
  LAST_TIME,
  CCOUNT,
  null as ISP_TYPE,
  TCOUNT,
  null as SYNC_FLAG
from
  (
    SELECT
      c.MD_ID,
      c.IP,
      c.DOMAIN,
      c.FIRST_TIME,
      c.LAST_TIME,
      c.CCOUNT,
      c.TCOUNT
    from
      (
        SELECT
          a.MD_ID,
          a.IP,
          a.DOMAIN,
          a.FIRST_TIME,
          a.LAST_TIME,
          a.CCOUNT,
          a.TCOUNT
        from
          fmdbmeta."DAW_DOMAIN_IP_ALL_MERGE" a
          left join fmdbmeta."DAW_DOMAIN_SEC_TH_FYM" b on daw_domain_udf_get_level_only_domain(a.DOMAIN, cast_to_int('2')) = b.DOMAIN
        where
          b.DOMAIN is null
      ) c
      left join fmdbmeta."DAW_DOMAIN_SEC_TH_FYM" d on daw_domain_udf_get_level_only_domain(c.DOMAIN, cast_to_int('3')) = d.DOMAIN
    where
      d.DOMAIN is null
  ) t
"""

sql_1 = """INSERT INTO
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


sql_2 = """INSERT INTO
  fmdbmeta.ADM_DOMAIN_WHOIS
SELECT
  daw_udf_md5(DOMAIN) AS MD_ID,
  DOMAIN,
  daw_domain_udaf_get_top_flag_fields(REGISTRY_DOMAIN_ID, cast_to_int('1'), LAST_TIME) AS REGISTRY_DOMAIN_ID,
  daw_domain_udaf_get_top_flag_fields(
    REGISTRAR_WHOIS_SERVER,
    cast_to_int('1'),
    LAST_TIME
  ) AS REGISTRAR_WHOIS_SERVER,
  daw_domain_udaf_get_top_flag_fields(REGISTRAR_URL, cast_to_int('1'), LAST_TIME) AS REGISTRAR_URL,
  cast_to_long(
    daw_domain_udaf_get_top_flag_fields(
      cast_to_str(UPDATED_TIME),
      cast_to_int('1'),
      LAST_TIME
    )
  ) AS UPDATED_TIME,
  cast_to_long(
    daw_domain_udaf_get_top_flag_fields(
      cast_to_str(CREATION_TIME),
      cast_to_int('1'),
      LAST_TIME
    )
  ) AS CREATION_TIME,
  cast_to_long(
    daw_domain_udaf_get_top_flag_fields(
      cast_to_str(EXPIRATION_TIME),
      cast_to_int('1'),
      LAST_TIME
    )
  ) AS EXPIRATION_TIME,
  daw_domain_udaf_get_top_flag_fields(REGISTRAR, cast_to_int('1'), LAST_TIME) AS REGISTRAR,
  daw_domain_udaf_get_top_flag_fields(REGISTRAR_IANA_ID, cast_to_int('1'), LAST_TIME) AS REGISTRAR_IANA_ID,
  daw_domain_udaf_get_top_flag_fields(
    REGISTRAR_CONTACT_EMAIL,
    cast_to_int('1'),
    LAST_TIME
  ) AS REGISTRAR_CONTACT_EMAIL,
  daw_domain_udaf_get_top_flag_fields(
    REGISTRAR_CONTACT_PHONE,
    cast_to_int('1'),
    LAST_TIME
  ) AS REGISTRAR_CONTACT_PHONE,
  daw_domain_udaf_get_top_flag_fields(
    REGISTRANT_ORGANIZATION,
    cast_to_int('1'),
    LAST_TIME
  ) AS REGISTRANT_ORGANIZATION,
  daw_domain_udaf_get_top_flag_fields(REGISTRANT_PROVINCE, cast_to_int('1'), LAST_TIME) AS REGISTRANT_PROVINCE,
  daw_domain_udaf_get_top_flag_fields(REGISTRANT_COUNTRY, cast_to_int('1'), LAST_TIME) AS REGISTRANT_COUNTRY,
  daw_domain_udaf_get_top_flag_fields(REGISTRANT_EMAIL, cast_to_int('1'), LAST_TIME) AS REGISTRANT_EMAIL,
  daw_domain_udaf_get_top_flag_fields(ADMIN_ORGANIZATION, cast_to_int('1'), LAST_TIME) AS ADMIN_ORGANIZATION,
  daw_domain_udaf_get_top_flag_fields(ADMIN_PROVINCE, cast_to_int('1'), LAST_TIME) AS ADMIN_PROVINCE,
  daw_domain_udaf_get_top_flag_fields(ADMIN_COUNTRY, cast_to_int('1'), LAST_TIME) AS ADMIN_COUNTRY,
  daw_domain_udaf_get_top_flag_fields(ADMIN_EMAIL, cast_to_int('1'), LAST_TIME) AS ADMIN_EMAIL,
  daw_domain_udaf_get_top_flag_fields(TECH_ORGANIZATION, cast_to_int('1'), LAST_TIME) AS TECH_ORGANIZATION,
  daw_domain_udaf_get_top_flag_fields(TECH_PROVINCE, cast_to_int('1'), LAST_TIME) AS TECH_PROVINCE,
  daw_domain_udaf_get_top_flag_fields(TECH_COUNTRY, cast_to_int('1'), LAST_TIME) AS TECH_COUNTRY,
  daw_domain_udaf_get_top_flag_fields(TECH_EMAIL, cast_to_int('1'), LAST_TIME) AS TECH_EMAIL,
  min_value_long(CREATE_TIME) AS CREATE_TIME,
  max_value_long(LAST_TIME) AS LAST_TIME
FROM(
    SELECT
      daw_domain_udf_get_level_only_domain(DOMAIN, cast_to_int('2')) AS DOMAIN,
      REGISTRY_DOMAIN_ID,
      REGISTRAR_WHOIS_SERVER,
      REGISTRAR_URL,
      UPDATED_TIME,
      CREATION_TIME,
      EXPIRATION_TIME,
      REGISTRAR,
      REGISTRAR_IANA_ID,
      REGISTRAR_CONTACT_EMAIL,
      REGISTRAR_CONTACT_PHONE,
      REGISTRANT_ORGANIZATION,
      REGISTRANT_PROVINCE,
      REGISTRANT_COUNTRY,
      REGISTRANT_EMAIL,
      ADMIN_ORGANIZATION,
      ADMIN_PROVINCE,
      ADMIN_COUNTRY,
      ADMIN_EMAIL,
      TECH_ORGANIZATION,
      TECH_PROVINCE,
      TECH_COUNTRY,
      TECH_EMAIL,
      COLL_TIME as CREATE_TIME,
      UPD_TIME as LAST_TIME
    FROM
      fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS
    where
      daw_udf_check_not_empty(
        REGISTRY_DOMAIN_ID,
        REGISTRAR_WHOIS_SERVER,
        REGISTRAR_URL,
        REGISTRAR
      ) != '0000'
    UNION ALL
    SELECT
      DOMAIN,
      REGISTRY_DOMAIN_ID,
      REGISTRAR_WHOIS_SERVER,
      REGISTRAR_URL,
      UPDATED_TIME,
      CREATION_TIME,
      EXPIRATION_TIME,
      REGISTRAR,
      REGISTRAR_IANA_ID,
      REGISTRAR_CONTACT_EMAIL,
      REGISTRAR_CONTACT_PHONE,
      REGISTRANT_ORGANIZATION,
      REGISTRANT_PROVINCE,
      REGISTRANT_COUNTRY,
      REGISTRANT_EMAIL,
      ADMIN_ORGANIZATION,
      ADMIN_PROVINCE,
      ADMIN_COUNTRY,
      ADMIN_EMAIL,
      TECH_ORGANIZATION,
      TECH_PROVINCE,
      TECH_COUNTRY,
      TECH_EMAIL,
      CREATE_TIME,
      LAST_TIME
    FROM
      fmdbmeta.ADM_DOMAIN_WHOIS
  ) t
where
  DOMAIN is not null
GROUP BY
  DOMAIN
"""

# 解析sql
parsed_sql = sqlglot.parse_one(sql_2)

# print(f"parsed_sql===\n{repr(parsed_sql)}")

# 提取表信息
tables_info = []


def extract_table_info(select_node):
    table_info = {
        "tables_name": None,
        # "selected_columns": [],
        "filters": [],
        # "udf_functions": [],
        "join_conditions": [],
        "union_conditions": [],
    }

    # 获取表名
    if isinstance(select_node, sqlglot.expressions.Select):
        from_clause = select_node.args.get("from")
        if from_clause:
            table_expr = from_clause.this
            if isinstance(table_expr, sqlglot.expressions.Table):
                table_info["tables_name"] = table_expr.sql()

        # 提取查询字段和UDF函数
        # for expr in select_node.expressions:
        #     if isinstance(expr, sqlglot.expressions.Alias):
        # table_info["selected_columns"].append(expr.alias)
        # 检查是否包含udf函数
        # if isinstance(expr.this, sqlglot.expressions.Func):
        #     table_info["udf_functions"].append(expr.this.sql())
        # elif isinstance(expr, sqlglot.expressions.Column):
        #     table_info["selected_columns"].append(expr.name)

        # 提取过滤条件
        where_clause = select_node.args.get("where")
        if where_clause:
            table_info["filters"].append(where_clause.sql())

        # 提取JOIN条件
        joins = select_node.find_all(sqlglot.expressions.Join)
        for join in joins:
            join_condition = join.args.get("on")
            if join_condition:
                table_info["join_conditions"].append(join_condition.sql())
        # 提取UNION条件
        unions = select_node.find_all(sqlglot.expressions.Union)
        for union in unions:
            if hasattr(union, "distinct"):
                table_info["union_conditions"].append(
                    "UNION" if union.distinct else "UNION ALL"
                )
            else:
                table_info["union_conditions"].append(
                    "UNION" if union.args.get("distinct", True) else "UNION ALL"
                )
    return table_info


# 遍历子查询
for subquery in parsed_sql.find_all(sqlglot.expressions.Select):
    tables_info.append(extract_table_info(subquery))

output_json = json.dumps(tables_info, indent=2, ensure_ascii=False)
print(output_json)
