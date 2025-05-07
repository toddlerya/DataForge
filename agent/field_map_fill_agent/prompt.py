# coding: utf-8
# @Time:     2025/5/7 10:18
# @Author:   toddlerya
# @FileName: prompt.py
# @Project:  DataForge

prompt_create_table_raw_field = """您是数仓建模专家，请仔细遵循以下指示。
1. 根据用户提供的表名称和表的字段信息创建数据库表元数据信息.
2. 首先确认表名称: 
{table_en_name}
3. 然后检查任何可选提供的编辑反馈
{human_mapping_feedback}
4. 生成结构化的数据库表字段元数据信息
"""
