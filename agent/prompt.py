# coding: utf-8
# @Time:     2025/5/8 11:09
# @Author:   toddlerya
# @FileName: prompt.py
# @Project:  DataForge


prompt_intent_analyse = """你是数仓建模专家，你的任务是识别出每张表的名称、每张表的约束条件、每张表所需的数据条数，按照要求输出结构化数据。

# 这是是用户的输入信息
{user_input}
# 这是用户的之前的会话信息
{messages}
"""

#
# # 输入示例
# ```markdown
# 数据库表名称
# 1. adm_test
# 2. ods_test
# 期望表约束条件
# 1. adm_test: from_city_code != to_city_code and datetime = 20250508 and ods_test.phone = adm_test.phone
# 2. ods_test: idcard is not null and phone is not null
# 期望生成数据条数
# 1. adm_test: 10
# 2. ods_test: 20
# ```
# # 输出示例:
# ```json
# {{
# "table_en_names": ["adm_test", "ods_test"],
# "table_conditions": {{
#     "adm_test": "from_city_code != to_city_code and datetime = 20250508 and ods_test.phone = adm_test.phone",
#     "ods_test": "idcard is not null and phone is not null"}},
# "table_data_count": {{"adm_test": 10, "ods_test": 20}},
# }}
# ```