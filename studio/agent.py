#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/15 15:40
# @Author   : guoqun X2590
# @FileName : agent.py
# @Project  : PreviewDataForge

from datetime import datetime

import requests

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from utils.llm_util import llm_client, langfuse_handler

from prompts import demo4_prompt


def add(a: int, b: int) -> int:
    """
    Adds a and b
    :param a: first int
    :param b: second int
    :return:
    """
    return a + b


def multiply(a: int, b: int) -> int:
    """
    Multiply a and b
    :param a: first int
    :param b: second int
    :return:
    """
    return a * b


def now_date_time_str(datetime_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前日期时间字符串

    Args:
        datetime_format (str): 日期时间格式. 默认为 `%Y-%m-%d %H:%M:%S`

    Returns:
        str: 格式化后的日期时间字符串
    """
    return datetime.strftime(datetime.now(), datetime_format)


def call_faker_factory(columns: str, number: int) -> list[dict]:
    """
    调用仿真数据生成工具生成所需的字段仿真数据
    ## 支持的数据内容为
    | 序号   |      参数      | 说明                                    |
    | :--- | :----------: | ------------------------------------- |
    | 1    |    color     | 颜色                                    |
    | 2    |     job      | 职业                                    |
    | 3    |     name     | 中文名字                                  |
    | 4    |     sex      | 性别                                    |
    | 5    |   address    | 地址信息（地区编号、邮编、固话区号、省市信息、社区名称、社区简称、经纬度） |
    | 6    |    idcard    | 大陆居民身份证号码                             |
    | 7    |     age      | 年龄                                    |
    | 8    | mobilephone  | 移动电话号码                                |
    | 9    |    email     | 电子邮箱                                  |
    | 10   |     imid     | IM类型的用户ID                             |
    | 11   |   nickname   | 用户昵称                                  |
    | 12   |   username   | 用户名                                   |
    | 13   |   password   | 用户密码                                  |
    | 14   |   website    | 网站地址                                  |
    | 15   |     url      | 网址URL（随机http或https）                   |
    | 16   |   airport    | 国内机场信息（IATA编码、城市名称、ICAO编码、机场名称、城市拼音）  |
    | 17   |    voyage    | 国内航班号                                 |
    | 18   | airlineinfo  | 航班唯一标识, 国内航空公司信息（代号、中文名称）                     |
    | 19   |  traintrips  | 火车班次（覆盖高铁、动车、特快、普快、城际、旅游专线）           |
    | 20   |  trainseat   | 火车座号                                  |
    | 22   |  flightseat  | 飞机座号                                  |
    | 23   |     ipv4     | ipv4的点分型IP地址                          |
    | 24   |     ipv6     | ipv6的点分型IP地址                          |
    | 25   |     mac      | mac地址（随机大小写，分隔符）                      |
    | 26   |  useragent   | 浏览器请求头                                |
    | 27   |     imsi     | IMSI（目前只支持国内460开头的）                   |
    | 28   |     imei     | IMEI（目前支持中国、英国、美国）                    |
    | 29   |     meid     | MEID（随机大小写）                           |
    | 30   |   deviceid   | DEVICEID（设备编号）                        |
    | 31   |   telphone   | 固定电话（暂时只支持国内号码）                       |
    | 32   |   citycode   | 国内长途区号                                |
    | 33   | specialphone | 特殊电话号码（比如10086、110）                   |
    | 34   | capturetime  | 当前时间绝对秒（10位数字）                        |
    | 35   |     date     | 当前时间，数据库日期格式{YYYYMMDD,hh:mm:ss}       |
    | 36   |   carbrand   | 汽车品牌（中文）       |
    ## 生成的数据自动内容，为list[dict]嵌套结构，例如：
        columns=idcard,name,mobilephone
        number=2
        输出结果为
        [
           {
              "idcard": "371321194912241095",
              "mobilephone": "+8613587694173",
              "name": "逄高爽"
           },
           {
              "idcard": "220106201205120037",
              "mobilephone": "+8617056471167",
              "name": "奚语风"
           }
        ]
    Args:
        columns: 字段英文名称，多个字段用英文逗号分割，例如idcard,name,mobilephone
        number: 数据条数

    Returns:

    """
    payload = {"number": number, "columns": columns}
    print(f"call_faker_factory payload: {payload}")
    resp = requests.get(
        url="http://172.16.111.6:8001/api/v1/fakerfactory", params=payload
    )
    if resp.status_code != 200:
        return [{"message": "服务异常，无法生成仿真数据"}]
    result = resp.json().get("data", [{}])
    print(f"call_faker_factory result: {result}")
    return result


tools = [call_faker_factory]

llm_with_tools = llm_client.bind_tools(tools, parallel_tool_calls=False)

sys_message = SystemMessage(
    content="You are a helpful assistant tasked with writing performing arithmetic on a set of inputs."
)


# node
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_message] + state["messages"])]}


# Build graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)
builder.add_edge("tools", "assistant")
react_graph = builder.compile().with_config({"callbacks": [langfuse_handler]})


def draw_graph():
    print(react_graph.get_graph().draw_mermaid())


def demo1():
    messages = [HumanMessage(content=demo4_prompt)]
    messages = react_graph.invoke({"messages": messages})
    print(messages)
    for message in messages.values():
        for item in message:
            print(type(item), item)


if __name__ == "__main__":
    draw_graph()
    print("=" * 20)
    demo1()
