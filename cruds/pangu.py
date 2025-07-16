#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/16 10:01 
# @Author   : guoqun X2590
# @FileName : pangu.py
# @Project  : DataForge

from urllib.parse import quote_plus

from sqlalchemy import text
from cruds.dynamic_query import query_sql

from utils.db import Database


def get_all_pangu_field_stat(db_handler: Database) -> tuple[bool, str, list[dict]]:
    """
    获取所有盘古字段统计
    :param db_handler:
    :return:
    """
    sql = """SELECT ename, count(*) ename_count FROM public.base_field_info GROUP BY ename ORDER BY ename_count DESC;"""
    status, message, result = query_sql(db=db_handler, sql_text=sql)
    print(status)
    print(message)
    print(result)
    return status, message, result


def recommend_field_info_by_pangu(db_handler: Database, field_en_name: str) -> tuple[bool, str, dict]:
    """
    查询盘古表元数据信息获取字段的推荐属性
    :param db_handler:
    :param field_en_name:
    :return:
    """
    sql = f"""SELECT name_sub.name                                        AS name,
       name_sub.name_count                                  AS name_count,
       ROUND(COALESCE(name_sub.name_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS name_percentage,
       identifier_sub.identifier                            AS identifier,
       identifier_sub.identifier_count                      AS identifier_count,
       ROUND(COALESCE(identifier_sub.identifier_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS identifier_percentage,
       description_sub.description                          AS description,
       description_sub.description_count                    AS description_count,
       ROUND(COALESCE(description_sub.description_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS description_percentage,
       field_type_sub.field_type_name                       AS field_type_name,
       field_type_sub.field_type_count                      AS field_type_count,
       ROUND(COALESCE(field_type_sub.field_type_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS field_type_percentage,
       dictkey_sub.dictkey                                  AS dictkey,
       dictkey_sub.dictkey_count                            AS dictkey_count,
       ROUND(COALESCE(dictkey_sub.dictkey_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS dictkey_percentage,
       structure_type_sub.structure_type                    AS structure_type,
       COALESCE(structure_type_sub.structure_type_count, 0) AS structure_type_count,
       ROUND(COALESCE(structure_type_sub.structure_type_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS structure_type_percentage,
       field_length_sub.field_length                        AS field_length,
       COALESCE(field_length_sub.field_length_count, 0)     AS field_length_count,
       ROUND(COALESCE(field_length_sub.field_length_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS field_length_percentage,
       element_code_sub.element_code_name                   AS element_code_name,
       COALESCE(element_code_sub.element_code_count, 0)     AS element_code_count,
       ROUND(COALESCE(element_code_sub.element_code_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS element_code_name_percentage,
       determiner_code_sub.determiner_code_name             AS determiner_code_name,
       determiner_code_sub.determiner_code_count            AS determiner_code_count,
       ROUND(COALESCE(determiner_code_sub.determiner_code_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS determiner_code_percentage,
       is_query_sub.is_query                                AS is_query,
       is_query_sub.is_query_count                          AS is_query_count,
       ROUND(COALESCE(is_query_sub.is_query_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS is_query_percentage,
       is_multi_value_sub.is_multi_value                    AS is_multi_value,
       is_multi_value_sub.is_multi_value_count              AS is_multi_value_count,
       ROUND(COALESCE(is_multi_value_sub.is_multi_value_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS is_multi_value_percentage,
       is_required_sub.is_required                          AS is_required,
       is_required_sub.is_required_count                    AS is_required_count,
       ROUND(COALESCE(is_required_sub.is_required_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS is_required_percentage,
       core_flag_sub.core_flag                              AS core_flag,
       core_flag_sub.core_flag_count                        AS core_flag_count,
       ROUND(COALESCE(core_flag_sub.core_flag_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS core_flag_percentage
FROM ((SELECT name, COUNT(*) AS name_count
       FROM public.base_field_info
       WHERE ename = UPPER('{field_en_name}')
         AND name ~ '[\u4e00-\u9fa5]'
       GROUP BY name
       ORDER BY name_count DESC
       LIMIT 1)
      UNION ALL
      (SELECT name, COUNT(*) AS name_count
       FROM public.base_field_info
       WHERE ename = UPPER('{field_en_name}')
       GROUP BY name
       ORDER BY name_count DESC
       LIMIT 1)
      LIMIT 1) AS name_sub
         CROSS JOIN (SELECT identifier, COUNT(*) AS identifier_count
                     FROM public.base_field_info
                     WHERE ename = UPPER('{field_en_name}')
                     GROUP BY identifier
                     ORDER BY identifier_count DESC
                     LIMIT 1) AS identifier_sub
         CROSS JOIN ((SELECT description, COUNT(*) AS description_count
                      FROM public.base_field_info
                      WHERE ename = UPPER('{field_en_name}')
                        AND description ~ '[\u4e00-\u9fa5]'
                      GROUP BY description
                      ORDER BY description_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS description, 0 AS description_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS description_sub
         CROSS JOIN (SELECT bft.field_type AS field_type_name, COUNT(*) AS field_type_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_field_type AS bft ON bfi.field_type = bft.code
                     WHERE bfi.ename = UPPER('{field_en_name}')
                     GROUP BY bft.field_type
                     ORDER BY field_type_count DESC
                     LIMIT 1) AS field_type_sub
         CROSS JOIN ((SELECT dictkey, COUNT(*) AS dictkey_count
                      FROM public.base_field_info
                      WHERE ename = UPPER('{field_en_name}')
                        AND dictkey IS NOT NULL
                        AND dictkey != ''
                      GROUP BY dictkey
                      ORDER BY dictkey_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS dictkey, 0 AS dictkey_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS dictkey_sub
         CROSS JOIN ((SELECT field_length, COUNT(*) AS field_length_count
                      FROM public.base_field_info
                      WHERE ename = UPPER('{field_en_name}')
                        AND field_length IS NOT NULL
                        AND field_length != ''
                      GROUP BY field_length
                      ORDER BY field_length_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS field_length, 0 AS field_length_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS field_length_sub
         CROSS JOIN ((SELECT bde.name AS element_code_name, COUNT(*) AS element_code_count
                      FROM public.base_field_info AS bfi
                               JOIN public.base_data_element AS bde ON bfi.element_code = bde.code
                      WHERE bfi.ename = UPPER('{field_en_name}')
                        AND bfi.element_code IS NOT NULL
                        AND bfi.element_code != ''
                      GROUP BY element_code_name
                      ORDER BY element_code_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS element_code_name, 0 AS element_code_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS element_code_sub
         CROSS JOIN ((SELECT bdd.name AS determiner_code_name, COUNT(*) AS determiner_code_count
                      FROM public.base_field_info AS bfi
                               JOIN public.base_data_determiner AS bdd ON bfi.determiner_code = bdd.code
                      WHERE bfi.ename = UPPER('{field_en_name}')
                        AND bfi.determiner_code IS NOT NULL
                        AND bfi.determiner_code != ''
                      GROUP BY determiner_code_name
                      ORDER BY determiner_code_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS determiner_code_name, 0 AS determiner_code_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS determiner_code_sub
         CROSS JOIN ((SELECT structure_type, COUNT(*) AS structure_type_count
                      FROM public.base_field_info
                      WHERE ename = UPPER('{field_en_name}')
                        AND structure_type IS NOT NULL
                      GROUP BY structure_type
                      ORDER BY structure_type_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS structure_type, 0 AS structure_type_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS structure_type_sub
         CROSS JOIN (SELECT is_query, COUNT(*) AS is_query_count
                     FROM public.base_field_info
                     WHERE ename = UPPER('{field_en_name}')
                       AND is_query IS NOT NULL
                     GROUP BY is_query
                     ORDER BY is_query_count DESC
                     LIMIT 1) AS is_query_sub
         CROSS JOIN (SELECT is_multi_value, COUNT(*) AS is_multi_value_count
                     FROM public.base_field_info
                     WHERE ename = UPPER('{field_en_name}')
                       AND is_multi_value IS NOT NULL
                     GROUP BY is_multi_value
                     ORDER BY is_multi_value_count DESC
                     LIMIT 1) AS is_multi_value_sub
         CROSS JOIN (SELECT is_required, COUNT(*) AS is_required_count
                     FROM public.base_field_info
                     WHERE ename = UPPER('{field_en_name}')
                       AND is_required IS NOT NULL
                     GROUP BY is_required
                     ORDER BY is_required_count DESC
                     LIMIT 1) AS is_required_sub
         CROSS JOIN (SELECT core_flag, COUNT(*) AS core_flag_count
                     FROM public.base_field_info
                     WHERE ename = UPPER('{field_en_name}')
                     GROUP BY core_flag
                     ORDER BY core_flag_count DESC
                     LIMIT 1) AS core_flag_sub
         CROSS JOIN (SELECT COUNT(*) AS total_count
                     FROM public.base_field_info
                     WHERE ename = UPPER('{field_en_name}')) AS total_sub;"""
    field_info = {}
    try:
        result = db_handler.session.execute(statement=text(sql))
        temp_field_info = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        if len(temp_field_info) == 1:
            field_info = temp_field_info[0]
    except Exception as err:
        message = f"数据库读操作异常: {err}"
        return False, message, field_info
    else:
        return True, "ok", field_info


if __name__ == '__main__':
    from config import METADATA_DB_IP, METADATA_DB_NAME, METADATA_DB_USER, METADATA_DB_PORT, METADATA_DB_PASSWORD

    SQLALCHEMY_URL = f"postgresql+psycopg2://" \
                     f"{METADATA_DB_USER}:{quote_plus(METADATA_DB_PASSWORD)}" \
                     f"@{METADATA_DB_IP}:{METADATA_DB_PORT}" \
                     f"/{METADATA_DB_NAME}" \
                     f"?client_encoding=UTF8"
    metadata_db = Database(url=SQLALCHEMY_URL)

    s, m, d = get_all_pangu_field_stat(metadata_db)
    if s:
        for f in d:
            print(f"field: {f}")
            s, m, d = recommend_field_info_by_pangu(db_handler=metadata_db, field_en_name=f.get("ename"))
            if s:
                print(d)
            else:
                print(m)
    else:
        print(m)
