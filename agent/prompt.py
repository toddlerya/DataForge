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
data_intent_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是数仓测试专家，你的任务如下\n"
    "1. 识别出数据库表名称(可以多张表，对应table_en_names)\n"
    "2. 期望表约束条件(每张表可以有或者没有约束条件，对应table_conditions)\n"
    "3. 期望生成数据条数(每张表都有条数，对应table_data_count)\n"
    "按照要求输出结构化数据。"
)

data_intent_human_prompt = HumanMessagePromptTemplate.from_template(
    "分析如下信息并结构化输出: {user_input}\n"
    "这是用户之前的反馈信息: {human_intent_feedback}"
)

data_intent_prompt = ChatPromptTemplate.from_messages(
    [data_intent_system_prompt, data_intent_human_prompt]
)

dg_category_system_prompt = SystemMessagePromptTemplate.from_template(
    """
您是一位专业的数据分类助手。
您的任务是根据提供的数据库表字段信息以及一个预定义的类别配置信息，来推荐最可能的类别。
您需要输出一个包含推荐类别、置信度（0-100之间）和推荐理由的JSON对象。

**预定义的类别配置信息<config>:**
```
{dg_category_config_data}
```

**任务要求:**
1.  仔细分析用户提供的“数据库字段信息”。
2.  参考“预定义的类别配置信息<config>:”，其中列出了具体 `category` 和对应的示例 `value`。
3.  您的目标是为输入的数据库字段从<config>:中找到最匹配的 `category` 值。
4.  综合考虑字段的中文名、英文名、数据类型以及示例数据与<config>:中各个 `category` 的语义、模式和示例值的相似度。
5.  给出一个0到100之间的整数作为置信度评分（`score`），表示您对推荐的把握程度。
6.  提供推荐该类别的具体理由（`reason`）。
7.  特别注意：所有的类别只能是预定义的<config>中的类别，如果无法找到合适的类别，请返回一个置信度为0的结果, category设置为"数字串"，并说明原因。


**输出格式:**
请严格按照以下JSON格式输出结果，不要包含任何额外的解释或文本，只需一个JSON对象:
`{{"category": "推荐的类别名称", "score": 置信度分数, "reason": "推荐理由说明"}}`

**示例输出 (请根据实际判断替换内容):**
`{{"category": "身份证", "score": 95, "reason": "字段名为'id_card'，示例数据'652201199510238272'是18位数字，符合身份证号码的特征，与<config>中'身份证'条目匹配。"}}`

请基于用户接下来提供的字段信息开始您的分析和推荐。
"""
)

dg_category_human_prompt = HumanMessagePromptTemplate.from_template(
    """
**数据库字段信息:**
字段中文名: {cn_name}
字段英文名: {en_name}
字段类型: {field_type}
字段描述：{desc}
字典名称: {dict_name}
字段示例数据: {sample_value}

**上次尝试的推荐类别错误信息, 请不要重蹈覆辙:**
{last_error_message}
"""
)

dg_category_prompt = ChatPromptTemplate.from_messages(
    [dg_category_system_prompt, dg_category_human_prompt]
)

table_intent_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是数据资产专家，你的任务如下\n"
    "1. 识别出用户期望生成的表类别，对应categories\n"
    "2. 识别出每个类别最小表数量，对应category_table_number_min\n"
    "3. 识别出每个类别最大表数量，对应category_table_number_max\n"
    "3. 识别出每个表的最小字段数量，对应table_field_col_min\n"
    "3. 识别出每个表的最大字段数量，对应table_field_col_max\n"
    "按照要求输出结构化数据。"
)

table_intent_human_prompt = HumanMessagePromptTemplate.from_template(
    "分析如下信息并结构化输出: {user_input}\n"
    "这是用户之前的反馈信息: {human_intent_feedback}"
)

table_intent_prompt = ChatPromptTemplate.from_messages(
    [table_intent_system_prompt, table_intent_human_prompt]
)

table_mapping_dimension_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是资深数据架构师，任务是从现有数据结构中识别新的业务建模机会，将分析的结果按照要求输出结构化数据\n"
    "1. 这些表可以聚合衍生出的新的推荐类别应该在{user_intent_categories}范围内，对应recommend_category\n"
    "2. 创建的新的表英文名称，表名称命名规范为英文全部大写+下划线，对应dimension_table_en_name\n"
    "4. 推荐的置信度评分，对应score\n"
    "5. 推荐的理由，对应reason\n"
    "6. 参考的素材表英文名称清单列表，对应reference_material_table_slice\n"
    "7. 创建的新的表英文名称(`dimension_table_en_name`)不应在参考的素材表英文名称清单列表(`reference_material_table_slice`)范围内\n"
)
table_mapping_dimension_human_prompt = HumanMessagePromptTemplate.from_template(
    "这是我们现有数仓中的一些表元数据"
    "---"
    "{material_table_infos}"
)
table_mapping_dimension_prompt = ChatPromptTemplate.from_messages(
    [table_mapping_dimension_system_prompt, table_mapping_dimension_human_prompt]
)

table_ename_translate_system_prompt = ChatPromptTemplate.from_template(
    "你是数仓软件专家，精通英语翻译，你的任务是把用户给的表名称翻译为英文。"
    "请遵循如下命名规范："
    "1. 全部使用大写英文"
    "2. 英文字符见可以使用`_`分割单词"
    "3. 不可以已`_`开头和结尾"
)

