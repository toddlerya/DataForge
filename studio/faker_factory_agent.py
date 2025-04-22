#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/22 11:45 
# @Author   : guoqun X2590
# @FileName : faker_factory_agent.py
# @Project  : PreviewDataForge

# 字段映射填充Agent
# 主要功能: 根据表字段信息映射FakerFactory API工具的参数，并调用工具生成字段的预填充数据池备用。

from datetime import datetime

import requests

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from utils.llm_util import llm_client, langfuse_handler
from studio.prompt_samples import table_en_name, table_cn_name, table_columns_info


faker_factory_tool_args = """
|     参数     | 说明                                                         |
| :----------: | ------------------------------------------------------------ |
|    color     | 颜色                                                         |
|     job      | 职业                                                         |
|     name     | 中文名字                                                     |
|     sex      | 性别                                                         |
|   address    | 地址信息（行政区划代码、邮编、固话区号、省市信息、社区名称、社区简称、经纬度） |
|    idcard    | 大陆居民身份证号码                                           |
|     age      | 年龄                                                         |
| mobilephone  | 移动电话号码                                                 |
|    email     | 电子邮箱                                                     |
|     imid     | IM类型的用户ID                                               |
|   nickname   | 用户昵称                                                     |
|   username   | 用户名                                                       |
|   password   | 用户密码                                                     |
|   website    | 网站地址                                                     |
|     url      | 网址URL（随机http或https）                                   |
|   airport    | 国内机场信息（IATA编码、城市名称、ICAO编码、机场名称、城市拼音） |
|    voyage    | 国内航班号                                                   |
| airlineinfo  | 国内航空公司信息（代号、航班唯一标识、中文名称）                           |
|  traintrips  | 火车班次（覆盖高铁、动车、特快、普快、城际、旅游专线）       |
|  trainseat   | 火车座号                                                     |
|  flightseat  | 飞机座号                                                     |
|     ipv4     | ipv4的点分型IP地址                                           |
|     ipv6     | ipv6的点分型IP地址                                           |
|     mac      | mac地址（随机大小写，分隔符）                                |
|  useragent   | 浏览器请求头                                                 |
|     imsi     | IMSI（目前只支持国内460开头的）                              |
|     imei     | IMEI（目前支持中国、英国、美国）                             |
|     meid     | MEID（随机大小写）                                           |
|   deviceid   | DEVICEID（设备编号）                                         |
|   telphone   | 固定电话（暂时只支持国内号码）                               |
|   citycode   | 国内长途区号                                                 |
| specialphone | 特殊电话号码（比如10086、110）                               |
| capturetime  | 当前时间绝对秒（10位数字）                                   |
|     date     | 当前时间，数据库日期格式{YYYYMMDD,hh:mm:ss}                  |
|   carbrand   | 汽车品牌（中文）                                             |
"""

faker_tool_prompt = f"""
你是一个数据治理业务专家，现在请完成如下任务。
# 任务
理解表的名称、字段信息，映射到FakerFactory工具的参数中，输出表的字段与工具参数的映射字典关关系，并回填表字段信息的list[dict]结构，每个字段的dict增加两个字段参数: map_arg, reason。
# 表名称
- 中文名称: {table_cn_name}
- 英文名称: {table_en_name}
# 表字段信息
```json
{table_columns_info}
```
# FakerFactory工具参数
{faker_factory_tool_args}
"""

# 输出结果
"""
{
  "表名称": {
    "中文名称": "航班节点表",
    "英文名称": "ADM_GRAPH_NODE_FLIGHT"
  },
  "表字段与工具参数映射关系": [
    {
      "name": "航班唯一标识",
      "ename": "FLIGHT",
      "desc": "航班唯一标识",
      "map_arg": "airlineinfo",
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
      "map_arg": "airport",
      "reason": "airport参数包含机场城市名称"
    },
    {
      "name": "终点机场名称",
      "ename": "ARR_AIR",
      "desc": "终点机场名称",
      "map_arg": "airport",
      "reason": "airport参数包含机场城市名称"
    },
    {
      "name": "始发站行政区划代码",
      "ename": "DEP_CITY_CODE",
      "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
      "map_arg": "address",
      "reason": "address参数包含行政区划代码"
    },
    {
      "name": "终点站行政区划代码",
      "ename": "ARR_CITY_CODE",
      "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
      "map_arg": "address",
      "reason": "address参数包含行政区划代码"
    }
  ]
}
"""

if __name__ == '__main__':
    print(faker_tool_prompt)