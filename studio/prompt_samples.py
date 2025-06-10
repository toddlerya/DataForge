#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/22 16:29
# @Author   : guoqun X2590
# @FileName : prompt_samples.py
# @Project  : PreviewDataForge

# 假设已经从数仓知识库根据表名称获取到表字段信息
table_en_name = "ADM_GRAPH_NODE_FLIGHT"
table_cn_name = "航班节点表"
table_columns_info = [
    {"name": "航班唯一标识", "ename": "FLIGHT", "desc": "航班唯一标识"},
    {"name": "航班号", "ename": "FLIG_NO", "desc": "航班号"},
    {"name": "始发机场名称", "ename": "DEP_AIR", "desc": "始发机场名称"},
    {"name": "终点机场名称", "ename": "ARR_AIR", "desc": "终点机场名称"},
    {
        "name": "始发站行政区划代码",
        "ename": "DEP_CITY_CODE",
        "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
    },
    {
        "name": "终点站行政区划代码",
        "ename": "ARR_CITY_CODE",
        "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
    },
]

table_create_sql = """CREATE TABLE
  fmdbmeta.ADM_GRAPH_NODE_FLIGHT (
    flight STRING,
    flig_no STRING,
    dep_air STRING,
    arr_air STRING,
    dep_city_code STRING,
    arr_city_code STRING
  ) PARTITIONED BY (p1 string, p2 string, p3 string, p4 string) LOCATION 'hdfs://ngpcluster/nebula_datacenter/import/daml/data/adm/graph/node/ADM_GRAPH_NODE_FLIGHT' TBLPROPERTIES (
    'hive.output.file.extension' = '.nb',
    'serialization.null.format' = ''
  ) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE"""

job_sql = """INSERT INTO fmdbmeta.ADM_GRAPH_NODE_FLIGHT
SELECT md5_id(FLIG_NO, '\t', DEP_AIR, '\t', ARR_AIR) AS FLIGHT,
       FLIG_NO                                       AS FLIG_NO,
       DEP_AIR                                       AS DEP_AIR,
       ARR_AIR                                       AS ARR_AIR,
       DEP_CITY_CODE                                 AS DEP_CITY_CODE,
       ARR_CITY_CODE                                 AS ARR_CITY_CODE
FROM (
         SELECT FLIG_NO       AS FLIG_NO,
                dw_wa_adm_graph_dicloader('123') AS TEST,
                DEP_AIR       AS DEP_AIR,
                ARR_AIR       AS ARR_AIR,
                DEP_CITY_CODE AS DEP_CITY_CODE,
                ARR_CITY_CODE AS ARR_CITY_CODE
         FROM fmdbmeta.ADM_GRAPH_NODE_FLIGHT ADM_GRAPH_NODE_FLIGHT
         UNION
         SELECT FLIG_NUM                                           AS FLIG_NO,
                dw_wa_adm_graph_dicloader('123') AS TEST,
                map_finder(DEPARTURE_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_NAME.DIC')            AS DEP_AIR,
                map_finder(ARR_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_NAME.DIC')                  AS ARR_AIR,
                map_finder(DEPARTURE_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_ADDI_CODE.DIC') AS DEP_CITY_CODE,
                map_finder(ARR_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_ADDI_CODE.DIC')       AS ARR_CITY_CODE
         FROM fmdbmeta.DWS_PER_RES_DAY_DCFLIGHT DWS_PER_RES_DAY_DCFLIGHT
         WHERE FLIG_NUM IS NOT NULL
           AND DEPARTURE_AIR IS NOT NULL
           AND ARR_AIR IS NOT NULL
     ) ADM_GRAPH_NODE_FLIGHT_TMP
GROUP BY FLIG_NO,
         DEP_AIR,
         ARR_AIR,
         DEP_CITY_CODE,
         ARR_CITY_CODE"""
