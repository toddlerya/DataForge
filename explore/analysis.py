#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/09/18 10:03
# @Author   : guoqun X2590
# @Desc     : 分析百万fmdbsql


import pathlib

from loguru import logger

from cruds.dynamic_query import query_sql
from utils.db_manager import DatabaseManager
from utils.file import load_json_from_file, save_jl_data2xlsx


def main():
    base_path = pathlib.Path(__file__).parent.joinpath("mass_fmdb_sql_csv_data")
    dql_point_query_table_json = base_path.joinpath(
        "11w_sql_dql_point_query_table_info.json"
    )
    load_msg, load_data = load_json_from_file(
        json_file_path=str(dql_point_query_table_json)
    )
    if load_msg != "ok":
        raise Exception(load_msg)
    logger.info(f"共计{len(load_data)}条数据")
    # 查询哪些表没有使用
    db_manager = DatabaseManager()
    query_status, query_msg, table_data = query_sql(
        db_manager=db_manager,
        sql_text="""select table_en_name, table_cn_name from table_meta_data_info tmdi
        where "source" = '盘古' and table_en_name like 'massdata%';""",
    )
    if query_status is False:
        raise Exception(query_msg)
    all_pangu_fmdb_table_en_name = [ele.get("table_en_name") for ele in table_data]
    logger.info(f"共计{len(all_pangu_fmdb_table_en_name)}个盘古massdata FMDB表")
    dql_point_query_table_en_name_list = list(load_data.keys())
    dont_use_fmdb_table_en_name_set = set(all_pangu_fmdb_table_en_name) - set(
        dql_point_query_table_en_name_list
    )
    logger.info(
        f"共计{len(dont_use_fmdb_table_en_name_set)}个盘古massdata FMDB表没有使用"
    )
    # with open(
    #     base_path.joinpath("没有使用的盘古FMDB表清单.xlsx"), mode="w", encoding="utf-8"
    # ) as w:
    dont_use_table_name_data = [
        ele
        for ele in table_data
        if ele.get("table_en_name") in dont_use_fmdb_table_en_name_set
    ]
    save_jl_data2xlsx(
        json_line_data=dont_use_table_name_data,
        save_path=str(
            base_path.joinpath(
                "杭州11万SQL【dql_point_query】没有使用的盘古FMDB表清单(massdata).xlsx"
            ).absolute()
        ),
    )
    used_table_name_data = [
        ele
        for ele in table_data
        if ele.get("table_en_name") in dql_point_query_table_en_name_list
    ]
    save_jl_data2xlsx(
        json_line_data=used_table_name_data,
        save_path=str(
            base_path.joinpath(
                "杭州11万SQL【dql_point_query】使用的盘古FMDB表清单(massdata).xlsx"
            ).absolute()
        ),
    )
    # only_hangzhou_fmdb_table_en_name_set = set(
    #     dql_point_query_table_en_name_list
    # ) - set(all_pangu_fmdb_table_en_name)
    # only_hangzhou_fmdb_table_en_name_data = [
    #     {"table_en_name": ele} for ele in only_hangzhou_fmdb_table_en_name_set
    # ]
    # save_jl_data2xlsx(
    #     json_line_data=only_hangzhou_fmdb_table_en_name_data,
    #     save_path=str(
    #         base_path.joinpath(
    #             "杭州11万SQL【dql_point_query】只在dql_point_query日志中出现的表清单.xlsx"
    #         ).absolute()
    #     ),
    # )


if __name__ == "__main__":
    main()
