# 杭州 11 万 SQL（百万 SQL 的精简结果）的 dql_point_query（点查）信息统计概要

## dql_point_query（点查） 日志统计概览

杭州 11 万 SQL 日志中，dql_point_query 日志共计 154617 条件，
提取所有 FROM 查询表名称，去重后共计 776 张表；
提取所有 SELECT 查询字段名称，去重后共计 8965 个查询字段；

详情见《11w_sql_dql_point_query_table_info.json》

原始数据见《11W+SQL.csv》

## 杭州 dql_point_query（点查） 的表信息 与 WA 盘古 FMDB 表比对统计

> <mark>点查大多是查massdata库中的FRC表</mark>，fmdbmeta库基本是ORC表，偏分析用，如HETU用的多。

### 概览

| 统计条目                                                     | 统计数量 |
| ------------------------------------------------------------ | -------- |
| 盘古表（massdata+fmdbmeata)总量                              | 3390     |
| 盘古massdata表总量                                           | 1287     |
| 盘古fmdbmeta表总量                                           | 2103     |
| **dql_point_query 表总量（去重后，后续都是去重后的统计，不再赘述）** | 776      |
| dql_point_query 与 盘古表交集（massdata+fmdbmeata)           | 741      |
| dql_point_query 与 盘古差集（杭州独有）                      | 35       |
| dql_point_query未使用的表统计（massdata+fmdbmeata)           | 2649     |
| **dql_point_query未使用的massdata表统计**                    | **561**  |
| **dql_point_query已使用的massdata表统计**                    | **72**6  |

### 盘古表（massdata+fmdbmeata)总量

盘古元数据中的 FMDB 表（仅包含 massdata，fmdbmeta 表）共计 3390 张 FMDB 表；

其中massdata（FRC表）共计1287张，主要是用于查询场景，理论上与dql_point_query（点查）日志的SQL匹配度较高；

其中fmdbmeta（ORC表）共计2103张，主要是用于分析场景；

### dql_point_query 表总量（去重后，后续都是去重后的统计，不再赘述）

杭州 11 万 SQL 日志中，dql_point_query 日志共计 154617 条件，
提取所有 FROM 查询表名称，去重后共计 776 张表；
提取所有 SELECT 查询字段名称，去重后共计 8965 个查询字段。

详情见《11w_sql_dql_point_query_table_info.json》

原始数据见《11W+SQL.csv》

### dql_point_query 与 盘古表交集（massdata+fmdbmeata)

杭州 dql_point_query 共计使用了 741 张盘古 FMDB 表；

详情见《杭州 11 万 SQL【dql_point_query】使用的盘古 FMDB 表清单.xlsx》

### dql_point_query 与 盘古差集（杭州独有）

杭州 dql_point_query 日志中，还出现了 35 张表不在 WA 盘古元数据范围；

#### 样例分析

- 比如杭州出现了`massdata.LOCATION_PERSON`表，使用`LOCATION_PERSON`这个表名称在盘古元数据是能检索到，但是这个表在盘古元数据的注册数据库是`location.LOCATION_PERSON`;
- 比如杭州出现了`massdata.NB_APP_SKE_WXLOG`表，使用`NB_APP_SKE_WXLOG`这个表名称在盘古元数据能检索到，但是这个表在盘古元数据不是`massdata`表，数据库类型是`FILE-tornado`、`FILE-scp`、`FILE-stream`;
- 比如杭州出现了`massdata.NB_APP_SKE_WXMSG`表，使用`NB_APP_SKE_WXMSG`这个表名称在盘古元数据直接就查不到任何信息。

详情见《杭州 11 万 SQL【dql_point_query】只在 dql_point_query 日志中出现的表清单.xlsx》

### dql_point_query未使用的表统计（massdata+fmdbmeata)

杭州 dql_point_query 没有使用的盘古 FMDB 表共计 2649 张；

详情见《杭州 11 万 SQL【dql_point_query】没有使用的盘古 FMDB 表清单.xlsx》

### dql_point_query未使用的massdata表统计

**杭州 dql_point_query 没有使用的盘古 FMDB massdata表共计 561张；**

561 / 1287 = 44%，**有4成多的massdata表没有被业务点查SQL使用**；

详情见《杭州11万SQL【dql_point_query】没有使用的盘古FMDB表清单(massdata).xlsx》

### dql_point_query已使用的massdata表统计

**杭州 dql_point_query 使用的盘古 FMDB massdata表共计 726张；**

726 / 1287 = 56%，**仅有56%的massdata表被业务点查SQL使用**。

详情见《杭州11万SQL【dql_point_query】没有使用的盘古FMDB表清单(massdata).xlsx》
