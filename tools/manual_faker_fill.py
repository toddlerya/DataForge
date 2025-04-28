#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/28 16:35 
# @Author   : guoqun X2590
# @FileName : manual_faker_fill.py
# @Project  : DataForge

import json


with open(r"F:\GITLAB\DataForge\output\pangu\bxf\ODS_BEIAN_MARKETPLACE_INFO.json", mode='r', encoding='utf-8') as tb_r:
    table_info = json.load(tb_r)

with open(r'F:\GITLAB\DataForge\output\fake_sample_data\ODS_BEIAN_MARKETPLACE_INFO.json', mode='r', encoding='utf-8') as faker_r:
    faker_data_input = json.load(faker_r)


values_array_tuple: list = list()

first_value = []
second_value = []
third_value = []
for index, col in enumerate(table_info):
    col_name = col.get("name")
    col_faker_data = faker_data_input[index]
    print(col_name, col_faker_data)
    first_value.append(col_faker_data['sample'][0])
    second_value.append(col_faker_data['sample'][1])
    third_value.append(col_faker_data['sample'][2])

first_value.extend(["final", "update", "1745830299", "20250428"])
second_value.extend(["final", "update", "1745830299", "20250428"])
third_value.extend(["final", "update", "1745830299", "20250428"])

print(len(first_value))
print(len(second_value))
print(len(third_value))

print(f'insert into fmdbmeta.ODS_BEIAN_MARKETPLACE_INFO values {tuple(first_value)}, {tuple(second_value)}, {tuple(third_value)};')

