#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/15 17:30
# @Author   : guoqun X2590
# @FileName : prompts.py
# @Project  : PreviewDataForge

demo1_prompt = """
# 任务
构造这两张表的测试数据
1. fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS ( 域名分类信息表 )
2. fmdbmeta.ADM_DOMAIN_WHOIS ( 域名备案表 )

# 要求
1. 满足治理SQL的过滤条件，确保数据能够符合过滤条件
2. 字段数据要丰富真实
3. 字段数据优先使用call_faker_factory工具来生成仿真数据


# 参考信息
## 表结构元数据

### fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS

```json
[
  {
    "name": "烽火系统数据唯一标识ID",
    "ename": "MD_ID",
    "desc": "md5(SEARCH_URL,URL_DOMAIN,URL)"
  },
  {
    "name": "数据采集来源系统",
    "ename": "COL_SOUR_SYS",
    "desc": "参考数据来源系统字典，现场对标没有可以补充"
  },
  {
    "name": "数据采集来源系统备注",
    "ename": "COL_SOUR_SYS_REMARK",
    "desc": "参考数据来源系统字典对应的名称"
  },
  {
    "name": "数据采集来源部门",
    "ename": "COL_SOUR_DEP",
    "desc": "参考数据来源部门字典，现场对标没有可以补充"
  },
  {
    "name": "数据采集来源地",
    "ename": "COL_SOUR_PLAC",
    "desc": "填入数据来源的六位行政区划代码"
  },
  {
    "name": "采集时间",
    "ename": "COLL_TIME",
    "desc": "指数据接入到大数据平台的时间"
  },
  {
    "name": "数据采集来源表名",
    "ename": "COL_SOUR_TABLE",
    "desc": "从原始数据里面获取，填入STG表的原始表名"
  },
  {
    "name": "原始系统接入主键",
    "ename": "ORIG_DATA_ID",
    "desc": "从原始数据里面获取，填入STG表的主键值"
  },
  {
    "name": "更新时间",
    "ename": "UPD_TIME",
    "desc": "从原始数据里面获取，这里指业务的更新时间，选取数据的业务性质的更新时间，默认更新时间不可大于当前时间，对于无业务更新时间统一约定为-1"
  },
  {
    "name": "信息删除_判断标识",
    "ename": "INFO_DELE_JUDGE_FLAG",
    "desc": "从原始数据里面获取，指整条数据是否有效，从原始数据判断数据已经删除填写“1”，否则填“0”"
  },
  {
    "name": "数据敏感级别编码",
    "ename": "DATA_SENS_LEVE_NO",
    "desc": "数据敏感级别编码"
  },
  {
    "name": "数据库回溯标识符",
    "ename": "DATBAS_RECSOU_TAG",
    "desc": "数据库回溯标识符"
  },
  {
    "name": "业务标签标识",
    "ename": "BUS_TAG_FLAG",
    "desc": "业务标签标识"
  },
  {
    "name": "行为标签标识",
    "ename": "BEH_TAG_FLAG",
    "desc": "行为标签标识"
  },
  {
    "name": "域名",
    "ename": "DOMAIN",
    "desc": "字段说明：域名（二级域名，部分二级域名会带有国家后缀，也认定为二级域名）\n样例数据：www.qdsrmyy.com"
  },
  {
    "name": "域名ID",
    "ename": "REGISTRY_DOMAIN_ID",
    "desc": "字段说明：域名的唯一标识，是注册服务商分配的一个ID\n样例数据：113108974_domain_com-vrsn"
  },
  {
    "name": "注册服务商",
    "ename": "REGISTRAR",
    "desc": "样例数据：Xin Net Technology Corporation"
  },
  {
    "name": "注册服务商IANA ID",
    "ename": "REGISTRAR_IANA_ID",
    "desc": "字段说明：注册服务商互联网数字分配机构ID\n样例数据：120"
  },
  {
    "name": "注册服务商WHOIS服务器",
    "ename": "REGISTRAR_WHOIS_SERVER",
    "desc": "字段说明：注册服务商WHOIS服务器(whois 用来查询域名的ip以及所有者等信息的传输协议)\n样例数据：whois.paycenter.com.cn"
  },
  {
    "name": "注册服务商网址",
    "ename": "REGISTRAR_URL",
    "desc": "样例数据：http://www.xinnet.com"
  },
  {
    "name": "注册服务商电子邮件",
    "ename": "REGISTRAR_CONTACT_EMAIL",
    "desc": "样例数据：supervision@xinnet.com"
  },
  {
    "name": "注册服务商联系电话",
    "ename": "REGISTRAR_CONTACT_PHONE",
    "desc": "样例数据：86.4008182233"
  },
  {
    "name": "域名建立时间",
    "ename": "CREATION_TIME",
    "desc": "字段说明：域名的建立时间\n样例数据：1078214400"
  },
  {
    "name": "域名更新时间",
    "ename": "UPDATED_TIME",
    "desc": "字段说明：域名的更新时间\n样例数据：1612312997"
  },
  {
    "name": "域名到期时间",
    "ename": "EXPIRATION_TIME",
    "desc": "字段说明：域名的到期时间\n样例数据：1646284971"
  },
  {
    "name": "注册单位名称",
    "ename": "REGISTRANT_ORGANIZATION",
    "desc": ""
  },
  {
    "name": "注册省名称",
    "ename": "REGISTRANT_PROVINCE",
    "desc": "样例数据：JS"
  },
  {
    "name": "注册国家名称",
    "ename": "REGISTRANT_COUNTRY",
    "desc": "样例数据：CN"
  },
  {
    "name": "注册电子邮件",
    "ename": "REGISTRANT_EMAIL",
    "desc": "样例数据：supervision@xinnet.com"
  },
  {
    "name": "管理员单位名称",
    "ename": "ADMIN_ORGANIZATION",
    "desc": ""
  },
  {
    "name": "管理员省名称",
    "ename": "ADMIN_PROVINCE",
    "desc": ""
  },
  {
    "name": "管理员国家名称",
    "ename": "ADMIN_COUNTRY",
    "desc": ""
  },
  {
    "name": "管理员电子邮件",
    "ename": "ADMIN_EMAIL",
    "desc": "样例数据：supervision@xinnet.com"
  },
  {
    "name": "技术单位名称",
    "ename": "TECH_ORGANIZATION",
    "desc": ""
  },
  {
    "name": "技术单位省名称",
    "ename": "TECH_PROVINCE",
    "desc": ""
  },
  {
    "name": "技术单位国家名称",
    "ename": "TECH_COUNTRY",
    "desc": ""
  },
  {
    "name": "技术单位电子邮件",
    "ename": "TECH_EMAIL",
    "desc": "样例数据：supervision@xinnet.com"
  }
]
```

### fmdbmeta.ADM_DOMAIN_WHOIS

```json
[
  {
    "name": "md5主键",
    "ename": "MD_ID",
    "desc": "MD5(DOMAIN)"
  },
  {
    "name": "域名",
    "ename": "DOMAIN",
    "desc": "域名（二级域名，ipv4、ipv6保留原格式，部分二级域名会带有国家后缀，也认定为二级域名）\n例：\nbaidu.com\nbaidu.com.cn\n12.12.12.12"
  },
  {
    "name": "注册域名ID",
    "ename": "REGISTRY_DOMAIN_ID",
    "desc": "注册域名ID"
  },
  {
    "name": "注册商WHOIS服务器",
    "ename": "REGISTRAR_WHOIS_SERVER",
    "desc": "注册商WHOIS服务器"
  },
  {
    "name": "注册商网址",
    "ename": "REGISTRAR_URL",
    "desc": "注册商网址"
  },
  {
    "name": "更新时间",
    "ename": "UPDATED_TIME",
    "desc": "更新时间"
  },
  {
    "name": "建立时间",
    "ename": "CREATION_TIME",
    "desc": "建立时间"
  },
  {
    "name": "到期时间",
    "ename": "EXPIRATION_TIME",
    "desc": "到期时间"
  },
  {
    "name": "注册商",
    "ename": "REGISTRAR",
    "desc": "注册商"
  },
  {
    "name": "注册机构IANA ID",
    "ename": "REGISTRAR_IANA_ID",
    "desc": "注册机构IANA ID"
  },
  {
    "name": "注册服务商联系电子邮件",
    "ename": "REGISTRAR_CONTACT_EMAIL",
    "desc": "注册服务商联系电子邮件"
  },
  {
    "name": "注册服务商联系电话",
    "ename": "REGISTRAR_CONTACT_PHONE",
    "desc": "注册服务商联系电话"
  },
  {
    "name": "注册单位名称",
    "ename": "REGISTRANT_ORGANIZATION",
    "desc": "注册单位名称"
  },
  {
    "name": "注册省",
    "ename": "REGISTRANT_PROVINCE",
    "desc": "注册省"
  },
  {
    "name": "注册国家",
    "ename": "REGISTRANT_COUNTRY",
    "desc": "注册国家"
  },
  {
    "name": "注册人电子邮件",
    "ename": "REGISTRANT_EMAIL",
    "desc": "注册人电子邮件"
  },
  {
    "name": "管理员单位名称",
    "ename": "ADMIN_ORGANIZATION",
    "desc": "管理员单位名称"
  },
  {
    "name": "管理员省",
    "ename": "ADMIN_PROVINCE",
    "desc": "管理员省"
  },
  {
    "name": "管理员国家",
    "ename": "ADMIN_COUNTRY",
    "desc": "管理员国家"
  },
  {
    "name": "管理员联系电子邮件",
    "ename": "ADMIN_EMAIL",
    "desc": "管理员联系电子邮件"
  },
  {
    "name": "技术单位名称",
    "ename": "TECH_ORGANIZATION",
    "desc": "技术单位名称"
  },
  {
    "name": "技术单位省",
    "ename": "TECH_PROVINCE",
    "desc": "技术单位省"
  },
  {
    "name": "技术单位国家",
    "ename": "TECH_COUNTRY",
    "desc": "技术单位国家"
  },
  {
    "name": "技术单位联系电子邮件",
    "ename": "TECH_EMAIL",
    "desc": "技术单位联系电子邮件"
  },
  {
    "name": "入库时间",
    "ename": "CREATE_TIME",
    "desc": "入库时间"
  },
  {
    "name": "最后更新时间",
    "ename": "LAST_TIME",
    "desc": "最后更新时间"
  },
  {
    "name": "注册人",
    "ename": "REGISTRANT",
    "desc": "注册人"
  }
]
```



## 建表语句

### fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS建表语句

```sql
CREATE TABLE
  fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS (
    md_id STRING,
    col_sour_sys STRING,
    col_sour_sys_remark STRING,
    col_sour_dep STRING,
    col_sour_plac STRING,
    coll_time BIGINT,
    col_sour_table STRING,
    orig_data_id STRING,
    upd_time BIGINT,
    info_dele_judge_flag STRING,
    data_sens_leve_no STRING,
    datbas_recsou_tag STRING,
    bus_tag_flag STRING,
    beh_tag_flag STRING,
    domain STRING,
    registry_domain_id STRING,
    registrar STRING,
    registrar_iana_id STRING,
    registrar_whois_server STRING,
    registrar_url STRING,
    registrar_contact_email STRING,
    registrar_contact_phone STRING,
    creation_time BIGINT,
    updated_time BIGINT,
    expiration_time BIGINT,
    registrant_organization STRING,
    registrant_province STRING,
    registrant_country STRING,
    registrant_email STRING,
    admin_organization STRING,
    admin_province STRING,
    admin_country STRING,
    admin_email STRING,
    tech_organization STRING,
    tech_province STRING,
    tech_country STRING,
    tech_email STRING,
    p1 STRING,
    p2 STRING,
    p3 STRING,
    p4 STRING
  ) USING ORC PARTITIONED BY (p1, p2, p3, p4) TBLPROPERTIES (
    'table.ttl.partition' = 'p1',
    'table.ttl' = '630720000'
  )
```


### fmdbmeta.ADM_DOMAIN_WHOIS建表语句
```sql
CREATE TABLE
  fmdbmeta.ADM_DOMAIN_WHOIS (
    md_id STRING,
    domain STRING,
    registry_domain_id STRING,
    registrar_whois_server STRING,
    registrar_url STRING,
    updated_time BIGINT,
    creation_time BIGINT,
    expiration_time BIGINT,
    registrar STRING,
    registrar_iana_id STRING,
    registrar_contact_email STRING,
    registrar_contact_phone STRING,
    registrant_organization STRING,
    registrant_province STRING,
    registrant_country STRING,
    registrant_email STRING,
    admin_organization STRING,
    admin_province STRING,
    admin_country STRING,
    admin_email STRING,
    tech_organization STRING,
    tech_province STRING,
    tech_country STRING,
    tech_email STRING,
    create_time BIGINT,
    last_time BIGINT,
    registrant STRING,
    p1 STRING,
    p2 STRING,
    p3 STRING,
    p4 STRING
  ) USING ORC PARTITIONED BY (p1, p2, p3, p4) TBLPROPERTIES (
    'table.ttl.partition' = 'p1',
    'table.ttl' = '630720000'
  )
```

## 治理SQL

```sql
-- ************************************************************
-- SQL功能描述：WHOIS增量数据合并，更新策略为最新覆盖，部分域名没有做二级域名提取，合并之前一起做一下二级域名归一化
-- SQL调度策略：周期
-- 输入表策略：
-- 1、fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS ( 域名分类信息表 )：增量数据（nbapp）
-- 2、fmdbmeta.ADM_DOMAIN_WHOIS ( 域名备案表 )：全量数据（lastdir）
-- 输出表策略：
-- fmdbmeta.ADM_DOMAIN_WHOIS ：全量数据
-- ************************************************************
INSERT INTO
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
```

## 表约束元数据

```json
[
  {
    "tables_name": null,
    "filters": [
      "WHERE NOT DOMAIN IS NULL"
    ],
    "join_conditions": [],
    "union_conditions": [
      "UNION ALL"
    ]
  },
  {
    "tables_name": "fmdbmeta.ODS_POL_EIV_DOMAIN_WHOIS",
    "filters": [
      "WHERE DAW_UDF_CHECK_NOT_EMPTY(REGISTRY_DOMAIN_ID, REGISTRAR_WHOIS_SERVER, REGISTRAR_URL, REGISTRAR) <> '0000'"
    ],
    "join_conditions": [],
    "union_conditions": []
  },
  {
    "tables_name": "fmdbmeta.ADM_DOMAIN_WHOIS",
    "filters": [],
    "join_conditions": [],
    "union_conditions": []
  }
]
```
"""


