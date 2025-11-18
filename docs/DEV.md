## 　 Migration 初始化

### 　 1. 生成

```shell
alembic init migrations
```

### 2. 修改

`migrations/env.py`

```python
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../../')
from server.config import SQLALCHEMY_URL
from model import models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the configs file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option('sqlalchemy.url', SQLALCHEMY_URL)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = models.Base.metadata
```

## 使用

```
alembic revision --autogenerate -m "init db"
alembic upgrade head
alembic downgrade "xxx"
```

# 常用 SQL

```sql
-- 清空表以及重置自增序列
TRUNCATE TABLE environment_info RESTART IDENTITY;
```

```sql
-- 查询盘古字段在哪些盘古表出现过
SELECT DISTINCT t.*
FROM table_meta_data_info t,
     jsonb_array_elements(t.table_fields) AS field
WHERE field->>'en_name' = 'ACTION_TYPE';
```

```sql

-- 获取所有字典不为空的字段名称
SELECT DISTINCT tf.en_name
FROM public.table_meta_data_info t,
     jsonb_to_recordset(t.table_fields) AS tf(en_name text, dict_name text)
WHERE tf.dict_name IS NOT NULL
  AND tf.dict_name <> '' and tf.en_name = 'OS_TYPE';



-- 先查确认要删的数据：
 SELECT ename
FROM public.field_dg_rule_cache
WHERE ename IN (
    SELECT DISTINCT tf.en_name
    FROM public.table_meta_data_info t,
         jsonb_to_recordset(t.table_fields) AS tf(en_name text, dict_name text)
    WHERE tf.dict_name IS NOT NULL AND tf.dict_name <> ''
);

--再执行删除缓存的字段
DELETE FROM public.field_dg_rule_cache
WHERE ename IN (
    SELECT DISTINCT tf.en_name
    FROM public.table_meta_data_info t,
         jsonb_to_recordset(t.table_fields) AS tf(en_name text, dict_name text)
    WHERE tf.dict_name IS NOT NULL AND tf.dict_name <> ''
);
```

# 任务统计

```sql

select
	ti.task_uuid ,
	update_time ,
	ti.table_en_name,
	ti.data_row_count ,
	ti."mode" ,
	ti.client_ip ,
	dg_task_id ,
	task_rule ,
	dg_task_message ,

	ti.dg_task_duration,
	env_name
from
	task_info ti
	 order by create_time desc limit 9000;

-- 按照调用模式分组统计
SELECT
    CASE
        WHEN dg_task_id IS NOT NULL and dg_task_id != ''  THEN 'DG-AI Chat模式'
        ELSE 'DG-AI元数据推荐模式'
    END AS task_mode_type,
    COUNT(*) AS task_count,
    ROUND(AVG(data_row_count)) AS avg_data_row_count,
    MAX(dg_task_duration) AS max_duration,
    MIN(dg_task_duration) AS min_duration,
    STRING_AGG(DISTINCT env_name, ', ') AS env_names,
    STRING_AGG(DISTINCT client_ip, ', ') AS client_ips
FROM
    task_info ti
WHERE
    ti.create_time IS NOT NULL  -- 确保有创建时间
GROUP BY
    CASE
        WHEN dg_task_id IS NOT null  and dg_task_id != '' THEN 'DG-AI Chat模式'
        ELSE 'DG-AI元数据推荐模式'
    END
ORDER BY
    task_count DESC;
```
