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
    "1. 识别出数据库表名称(对应table_en_name)\n"
    "2. 期望生成数据条数(对应data_count)\n"
    "3. 环境名称(对应env_name), 若用户没提供环境名称则填写空字符串\n"
    "按照要求输出结构化数据。"
)

data_intent_human_prompt = HumanMessagePromptTemplate.from_template(
    "分析如下信息并结构化输出: {user_input}\n"
    "这是用户之前的反馈信息: {human_intent_feedback}"
)

data_intent_prompt = ChatPromptTemplate.from_messages(
    [data_intent_system_prompt, data_intent_human_prompt]
)

sql_mode_data_intent_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是SQL专家，你的任务如下\n"
    "1. 识别出数据库表名称用户提供的SQL内容, 对应sql\n"
    "2. 期望生成数据条数, 对应data_count\n"
    "按照要求输出结构化数据。"
)

sql_mode_data_intent_human_prompt = HumanMessagePromptTemplate.from_template(
    "分析如下信息并结构化输出: {user_input}\n"
    "这是用户之前的反馈信息: {human_intent_feedback}"
)

sql_mode_data_intent_prompt = ChatPromptTemplate.from_messages(
    [sql_mode_data_intent_system_prompt, sql_mode_data_intent_human_prompt]
)

dg_category_system_prompt = SystemMessagePromptTemplate.from_template(
    """
您是一位专业的数据分类助手。
您的任务是根据提供的数据库表字段信息以及一个预定义的类别配置信息，来推荐最可能的类别。
您需要输出一个包含推荐类别、置信度(0-100之间)和推荐理由的JSON对象。

**预定义的类别配置信息<configs>:**
```
{dg_category_config_data}
```

**任务要求:**
1.  仔细分析用户提供的“数据库字段信息”。
2.  参考“预定义的类别配置信息<configs>:”，其中列出了具体 `category` 和对应的示例 `value`。
3.  您的目标是为输入的数据库字段从<configs>:中找到最匹配的 `category` 值。
4.  综合考虑字段的中文名、英文名、数据类型以及示例数据与<configs>:中各个 `category` 的语义、模式和示例值的相似度。
5.  给出一个0到100之间的整数作为置信度评分(`score`)，表示您对推荐的把握程度。
6.  提供推荐该类别的具体理由(`reason`)。
7.  特别注意：所有的类别只能是预定义的<configs>中的类别，如果无法找到合适的类别，请返回一个置信度为0的结果, category设置为"数字串"，并说明原因。


**输出格式:**
请严格按照以下JSON格式输出结果，不要包含任何额外的解释或文本，只需一个JSON对象:
`{{"category": "推荐的类别名称", "score": 置信度分数, "reason": "推荐理由说明"}}`

**示例输出 (请根据实际判断替换内容):**
`{{"category": "身份证", "score": 95, "reason": "字段名为'id_card'，示例数据'652201199510238272'是18位数字，符合身份证号码的特征，与<configs>中'身份证'条目匹配。"}}`

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

**上次尝试的推荐类别错误信息, 不要重复之前错误的推荐类别:**
{last_error_message}
"""
)

dg_category_prompt = ChatPromptTemplate.from_messages(
    [dg_category_system_prompt, dg_category_human_prompt]
)

sql_mode_dg_category_system_prompt = SystemMessagePromptTemplate.from_template(
    """
您是一位专业的数据分类助手。
您的任务是根据提供的SQL字段信息以及一个预定义的类别配置信息，来推荐最可能的类别。
您需要输出一个包含推荐类别、置信度(0-100之间)和推荐理由的JSON对象。

**预定义的类别配置信息<configs>:**
```
{dg_category_config_data}
```

**任务要求:**
1.  仔细分析用户提供的“SQL字段信息”。
2.  参考“预定义的类别配置信息<configs>:”，其中列出了具体 `category` 和对应的示例 `value`。
3.  您的目标是为输入的数据库字段从<configs>:中找到最匹配的 `category` 值。
4.  综合考虑字段英文名称、字段注释以及字段别名与<configs>:中各个 `category` 的语义、模式的相似度。
5.  给出一个0到100之间的整数作为置信度评分(`score`)，表示您对推荐的把握程度。
6.  提供推荐该类别的具体理由(`reason`)。
7.  特别注意：所有的类别只能是预定义的<configs>中的类别，如果无法找到合适的类别，请返回一个置信度为0的结果, category设置为"数字串"，并说明原因。


**输出格式:**
请严格按照以下JSON格式输出结果，不要包含任何额外的解释或文本，只需一个JSON对象:
`{{"category": "推荐的类别名称", "score": 置信度分数, "reason": "推荐理由说明"}}`

**示例输出 (请根据实际判断替换内容):**
`{{"category": "身份证", "score": 95, "reason": "字段名为'id_card'，根据字段名称含义可能是身份证，与<configs>中'身份证'条目匹配。"}}`

请基于用户接下来提供的字段信息开始您的分析和推荐。
"""
)

sql_mode_dg_category_human_prompt = HumanMessagePromptTemplate.from_template(
    """
**数据库字段信息:**
字段英文名称: {en_name}
字段别名: {alias_name}
字段注释: {comment}

**上次尝试的推荐类别错误信息, 请不要重蹈覆辙:**
{last_error_message}
"""
)

