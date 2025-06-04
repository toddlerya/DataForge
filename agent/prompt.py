# coding: utf-8
# @Time:     2025/5/8 11:09
# @Author:   toddlerya
# @FileName: prompt.py
# @Project:  DataForge

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

# 定义模板
intent_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是数仓测试专家，你的任务如下\n"
    "1. 识别出数据库表名称(可以多张表，对应table_en_names)\n"
    "2. 期望表约束条件(每张表可以有或者没有约束条件，对应table_conditions)\n"
    "3. 期望生成数据条数(每张表都有条数，对应table_data_count)\n"
    "按照要求输出结构化数据。"
)

intent_human_prompt = HumanMessagePromptTemplate.from_template(
    "分析如下信息并结构化输出: {user_input}\n" "这是用户之前的会话信息: {messages}"
)

intent_prompt = ChatPromptTemplate.from_messages(
    [intent_system_prompt, intent_human_prompt]
)


faker_plan_system_prompt = SystemMessagePromptTemplate.from_template(
    "您是一个智能助手，任务是根据数据库表结构和用户指定的条件，为 Python Faker 库生成数据生成计划配置"
)

faker_plan_human_prompt = HumanMessagePromptTemplate.from_template(
    "数据库表名称: {table_name}\n"
    "表结构信息: {table_schema}\n"
    "用户期望条件: {user_conditions}\n"
    "期望生成数据条数: {num_rows}\n"
    """请为上述表生成一个 Faker 配置。配置应包含 `table_en_name`, `row_count` 和一个 `instructions_for_fields` 对象。
`instructions_for_fields` 对象中的每个键是表中的字段 `field_en_name`，值是一个包含 `faker_func` (例如 "name", "pyint", "numerify", "uuid4", "date_between", "boolean") 和 `faker_parameters` (一个包含传递给 faker func 的参数的字典) 的对象。
请仔细考虑每个字段的 `field_type`, `cn_name`, `sample_value` 和 `constraints`，以及用户的期望条件，来选择最合适的 `faker_func` 和 `faker_parameters`。
例如:
- 对于 `ID is not null`，可以使用 `uuid4`。
- 对于 `phone like '139%'`，可以使用 `numerify` 和类似 `{{'text': '139########'}}` 的参数。
- 对于 `age < 100`，可以使用 `pyint` 和类似 `{{'min_value': 1, 'max_value': 99}}` 的参数。
- 对于布尔类型字段，可以使用 `boolean` provider，例如 `{{'chance_of_getting_true': 50}}`。
- 对于日期类型，可以使用 `date_between`，例如 `{{'start_date': '-1y', 'end_date': 'today'}}`。

输出必须是单个 JSON 对象，并检查输出的instructions_for_fields数量和表字段数量和内容是否一致，且需要保持表结构的字段顺序。

参考资料
faker provider func docs:
{faker_docs}
"""
)

faker_plan_prompt = ChatPromptTemplate.from_messages(
    [faker_plan_system_prompt, faker_plan_human_prompt]
)

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
