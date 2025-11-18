# 数据银行提供的接口服务【已完成】

## 表元数据-数据生成服务【已完成】

```
http://172.16.108.3:25702/data_gen_agent/run

POST

{
    "table_en_name": "fmdbmeta.ODS_POL_PRI_RECPER_BASINF",
    "data_count": 100,
    "env_name": "测试部仿真测试环境",
    "dont_run_dg_task": true
}
```

## 动态查询 SQL 服务【已完成】

http://172.16.108.3:25702/db/dynamic_query

POST

{
"sql": "select \* from table_meta_data_info tmdi where table_cn_name like '%用户%' limit 100;",
"max_count": 10
}

## 查询 SQL【已完成】

```sql
-- 查询有哪些环境名称
select * from environment_info ei ;
-- 查询有哪些表元数据信息，英文名、中文名、环境名称
select table_en_name , table_cn_name, env_name from table_meta_data_info tmdi
```

# 新增单字段 AI 推荐 DG 规则能力

给定字段名称信息（英文名、中文名、数据类型、样例数据等），直接触发 AI 推荐，生成单个的 DG 规则字典对象。

# 新增外部表结构信息推荐完整 DG 规则能力

外部传入表结构元数据，直接触发 AI 推荐，生成完整的 DG 规则配置信息。

# DG 对接待办事项

## 提供 DG 规则查询接口服务【新开发一个】【完成】

http://172.17.55.30/genius/api/v1/rule_category/

## 提供 DG 规则录入接口服务

实际都是自定义规则

## 规则数据预览接口需要改造【新开发一个】【完成】

http://172.17.55.30/genius/get-preview/ 改成了 172.17.55.30/genius/api/v1/preview_line/

现在是个 form 表单，改成 json/application 请求

## AI 生成的任务规则经人工修改后的派生任务记录回调录入流程

### 场景

比如 AI 推荐创建了一个 DG 任务 A，用户发现 A 任务的第 5 个字段不合适，在 DG 页面修改了，然后点创建，这时候 DG 新建了一个任务 B，我们需要记录 A-->B 的这种派生关系

### 逻辑

AI 创建的任务，然后用户对这个任务进行了修改，新建了任务，回调一下数据银行的服务接口 http://10.0.23.57:25702/task/add。

此场景必填字段

```
"table_en_name",
"rule_name",  # 例子 dg_task_plan_8590a134d9a84d319bbe37fcc1d118b0
"task_rule",
"parent_dg_task_id", # 例子 8590a134d9a84d319bbe37fcc1d118b0
"parent_rule_name",  # 例子 dg_task_plan_8590a134d9a84d319bbe37fcc1d118b0
```

详情见接口文档 http://10.0.23.57:25702/docs#/%E4%BB%BB%E5%8A%A1%E7%AE%A1%E7%90%86/add_task_info_task_add_post

## 仅在 DG 新建任务记录同步

调用 http://10.0.23.57:25702/task/add 不需传递 parent_dg_task_id, parent_rule_name

此场景必填字段

```
"table_en_name",
"rule_name", # 例子 dg_task_plan_8590a134d9a84d319bbe37fcc1d118b0
"task_rule",
```

详情见接口文档 http://10.0.23.57:25702/docs#/%E4%BB%BB%E5%8A%A1%E7%AE%A1%E7%90%86/add_task_info_task_add_post

## 支持类似 PG、MYSQL 这种库的字段长度 比如 varchar(30)生成的数据符合长度要求的规则【废弃】

使用自定义规则就好
