#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/16 10:01
# @Author   : guoqun X2590
# @FileName : pangu.py
# @Project  : DataForge


from sqlalchemy import or_, text

from cruds.dynamic_query import query_sql
from database_models.models import PanGuDictInfo, RecommendPanGuFieldInfo
from database_models.schema import RecommendPanGuDictSchema, RecommendPanGuFieldSchema
from utils.db_manager import DatabaseManager, GenericUpsert


def get_all_pangu_field_stat(
    db_manager: DatabaseManager,
) -> tuple[bool, str, list[dict] | None]:
    """
    获取所有盘古字段统计
    :param db_manager:
    :return:
    """
    sql = """SELECT ename, count(*) ename_count
                FROM public.base_field_info
                GROUP BY ename
                ORDER BY ename_count DESC;"""
    status, message, result = query_sql(db_manager=db_manager, sql_text=sql)
    return status, message, result


def pangu_recommend_field_info(
    db_manager: DatabaseManager, field_en_name: str
) -> tuple[bool, str, dict]:
    """
    查询盘古表元数据信息获取字段的推荐属性
    :param db_manager:
    :param field_en_name:
    :return:
    """
    sql = f"""SELECT
       cname_sub.cname                                        AS cname,
       cname_sub.cname_count                                  AS cname_count,
       ROUND(COALESCE(cname_sub.cname_count * 100.0 / NULLIF(total_sub.total_count, 0), 0),
             2)                                             AS cname_percentage,
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
FROM ((SELECT name AS cname, COUNT(*) AS cname_count
       FROM public.base_field_info
       WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
         AND name ~ '[\u4e00-\u9fa5]'
       GROUP BY name
       ORDER BY cname_count DESC
       LIMIT 1)
      UNION ALL
      (SELECT name AS cname, COUNT(*) AS cname_count
       FROM public.base_field_info
       WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
       GROUP BY name
       ORDER BY cname_count DESC
       LIMIT 1)
      LIMIT 1) AS cname_sub
         CROSS JOIN (SELECT identifier, COUNT(*) AS identifier_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                     GROUP BY identifier
                     ORDER BY identifier_count DESC
                     LIMIT 1) AS identifier_sub
         CROSS JOIN ((SELECT description, COUNT(*) AS description_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                        AND description ~ '[\u4e00-\u9fa5]'
                      GROUP BY description
                      ORDER BY description_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT description, COUNT(*) AS description_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                      GROUP BY description
                      ORDER BY description_count DESC
                      LIMIT 1) LIMIT 1) AS description_sub
         CROSS JOIN (SELECT bft.field_type AS field_type_name, COUNT(*) AS field_type_count
                     FROM public.base_field_info AS bfi
                              JOIN public.base_field_type AS bft ON bfi.field_type = bft.code
                     WHERE (bfi.ename = UPPER('{field_en_name}') OR bfi.ename = '{field_en_name}')
                     GROUP BY bft.field_type
                     ORDER BY field_type_count DESC
                     LIMIT 1) AS field_type_sub
         CROSS JOIN ((SELECT dictkey, COUNT(*) AS dictkey_count
                      FROM public.base_field_info
                      WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
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
                      WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
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
                      WHERE (bfi.ename = UPPER('{field_en_name}') OR bfi.ename = '{field_en_name}')
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
                      WHERE (bfi.ename = UPPER('{field_en_name}') OR bfi.ename = '{field_en_name}')
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
                      WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                        AND structure_type IS NOT NULL
                      GROUP BY structure_type
                      ORDER BY structure_type_count DESC
                      LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS structure_type, 0 AS structure_type_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS structure_type_sub
         CROSS JOIN ((SELECT is_multi_value, COUNT(*) AS is_multi_value_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                       AND is_multi_value IS NOT NULL
                     GROUP BY is_multi_value
                     ORDER BY is_multi_value_count DESC
                     LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS is_multi_value, 0 AS is_multi_value_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS is_multi_value_sub
         CROSS JOIN ((SELECT is_required, COUNT(*) AS is_required_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                       AND is_required IS NOT NULL
                     GROUP BY is_required
                     ORDER BY is_required_count DESC
                     LIMIT 1)
                     UNION ALL
                     (SELECT NULL AS is_required, 0 AS is_required_count FROM (SELECT 1) AS dummy)
                     LIMIT 1) AS is_required_sub
         CROSS JOIN (SELECT core_flag, COUNT(*) AS core_flag_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}')
                     GROUP BY core_flag
                     ORDER BY core_flag_count DESC
                     LIMIT 1) AS core_flag_sub
         CROSS JOIN (SELECT COUNT(*) AS total_count
                     FROM public.base_field_info
                     WHERE (ename = UPPER('{field_en_name}') OR ename = '{field_en_name}') ) AS total_sub;"""  # noqa: E501
    field_info = {}
    try:
        result = db_manager.get_session().execute(statement=text(sql))
        temp_field_info = [dict(zip(result.keys(), row)) for row in result.fetchall()]
        if len(temp_field_info) == 1:
            field_info = temp_field_info[0]
            field_info.update({"ename": field_en_name})
        db_manager.get_session().commit()
    except Exception as err:
        message = f"数据库读操作异常: {err}"
        db_manager.get_session().rollback()
        return False, message, field_info
    else:
        return True, "ok", field_info