demo2_prompt = """## 任务
根据下面的建表语句SQL，进行构造数据，使用insert into生成对应插入数据的SQL语句
## 要求
1. 表结构字段含义如下，尽可能使用仿真数据生成工具填充字段内容
[
  {
    "name": "车架号(车辆识别代号)",
    "ename": "VEH_NO",
    "desc": "车辆识别代号与号牌号码一个有值即可; VEH_NO | (DRIVE_LIC_TCODE & VEH_PLATE_NUM)"
  },
  {
    "name": "机动车号牌种类代码",
    "ename": "DRIVE_LIC_TCODE",
    "desc": "VEH_NO | (DRIVE_LIC_TCODE & VEH_PLATE_NUM)"
  },
  {
    "name": "机动车号牌号码",
    "ename": "VEH_PLATE_NUM",
    "desc": "车辆识别代号与号牌号码一个有值即可; VEH_NO | (DRIVE_LIC_TCODE & VEH_PLATE_NUM)"
  },
  {
    "name": "机动车序号",
    "ename": "VEH_IDNO",
    "desc": ""
  },
  {
    "name": "机动车国产/进口分类代码",
    "ename": "VEH_FROM_TCODE",
    "desc": ""
  },
  {
    "name": "出厂日期",
    "ename": "LCOM_DATE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "制造国（地区）_国家和地区代码",
    "ename": "ORIG_CTY_AREA_CODE",
    "desc": ""
  },
  {
    "name": "制造厂_单位名称",
    "ename": "MANU_COM",
    "desc": ""
  },
  {
    "name": "车辆型号",
    "ename": "VEH_TYPE",
    "desc": ""
  },
  {
    "name": "中文品牌名称",
    "ename": "BRAND_CH",
    "desc": ""
  },
  {
    "name": "英文品牌名称",
    "ename": "BRAND_ENG",
    "desc": ""
  },
  {
    "name": "机动车转向形式代码",
    "ename": "VEH_VEER_FCODE",
    "desc": ""
  },
  {
    "name": "机动车车身颜色代码",
    "ename": "VEH_COLOR_CODE",
    "desc": ""
  },
  {
    "name": "机动车登记照片",
    "ename": "VEH_REG_PICTURE",
    "desc": ""
  },
  {
    "name": "机动车发动机（电动机）功率",
    "ename": "ENGINE_POWER",
    "desc": ""
  },
  {
    "name": "机动车发动机（电动机）号",
    "ename": "ENGINE_NO",
    "desc": ""
  },
  {
    "name": "机动车发动机（电动机）型号",
    "ename": "ENGINE_MODEL",
    "desc": ""
  },
  {
    "name": "发动机缸数",
    "ename": "ENGINE_JAR",
    "desc": ""
  },
  {
    "name": "机动车发动机排量",
    "ename": "ENGINE_DESPL",
    "desc": ""
  },
  {
    "name": "机动车外廓宽度",
    "ename": "VEH_WIDTH",
    "desc": ""
  },
  {
    "name": "机动车外廓高度",
    "ename": "VEH_HEIGHT",
    "desc": ""
  },
  {
    "name": "机动车外廓长度",
    "ename": "VEH_LEN",
    "desc": ""
  },
  {
    "name": "机动车货厢内部长度",
    "ename": "VEH_INSIDE_LEN",
    "desc": ""
  },
  {
    "name": "机动车货厢内部宽度",
    "ename": "VEH_INSIDE_WIDTH",
    "desc": ""
  },
  {
    "name": "机动车货厢内部高度",
    "ename": "VEH_INSIDE_HEIGHT",
    "desc": ""
  },
  {
    "name": "机动车后轴钢板弹簧片数",
    "ename": "VEH_RASPM_AMOUN",
    "desc": ""
  },
  {
    "name": "机动车轴数",
    "ename": "VEH_AXLE_AMOUN",
    "desc": ""
  },
  {
    "name": "机动车轴距",
    "ename": "VEH_AXLE_DISTAN",
    "desc": ""
  },
  {
    "name": "机动车前轮距",
    "ename": "VEH_FW_DISTAN",
    "desc": ""
  },
  {
    "name": "机动车后轮距",
    "ename": "VEH_RW_DISTAN",
    "desc": ""
  },
  {
    "name": "机动车轮胎规格",
    "ename": "VEH_TSIZE",
    "desc": ""
  },
  {
    "name": "机动车轮胎数",
    "ename": "VEH_TNUM",
    "desc": ""
  },
  {
    "name": "机动车总质量",
    "ename": "VEH_TMASS",
    "desc": ""
  },
  {
    "name": "机动车整备质量",
    "ename": "VEH_UMASS",
    "desc": ""
  },
  {
    "name": "机动车核定载质量",
    "ename": "VEH_RLC",
    "desc": ""
  },
  {
    "name": "机动车核定载客人数",
    "ename": "VEH_APC",
    "desc": ""
  },
  {
    "name": "机动车准牵引总质量",
    "ename": "VEH_TWEIG",
    "desc": ""
  },
  {
    "name": "机动车驾驶室前排载客人数",
    "ename": "PFOC_NUM",
    "desc": ""
  },
  {
    "name": "机动车驾驶室后排载客人数",
    "ename": "PBOC_NUM",
    "desc": ""
  },
  {
    "name": "机动车环保达标情况_简要情况",
    "ename": "ESFMV_BRIEF_COND",
    "desc": ""
  },
  {
    "name": "底盘合格证编号",
    "ename": "CHAS_QUAL_NUMB",
    "desc": ""
  },
  {
    "name": "机动车能源种类代码",
    "ename": "VEH_POWER_TCODE",
    "desc": "存在多值情况；机动车能源种类代码字典参考企标CODE_RES_VEH_0021"
  },
  {
    "name": "机动车车辆类型代码",
    "ename": "VEH_TCODE",
    "desc": ""
  },
  {
    "name": "机动车前号牌反光膜编号",
    "ename": "RFLPFMV_NO",
    "desc": ""
  },
  {
    "name": "机动车后号牌反光膜编号",
    "ename": "RLPRF_NO",
    "desc": ""
  },
  {
    "name": "机动车所有人名称",
    "ename": "VEH_PER_NAME",
    "desc": ""
  },
  {
    "name": "机动车所有权代码",
    "ename": "VEH_OWNER_CODE",
    "desc": ""
  },
  {
    "name": "有效期截止日期",
    "ename": "VE_DATE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "机动车强制报废期止",
    "ename": "VEH_RETIRE_DATE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "机动车出厂合格证编号",
    "ename": "MVCM_NO",
    "desc": ""
  },
  {
    "name": "机动车登记证书编号",
    "ename": "MVRC_NO",
    "desc": ""
  },
  {
    "name": "初次登记日期",
    "ename": "REG_DATE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "机动车最近定检日期",
    "ename": "MVROI_DATE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "发证机关_公安机关名称",
    "ename": "ISAU",
    "desc": ""
  },
  {
    "name": "发牌日期",
    "ename": "DATE_LICE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "发登记证书日期",
    "ename": "DATE_REGI_CERT",
    "desc": "yyyyMMdd"
  },
  {
    "name": "发合格证日期",
    "ename": "DATE_CERT_QUAL",
    "desc": "yyyyMMdd"
  },
  {
    "name": "注册流水号",
    "ename": "LSH",
    "desc": ""
  },
  {
    "name": "经办人",
    "ename": "HANDLER",
    "desc": ""
  },
  {
    "name": "管理部门_公安机关名称",
    "ename": "ADMI_DEPA",
    "desc": ""
  },
  {
    "name": "管理辖区_公安机关名称",
    "ename": "ADMIN_AREA",
    "desc": ""
  },
  {
    "name": "注册日期(发牌日期/号牌启用日期)",
    "ename": "LICENSE_START_TIME",
    "desc": "yyyyMMdd"
  },
  {
    "name": "机动车抵押/质押标记代码",
    "ename": "VEH_PLED_CODE",
    "desc": ""
  },
  {
    "name": "机动车状态代码",
    "ename": "VEH_SCODE",
    "desc": "存在多值情况；机动车状态代码字典参考企标CODE_RES_VEH_0020"
  },
  {
    "name": "机动车纳税证明种类代码",
    "ename": "TTPMV_CODE",
    "desc": ""
  },
  {
    "name": "机动车纳税证明编号",
    "ename": "TCMV_NO",
    "desc": ""
  },
  {
    "name": "机动车获得方式代码",
    "ename": "VEH_GET_MCODE",
    "desc": ""
  },
  {
    "name": "机动车使用性质代码",
    "ename": "VEH_USE_NCODE",
    "desc": ""
  },
  {
    "name": "车辆来源",
    "ename": "VEH_SOUR",
    "desc": ""
  },
  {
    "name": "车辆用途",
    "ename": "VEH_USE",
    "desc": ""
  },
  {
    "name": "用途属性",
    "ename": "USE_ATTR",
    "desc": ""
  },
  {
    "name": "销售日期",
    "ename": "SALES_DATE",
    "desc": "yyyyMMdd"
  },
  {
    "name": "销售单位",
    "ename": "SALES_COM",
    "desc": ""
  },
  {
    "name": "销售价格",
    "ename": "SALES_PRICE",
    "desc": ""
  },
  {
    "name": "使用起始日期",
    "ename": "USE_START_TIME",
    "desc": "yyyyMMdd"
  },
  {
    "name": "注销时间",
    "ename": "CAN_DATE",
    "desc": "绝对秒数"
  },
  {
    "name": "数据来源",
    "ename": "DATA_SOUR",
    "desc": "ODS的来源系统"
  },
  {
    "name": "发现地",
    "ename": "DIS_PLACE",
    "desc": "ODS的来源地"
  },
  {
    "name": "发现时间",
    "ename": "DIS_TIME",
    "desc": "绝对秒数"
  },
  {
    "name": "原始资源编码",
    "ename": "ORIG_RES_CODE",
    "desc": "ODS的资源编码"
  },
  {
    "name": "原始数据ID",
    "ename": "ORIG_DATA_ID",
    "desc": "ODS的MD_ID"
  },
  {
    "name": "数据来源可信标记",
    "ename": "CONF_LEVE_IDENT",
    "desc": "记录车辆数据来源，1为默认值，4为车管所注册等可信数据源"
  },
  {
    "name": "机动车号牌颜色代码",
    "ename": "VEH_LIC_COLOR_CODE",
    "desc": ""
  },
  {
    "name": "机动车车身颜色名称",
    "ename": "VEH_COLOR_NAME",
    "desc": ""
  },
  {
    "name": "机动车状态名称",
    "ename": "VEH_SNAME",
    "desc": ""
  },
  {
    "name": "机动车能源种类名称",
    "ename": "VEH_POWER_TNAME",
    "desc": ""
  }
]
2. p2、p3、p4分别设置为final、update、1744601400、20250414
3. DIS_PLACE字段赋值为110101、DATA_SOUR字段赋值为111
4. 建表语句如下：CREATE TABLE fmdbmeta.DWD_RES_NUL_LOG_VEH ( veh_no STRING, drive_lic_tcode STRING, veh_plate_num STRING, veh_idno STRING, veh_from_tcode STRING, lcom_date BIGINT, orig_cty_area_code STRING, manu_com STRING, veh_type STRING, brand_ch STRING, brand_eng STRING, veh_veer_fcode TINYINT, veh_color_code STRING, veh_reg_picture STRING, engine_power STRING, engine_no STRING, engine_model STRING, engine_jar INT, engine_despl STRING, veh_width DOUBLE, veh_height DOUBLE, veh_len DOUBLE, veh_inside_len DOUBLE, veh_inside_width DOUBLE, veh_inside_height DOUBLE, veh_raspm_amoun INT, veh_axle_amoun INT, veh_axle_distan STRING, veh_fw_distan STRING, veh_rw_distan STRING, veh_tsize STRING, veh_tnum STRING, veh_tmass DOUBLE, veh_umass DOUBLE, veh_rlc DOUBLE, veh_apc INT, veh_tweig DOUBLE, pfoc_num INT, pboc_num INT, esfmv_brief_cond STRING, chas_qual_numb STRING, veh_power_tcode STRING, veh_tcode STRING, rflpfmv_no STRING, rlprf_no STRING, veh_per_name STRING, veh_owner_code TINYINT, ve_date BIGINT, veh_retire_date BIGINT, mvcm_no STRING, mvrc_no STRING, reg_date BIGINT, mvroi_date BIGINT, isau STRING, date_lice BIGINT, date_regi_cert BIGINT, date_cert_qual BIGINT, lsh STRING, handler STRING, admi_depa STRING, admin_area STRING, license_start_time BIGINT, veh_pled_code TINYINT, veh_scode STRING, ttpmv_code TINYINT, tcmv_no STRING, veh_get_mcode STRING, veh_use_ncode STRING, veh_sour STRING, veh_use STRING, use_attr STRING, sales_date BIGINT, sales_com STRING, sales_price STRING, use_start_time BIGINT, can_date BIGINT, data_sour INT, dis_place INT, dis_time BIGINT, orig_res_code STRING, orig_data_id STRING, conf_leve_ident INT, veh_lic_color_code STRING, veh_color_name STRING, veh_sname STRING, veh_power_tname STRING, p1 STRING, p2 STRING, p3 STRING, p4 STRING) USING ORC PARTITIONED BY (p1, p2, p3, p4) TBLPROPERTIES ( 'table.ttl.partition' = 'p1', 'table.ttl' = '630720000')
"""


demo3_prompt = """
# 任务
根据下面的建表语句SQL，构造测试数据，使用insert into生成对应插入数据的SQL语句。
# 要求
1. 表结构字段含义如下，尽可能使用仿真数据生成工具填充字段内容
[
  {
    "name": "航班唯一标识",
    "ename": "FLIGHT",
    "desc": "航班唯一标识"
  },
  {
    "name": "航班号",
    "ename": "FLIG_NO",
    "desc": "航班号"
  },
  {
    "name": "始发机场名称",
    "ename": "DEP_AIR",
    "desc": "始发机场名称"
  },
  {
    "name": "终点机场名称",
    "ename": "ARR_AIR",
    "desc": "终点机场名称"
  },
  {
    "name": "始发站行政区划代码",
    "ename": "DEP_CITY_CODE",
    "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空"
  },
  {
    "name": "终点站行政区划代码",
    "ename": "ARR_CITY_CODE",
    "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空"
  }
]
2. 建表语句
CREATE TABLE
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
  ) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE 
"""


demo4_prompt = (
    demo3_prompt
    + """
3. p1, p2, p3, p4分别设置为final, update, 1744601400, 20250414
"""
)
