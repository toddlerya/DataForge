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