def pangu_dict_key_values(
    db_manager: DatabaseManager, dictkey_with_nlevel: str
) -> tuple[bool, str, list[dict]]:
    """
    根据字典关联ID及层级获取字典详情
    :param db_handler:
    :param dictkey_with_nlevel:
    :return:
    """
    sql = f"""SELECT code AS uuid,
                    '{dictkey_with_nlevel}' AS dictkey_with_nlevel,
                    parentid AS dict_category_code,
                    COALESCE(parentname, '无字典类别名称') AS dict_category,
                    nlevel AS dict_level,
                    id AS dict_id,
                    name AS dict_name FROM public.base_dd_tab
                WHERE parentid = split_part('{dictkey_with_nlevel}', ':', 1)
                AND nlevel = CAST(split_part('{dictkey_with_nlevel}', ':', 2) AS INTEGER);"""  # noqa: E501
    status, message, result = query_sql(db_manager=db_manager, sql_text=sql)
    return status, message, result


def save_recommend_pangu_field_info(
    db_manager: DatabaseManager,
    recommend_pangu_field_data: dict,
    auto_commit: bool = True,
) -> tuple[bool, str]:
    try:
        GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(),
            model_class=RecommendPanGuFieldInfo,
            data=recommend_pangu_field_data,
            auto_commit=auto_commit,
        )
    except Exception as err:
        message = f"数据库写操作错误: {err}"
        return False, message
    return True, "ok"


def batch_save_recommend_pangu_field_info(
    db_manager: DatabaseManager,
    recommend_pangu_field_data_slice: list[dict],
    batch_size: int,
) -> tuple[bool, str]:
    try:
        GenericUpsert(db=db_manager.db).batch_smart_insert_or_update(
            session=db_manager.get_session(),
            model_class=RecommendPanGuFieldInfo,
            data_list=recommend_pangu_field_data_slice,
            batch_size=batch_size,
        )
    except Exception as err:
        db_manager.get_session().rollback()
        message = f"数据库写操作错误: {err}"
        return False, message
    return True, "ok"


def save_pangu_dict_info(
    db_manager: DatabaseManager, pangu_dict_key_data: dict, auto_commit: bool = True
) -> tuple[bool, str]:
    try:
        GenericUpsert(db=db_manager.db).smart_insert_or_update_single(
            session=db_manager.get_session(),
            model_class=PanGuDictInfo,
            data=pangu_dict_key_data,
            auto_commit=auto_commit,
        )
    except Exception as err:
        message = f"数据库写操作错误: {err}"
        return False, message
    return True, "ok"


def query_field_recommend_info_by_ename(
    db_manager: DatabaseManager, field_en_name: str
) -> tuple[bool, str, RecommendPanGuFieldSchema | None]:
    """
    根据字段英文名查询存储的盘古字段推荐信息
    :param db_handler:
    :param field_en_name:
    :return:
    """

    recommend_field_data = None
    try:
        result = (
            db_manager.get_session()
            .query(RecommendPanGuFieldInfo)
            .filter(
                or_(
                    RecommendPanGuFieldInfo.ename.like(field_en_name),
                    RecommendPanGuFieldInfo.identifier.like(field_en_name),
                )
            )
            .all()
        )
        max_cname_percentage = 0.0
        max_identifier_percentage = 0.0
        for row in result:
            row_data = row.to_dict()
            row_data.pop("id")
            row_data.pop("create_time")
            row_data.pop("update_time")
            row_data.pop("remark")
            row_recommend_field_data = RecommendPanGuFieldSchema(**row_data)
            # 取占比最高的作为唯一结果
            if recommend_field_data is None:
                # 初始化
                recommend_field_data = row_recommend_field_data
                max_cname_percentage = row_recommend_field_data.cname_percentage
                max_identifier_percentage = (
                    row_recommend_field_data.identifier_percentage
                )
            elif (
                row_recommend_field_data.cname_percentage >= max_cname_percentage
                and row_recommend_field_data.identifier_percentage
                >= max_identifier_percentage
            ):
                # 更新
                recommend_field_data = row_recommend_field_data
                max_cname_percentage = row_recommend_field_data.cname_percentage
                max_identifier_percentage = (
                    row_recommend_field_data.identifier_percentage
                )
        db_manager.get_session().commit()
    except Exception as err:
        message = f"数据库查询异常: {err}"
        db_manager.get_session().rollback()
        return False, message, recommend_field_data
    return True, "ok", recommend_field_data