sql_mode_dg_category_prompt = ChatPromptTemplate.from_messages(
    [sql_mode_dg_category_system_prompt, sql_mode_dg_category_human_prompt]
)

table_intent_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是数据资产专家，你的任务如下\n"
    "- 识别出用户期望生成的表类别，对应categories\n"
    "- 识别出需要生成的表数量，对应table_number\n"
    "- 识别出每个表的最小字段数量，对应table_field_col_min\n"
    "- 识别出每个表的最大字段数量，对应table_field_col_max\n"
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
    "2. 推荐新表的表英文名称，表名称命名规范为英文全部大写+下划线，对应recommend_dimension_table_en_name\n"
    "4. 推荐的置信度评分，对应score\n"
    "5. 推荐的理由，对应reason\n"
    "6. 参考的素材表英文名称清单列表，对应recommend_reference_material_table_en_name_slice\n"
    "7. 创建的新的表英文名称(`recommend_dimension_table_en_name`)不应在参考的素材表英文名称清单列表(`recommend_reference_material_table_en_name_slice`)范围内\n"
)
table_mapping_dimension_human_prompt = HumanMessagePromptTemplate.from_template(
    "这是我们现有数仓中的一些表元数据---{material_table_infos}"
)
table_mapping_dimension_prompt = ChatPromptTemplate.from_messages(
    [table_mapping_dimension_system_prompt, table_mapping_dimension_human_prompt]
)

table_ename_translate_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是数仓软件专家，精通英语翻译，你的任务是把用户给的表名称翻译为英文。"
    "请遵循如下命名规范："
    "1. 全部使用大写英文"
    "2. 英文字符见可以使用`_`分割单词"
    "3. 不可以已`_`开头和结尾"
)

table_ename_translate_human_prompt = HumanMessagePromptTemplate.from_template(
    "用户的输入的表名称如下：{table_name}"
)

table_ename_translate_prompt = ChatPromptTemplate.from_messages(
    [table_ename_translate_system_prompt, table_ename_translate_human_prompt]
)

table_fields_fill_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是资深数据架构师，任务是根据用户提供的已有的素材表字段列表和用户需求设计新特征表信息，将分析的结果按照要求输出结构化数据"
    "1. 理解用户需要创建的新表的名称和含义"
    "2. 根据用户提供的表字段来推荐选取新表所需的字段"
    "3. 只能选取用户提供字段信息，然后输出对应的字段英文名列表"
    "4. 选取Top{top_num}最相关的字段"
    "5. 输出为List[str]格式"
    "---"
    "用户提供信息示例"
    "新特征表类别: 人员属性"
    "新特征表名称: 新浪微博_手机号邮箱注册信息"
    """素材表字段列表: `[{{"en_name":"rcid","cn_name":"信息唯一标识"}},{{"en_name":"doma","cn_name":"应用域名"}},{{"en_name":"sccjsj","cn_name":"采集时间"}},{{"en_name":"copl","cn_name":"采集地"}},{{"en_name":"hard","cn_name":"硬件特征串"}},{{"en_name":"osve","cn_name":"终端操作系统版本"}},{{"en_name":"fite","cn_name":"手机号"}},{{"en_name":"nm","cn_name":"注册用户姓名"}},{{"en_name":"birt","cn_name":"用户生日"}},{{"en_name":"sexc","cn_name":"用户性别"}},{{"en_name":"fiph","cn_name":"用户联系电话"}}]`"""
    "---"
    "输出结构化数据示例"
    """["rcid","fite","nm", "birt", "sexc", "fiph"]"""
)

table_fields_fill_human_prompt = HumanMessagePromptTemplate.from_template(
    "用户提供信息如下"
    "---"
    "新特征表类别: {category}"
    "新特征表名称: {table_cn_name}"
    "素材表字段列表: {table_fields_list}"
)

table_fields_fill_prompt = ChatPromptTemplate.from_messages(
    [table_fields_fill_system_prompt, table_fields_fill_human_prompt]
)


explore_chat_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是测试数据智能助手, 根据用户的问题, 选择合适的工具进行调用。"
    "若没有合适的工具可以调用, 请告诉用户你不暂时还不具备这个能力, 无需进行其他回答。"
)

expolore_chat_human_prompt = HumanMessagePromptTemplate.from_template(
    "用户的问题: \n{question}"
)

expolore_chat_prompt = ChatPromptTemplate.from_messages(
    [explore_chat_system_prompt, expolore_chat_human_prompt]
)


# 定义模板
main_intent_system_prompt = SystemMessagePromptTemplate.from_template(
    "你是测试数据智能助手, 分析用户的输入, 识别出以下信息\n"
    "1. 用户任务需要使用的子图(对应graph_name). \n"
    "- 如果是基于提供的明确表名称构造测试数据则填写data_gen_graph\n"
    "- 如果是基于提供的SQL构造测试数据则填写sql_mode_data_gen_graph\n"
    "- 如果都不是则填写expolore_graph\n"
    "- 没有第4种情况, 只能从给定的清单"
    "中[data_gen_graph,sql_mode_data_gen_graph,expolore_graph]3选1\n"
    "按照要求输出结构化数据。"
)

main_intent_human_prompt = HumanMessagePromptTemplate.from_template(
    "分析如下信息并结构化输出: {user_input}\n"
)

main_intent_prompt = ChatPromptTemplate.from_messages(
    [main_intent_system_prompt, main_intent_human_prompt]
)
