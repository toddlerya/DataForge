# 任务
构造这两张表的测试数据
1. fmdbmeta.DAW_DOMAIN_IP_TOTAL_MERGE ( 域名IP关系求全增量表 )
2. massdata.DAW_DOMAIN_IP_ALL_MERGE ( 域名IP关系求全总量中间表 )

# 要求
1. 满足治理SQL的过滤条件，确保数据能够符合过滤条件
2. 字段数据要丰富真实

# 参考信息
## 表结构信息

```sql
CREATE TABLE
  fmdbmeta.DAW_DOMAIN_IP_TOTAL_MERGE (
    md_id STRING,
    ip BIGINT,
    domain STRING,
    ip_location STRING,
    first_time BIGINT,
    last_time BIGINT,
    ccount BIGINT,
    isp_type INT,
    tcount BIGINT,
    sync_flag INT
  )
```


```sql
CREATE TABLE
  massdata.DAW_DOMAIN_IP_ALL_MERGE (
    md_id STRING,
    ip BIGINT,
    domain STRING,
    ip_location STRING,
    first_time BIGINT,
    last_time BIGINT,
    ccount BIGINT,
    isp_type INT,
    tcount BIGINT,
    sync_flag INT
  )
```

## SQL元数据
```json
[
  {
    "tables_name": null,
    "selected_columns": [
      "MD_ID",
      "IP",
      "DOMAIN",
      "IP_LOCATION",
      "FIRST_TIME",
      "LAST_TIME",
      "CCOUNT",
      "ISP_TYPE",
      "TCOUNT",
      "SYNC_FLAG"
    ],
    "filters": [],
    "udf_functions": []
  },
  {
    "tables_name": null,
    "selected_columns": [
      "MD_ID",
      "IP",
      "DOMAIN",
      "FIRST_TIME",
      "LAST_TIME",
      "CCOUNT",
      "TCOUNT"
    ],
    "filters": [
      "WHERE d.DOMAIN IS NULL"
    ],
    "udf_functions": []
  },
  {
    "tables_name": "fmdbmeta.\"DAW_DOMAIN_IP_ALL_MERGE\" AS a",
    "selected_columns": [
      "MD_ID",
      "IP",
      "DOMAIN",
      "FIRST_TIME",
      "LAST_TIME",
      "CCOUNT",
      "TCOUNT"
    ],
    "filters": [
      "WHERE b.DOMAIN IS NULL"
    ],
    "udf_functions": []
  }
]
```

## 治理SQL
```sql
-- ************************************************************
-- SQL功能描述：IP域名求全全量过滤泛域名
-- 输入表策略：
-- 1、fmdbmeta.DAW_DOMAIN_IP_TOTAL_MERGE ( 域名IP关系求全增量表 )：增量数据
-- 2、massdata.DAW_DOMAIN_IP_ALL_MERGE ( 域名IP关系求全总量中间表 )：全量数据
-- 输出表策略：
-- fmdbmeta.DAW_DOMAIN_IP_ALL_MERGE ( 域名IP关系求全总量中间表 )：全量数据
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
```