table_ename_translate_human_prompt = ChatPromptTemplate.from_template(
    "用户的输入的表名称如下：{table_name}"
)

table_ename_translate_prompt = ChatPromptTemplate.from_messages(
    [table_ename_translate_system_prompt, table_ename_translate_human_prompt]
)

table_fields_fill_system_prompt = ChatPromptTemplate.from_template(
    "你是资深数据架构师，任务是根据用户提供的已有的素材表字段列表和用户需求设计新特征表信息，将分析的结果按照要求输出结构化数据"
    "1. 理解用户需要创建的新表的名称和含义"
    "2. 根据用户提供的表字段来推荐选取新表所需的字段"
    "3. 只能选取用户提供字段信息，然后输出对应的字段英文名列表"
    "4. 输出为List[str]格式"
    "---"
    "用户提供信息示例"
    "新特征表类别: 人员属性"
    "新特征表名称: 新浪微博_手机号邮箱注册信息"
    """素材表字段列表: `[{{"en_name":"rcid","cn_name":"信息唯一标识"}},{{"en_name":"doma","cn_name":"应用域名"}},{{"en_name":"sccjsj","cn_name":"采集时间"}},{{"en_name":"copl","cn_name":"采集地"}},{{"en_name":"hard","cn_name":"硬件特征串"}},{{"en_name":"osve","cn_name":"终端操作系统版本"}},{{"en_name":"fite","cn_name":"手机号"}},{{"en_name":"nm","cn_name":"注册用户姓名"}},{{"en_name":"birt","cn_name":"用户生日"}},{{"en_name":"sexc","cn_name":"用户性别"}},{{"en_name":"fiph","cn_name":"用户联系电话"}}]`"""
    "---"
    "输出结构化数据示例"
    """["rcid","fite","nm", "birt", "sexc", "fiph"]"""
)

table_fields_fill_human_prompt = ChatPromptTemplate.from_template(
    "用户提供信息如下"
    "---"
    "新特征表类别: {category}"
    "新特征表名称: {table_cn_name}"
    "素材表字段列表: {table_fields_list}"
)

table_fields_fill_prompt = ChatPromptTemplate.from_messages([
    table_fields_fill_system_prompt, table_fields_fill_human_prompt
])

# faker_plan_system_prompt = SystemMessagePromptTemplate.from_template(
#     "您是一个智能助手，任务是根据数据库表结构和用户指定的条件，为 Python Faker 库生成数据生成计划配置"
# )

# faker_plan_human_prompt = HumanMessagePromptTemplate.from_template(
#     "数据库表名称: {table_name}\n"
#     "表结构信息: {table_schema}\n"
#     "用户期望条件: {user_conditions}\n"
#     "期望生成数据条数: {num_rows}\n"
#     """请为上述表生成一个 Faker 配置。配置应包含 `table_en_name`, `row_count` 和一个 `instructions_for_fields` 对象。
# `instructions_for_fields` 对象中的每个键是表中的字段 `field_en_name`，值是一个包含 `faker_func` (例如 "name", "pyint", "numerify", "uuid4", "date_between", "boolean") 和 `faker_parameters` (一个包含传递给 faker func 的参数的字典) 的对象。
# 请仔细考虑每个字段的 `field_type`, `cn_name`, `sample_value` 和 `constraints`，以及用户的期望条件，来选择最合适的 `faker_func` 和 `faker_parameters`。
# 例如:
# - 对于 `ID is not null`，可以使用 `uuid4`。
# - 对于 `phone like '139%'`，可以使用 `numerify` 和类似 `{{'text': '139########'}}` 的参数。
# - 对于 `age < 100`，可以使用 `pyint` 和类似 `{{'min_value': 1, 'max_value': 99}}` 的参数。
# - 对于布尔类型字段，可以使用 `boolean` provider，例如 `{{'chance_of_getting_true': 50}}`。
# - 对于日期类型，可以使用 `date_between`，例如 `{{'start_date': '-1y', 'end_date': 'today'}}`。
#
# 输出必须是单个 JSON 对象，并检查输出的instructions_for_fields数量和表字段数量和内容是否一致，且需要保持表结构的字段顺序。
#
# 参考资料
# faker provider func docs:
# {faker_docs}
# """
# )

# faker_plan_prompt = ChatPromptTemplate.from_messages(
#     [faker_plan_system_prompt, faker_plan_human_prompt]
# )

# prompt_gen_faker_data = """你是数仓测试专家，你的任务是生成虚拟测试数据，按照要求输出结构化数据。
# 需要生成测试数据的表名称:
# {table_en_name_array}
# 需要生成测试数据的表字段信息:
# {table_field_info_array}
# 请根据表字段信息生成测试数据，要求如下:
# {table_conditions_array}
# 每张表所需的数据量:
# {table_data_count_array}
# 注意：
# 1. 每条数据之间都应该有差异，同一个字段在每条数据不应出现重复的内容
# 2. 如果example字段有数据，要参照此字段样例值生成多样性的数据
# 3. 如果没有example样例值，你可以将字段值设置为空
# 4. 最后请检查输出的数据条数是否符合每张表所需的数据量要求
# """


# prompt_create_table_raw_field = """您是数仓建模专家，请仔细遵循以下指示。
# 1. 根据用户提供的表名称和表的字段信息创建数据库表元数据信息.
# 2. 首先确认表名称:
# {table_en_name}
# 3. 然后检查任何可选提供的编辑反馈
# {human_mapping_feedback}
# 4. 生成结构化的数据库表字段元数据信息
# """