def query_dict_items_info_by_dictkey(
    db_manager: DatabaseManager, dictkey_with_nlevel: str
) -> tuple[bool, str, list[RecommendPanGuDictSchema]]:
    """
    查询字典类别的所有字典值
    """
    data: list[RecommendPanGuDictSchema] = []
    try:
        result = (
            db_manager.get_session()
            .query(PanGuDictInfo)
            .filter(PanGuDictInfo.dictkey_with_nlevel == dictkey_with_nlevel.strip())
            .all()
        )
        for row in result:
            row_data = row.to_dict()
            row_data.pop("id")
            row_data.pop("create_time")
            row_data.pop("update_time")
            row_data.pop("remark")
            row_dict_data = RecommendPanGuDictSchema(**row_data)
            data.append(row_dict_data)
        db_manager.get_session().commit()
    except Exception as err:
        message = f"数据库查询异常: {err}"
        db_manager.get_session().rollback()
        return False, message, data
    return True, "ok", data


def query_dict_items_info_by_dict_category(
    db_manager: DatabaseManager, dict_category: str
) -> tuple[bool, str, list[RecommendPanGuDictSchema]]:
    """
    查询字典类别的所有字典值
    """
    data: list[RecommendPanGuDictSchema] = []
    try:
        result = (
            db_manager.get_session()
            .query(PanGuDictInfo)
            .filter(PanGuDictInfo.dict_category == dict_category.strip())
            .all()
        )
        for row in result:
            row_data = row.to_dict()
            row_data.pop("id")
            row_data.pop("create_time")
            row_data.pop("update_time")
            row_data.pop("remark")
            row_dict_data = RecommendPanGuDictSchema(**row_data)
            data.append(row_dict_data)
        db_manager.get_session().commit()
    except Exception as err:
        message = f"数据库查询异常: {err}"
        db_manager.get_session().rollback()
        return False, message, data
    return True, "ok", data


if __name__ == "__main__":
    # from config import (METADATA_DB_IP, METADATA_DB_NAME,
    # METADATA_DB_USER, METADATA_DB_PORT, METADATA_DB_PASSWORD)
    #
    # SQLALCHEMY_URL = f"postgresql+psycopg2://" \
    #                  f"{METADATA_DB_USER}:{quote_plus(METADATA_DB_PASSWORD)}" \
    #                  f"@{METADATA_DB_IP}:{METADATA_DB_PORT}" \
    #                  f"/{METADATA_DB_NAME}" \
    #                  f"?client_encoding=UTF8"
    # metadata_db = Database(url=SQLALCHEMY_URL)
    #
    # s, m, all_pangu_field_stat_data = get_all_pangu_field_stat(metadata_db)
    # if s:
    #     for each_field_info in all_pangu_field_stat_data:
    #         print("=" * 20)
    #         print(f"field: {each_field_info}")
    #         status, msg, data = pangu_recommend_field_info(
    # db_handler=metadata_db,
    # field_en_name=each_field_info.get("ename"))
    #         if status:
    #             print(f"data: {data}")
    #             if data.dictkey:
    #                 print("dict_key_values: ",
    #                       data.dictkey,
    #                       pangu_dict_key_values(dictkey_with_nlevel=data.dictkey,
    #  db_handler=metadata_db))
    #         else:
    #             print(msg)
    #             break
    # else:
    #     print(m)
    db_manager = DatabaseManager()
    print(
        query_field_recommend_info_by_ename(
            db_manager=db_manager, field_en_name="RELE_DIRECTION_TYPE"
        )
    )
    db_manager.close()
    # s,m,d=(query_dict_items_info_by_dictkey(db_handler=Database(),
    # dictkey_with_nlevel="FHWACODE_0098:2"))
    # print(s)
    # print(m)
    # print(d)
    # one_dict = d[0]
    # category = one_dict.dict_category
    # print(f"category: {category}")
    # value = [ele.model_dump_json() for ele in d]
