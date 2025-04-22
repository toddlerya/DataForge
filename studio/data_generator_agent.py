#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/22 16:16 
# @Author   : guoqun X2590
# @FileName : data_generator_agent.py
# @Project  : PreviewDataForge

# 仿真测试数据生成Agent
# 主要功能: 根据字段样例随机数据、表字段信息、表过滤条件、治理SQL信息生成满足条件的仿真数据。

# 字段样例随机数据样本
# http://172.16.111.6:8001/api/v1/fakerfactory?number=2&columns=airlineinfo,voyage,airport,airport,address,address
table_columns_random_data_sample = [
    {
        "address.zipcode": {
            "zip_code": "641503"
        },
        "airlineinfo": {
            "code": "JD",
            "name": "金鹿航空"
        },
        "airport": {
            "city": "毕节",
            "iata_code": "BFJ",
            "icao_code": "ZUBJ",
            "name": "毕节飞雄机场",
            "pinyin": "BIJIE"
        },
        "voyage": "EU229"
    },
    {
        "address": {
            "zip_code": "318017"
        },
        "airlineinfo": {
            "code": "KA",
            "name": "港龙航空"
        },
        "airport": {
            "city": "银川",
            "iata_code": "INC",
            "icao_code": "ZLIC",
            "name": "银川河东国际机场",
            "pinyin": "YINCHUAN"
        },
        "voyage": "UO6194"
    }
]

table_columns_map_info = {
    "表名称": {
        "中文名称": "航班节点表",
        "英文名称": "ADM_GRAPH_NODE_FLIGHT"
    },
    "表字段与工具参数映射关系": [
        {
            "name": "航班唯一标识",
            "ename": "FLIGHT",
            "desc": "航班唯一标识",
            "map_arg": "airlineinfo.code",
            "reason": "airlineinfo参数包含航班唯一标识"
        },
        {
            "name": "航班号",
            "ename": "FLIG_NO",
            "desc": "航班号",
            "map_arg": "voyage",
            "reason": "voyage参数对应国内航班号"
        },
        {
            "name": "始发机场名称",
            "ename": "DEP_AIR",
            "desc": "始发机场名称",
            "map_arg": "airport.name",
            "reason": "airport参数包含机场城市名称"
        },
        {
            "name": "终点机场名称",
            "ename": "ARR_AIR",
            "desc": "终点机场名称",
            "map_arg": "airport.name",
            "reason": "airport参数包含机场城市名称"
        },
        {
            "name": "始发站行政区划代码",
            "ename": "DEP_CITY_CODE",
            "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
            "map_arg": "address.zipcode",
            "reason": "address参数包含行政区划代码"
        },
        {
            "name": "终点站行政区划代码",
            "ename": "ARR_CITY_CODE",
            "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
            "map_arg": "address.zipcode",
            "reason": "address参数包含行政区划代码"
        }
    ]
}

query_sql_condition = [
    {
        "table_name": "ADM_GRAPH_NODE_FLIGHT",
        "where_condition": "FLIG_NO is not null and DEP_AIR is not null and ARR_AIR is not null and DEP_AIR != ARR_AIR and DEP_CITY_CODE != ARR_CITY_CODE"
    }
]

data_generator_prompt = f"""
你是一个数仓业务专家，现在请完成如下任务。
# 任务
根据表结构字段信息与样例数据映射关系的映射关系、样例数据、表的sql条件等信息构造表的测试数据
# 要求
1. 数据尽可能真实；
2. 不知道的的数据含义不要随便生成，请遵循表字段与样例数据映射关系和样例数据；
3. 遵循表的sql条件，确保生成的数据满足sql条件。
# 输出格式
列表嵌套字典的json结构，每个字典以ename参数为key, 样例数据为value
# 表结构字段信息与样例数据映射关系
```json
{table_columns_map_info}
```
# 样例数据
```json
{table_columns_random_data_sample}
```
# 表SQL条件
```json
{query_sql_condition}
```
"""


if __name__ == '__main__':
    print(data_generator_prompt)