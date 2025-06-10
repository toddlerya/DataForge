# coding: utf-8
# @Time:     2025/5/8 11:09
# @Author:   toddlerya
# @FileName: prompt.py
# @Project:  DataForge


prompt_intent_analyse = """
# 你是数仓测试专家，你的任务如下
1. 识别出数据库表名称(可以多张表，对应table_en_names)
2. 期望表约束条件(每张表可以有或者没有约束条件，对应table_conditions)
3. 期望生成数据条数(每张表都有条数，对应table_data_count)
按照要求输出结构化数据。

# 这是是用户的输入信息
{user_input}
# 这是用户的之前的会话信息
{messages}
"""

prompt_gen_faker_data = """你是数仓测试专家，你的任务是生成虚拟测试数据，按照要求输出结构化数据。
需要生成测试数据的表名称:
{table_en_name_array}
需要生成测试数据的表字段信息:
{table_field_info_array}
请根据表字段信息生成测试数据，要求如下:
{table_conditions_array}
每张表所需的数据量:
{table_data_count_array}
注意：
1. 每条数据之间都应该有差异，同一个字段在每条数据不应出现重复的内容
2. 如果example字段有数据，要参照此字段样例值生成多样性的数据
3. 如果没有example样例值，你可以将字段值设置为空
4. 最后请检查输出的数据条数是否符合每张表所需的数据量要求
"""


prompt_create_table_raw_field = """您是数仓建模专家，请仔细遵循以下指示。
1. 根据用户提供的表名称和表的字段信息创建数据库表元数据信息.
2. 首先确认表名称:
{table_en_name}
3. 然后检查任何可选提供的编辑反馈
{human_mapping_feedback}
4. 生成结构化的数据库表字段元数据信息
"""
