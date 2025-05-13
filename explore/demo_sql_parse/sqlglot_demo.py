from sqlglot import exp, parse_one

# print all column references (a and b)
# for column in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Column):
#     print(column.alias_or_name)

# find all projections in select statements (a and c)
# for select in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Select):
#     for projection in select.expressions:
#         print(projection.alias_or_name)


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

# 查找所有的表名称
print("==== 所有的表名称 ====")
for table in parse_one(demo_sql, read="spark").find_all(exp.Table):
    print(table.name)


# 查找所有列引用
print("==== 所有的列引用 ====")
for column in parse_one(demo_sql, read="spark").find_all(exp.Column):
    print(column.alias_or_name)

# 查找所有udf函数
print("==== 所有udf函数 ====")
for function in parse_one(demo_sql, read="spark").find_all(exp.Func):
    print(function.name)

# 查找所有的where条件
print("==== 所有的where条件 ====")
for where in parse_one(demo_sql, read="spark").find_all(exp.Where):
    print(f"where--> {where}")
    for condition in where.find_all(exp.Condition):
        print(f"condition.sql--> {condition.sql()}")
