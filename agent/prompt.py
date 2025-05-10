# coding: utf-8
# @Time:     2025/5/8 11:09
# @Author:   toddlerya
# @FileName: prompt.py
# @Project:  DataForge


prompt_intent_analyse = """你是数仓建模专家，你的任务是识别出每张表的名称、每张表的约束条件、每张表所需的数据条数，按照要求输出结构化数据。
这是是用户的输入信息
{user_input}
这是用户的之前的会话信息
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

"""


prompt_create_table_raw_field = """您是数仓建模专家，请仔细遵循以下指示。
1. 根据用户提供的表名称和表的字段信息创建数据库表元数据信息.
2. 首先确认表名称:
{table_en_name}
3. 然后检查任何可选提供的编辑反馈
{human_mapping_feedback}
4. 生成结构化的数据库表字段元数据信息
"""
