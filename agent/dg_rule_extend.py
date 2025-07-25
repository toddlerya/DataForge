#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/24 14:55 
# @Author   : guoqun X2590
# @FileName : dg_rule_extend.py
# @Project  : DataForge


from agent.state import PydanticDataGeniusRule
from agent.utils import today_timestamp_range


def force_update_dg_rule(pydantic_data_genius_rule: PydanticDataGeniusRule):
    # 依次进行检查若符合条件则应用更新规则
    pydantic_data_genius_rule = force_update_dg_timestamp_rule(pydantic_data_genius_rule)
    pydantic_data_genius_rule = force_update_dg_data_color_id_rule(pydantic_data_genius_rule)
    pydantic_data_genius_rule = force_update_dg_datetime_rule(pydantic_data_genius_rule)
    return pydantic_data_genius_rule


def force_update_dg_timestamp_rule(pydantic_data_genius_rule: PydanticDataGeniusRule):
    """
    强制设置DG的时间戳规则
    1. LLM推荐的score为0时，针对字段名称为明显的UNIX时间戳字段的，程序固定回填时间戳，时间戳默认使用`当前时间绝对秒`
    2. 当LLM推荐的DG规则为`时间绝对秒`时，更新为`当前时间绝对秒`
    :param pydantic_data_genius_rule:
    :return: PydanticDataGeniusRule
    """
    # 情况1：部分时间字段推荐不准，兜底逻辑
    if pydantic_data_genius_rule.preview.startswith("score: 0") and "_TIME" in pydantic_data_genius_rule.ename.upper():
        # "preview": "score: 0, reason: 无法找到合适的类别"  && "ename": "DELETE_TIME"
        pydantic_data_genius_rule.category = "当前时间绝对秒"
        pydantic_data_genius_rule.preview += "【时间字段-由程序强制设置规则为当前时间绝对秒】"
    # 情况2：DG生成的时间戳完全随机，不符合当前时间区间
    elif pydantic_data_genius_rule.category == "时间绝对秒":
        pydantic_data_genius_rule.category = "当前时间绝对秒"
        pydantic_data_genius_rule.preview += "【时间字段-由程序强制设置规则为当前时间绝对秒】"
    return pydantic_data_genius_rule


def force_update_dg_datetime_rule(pydantic_data_genius_rule: PydanticDataGeniusRule):
    """
    强制设置DG的日期时间规则
    :param pydantic_data_genius_rule:
    :return: PydanticDataGeniusRule
    """
    # 情况1：部分时间字段推荐不准，兜底逻辑
    if pydantic_data_genius_rule.preview.startswith("score: 0") and "_DATE" in pydantic_data_genius_rule.ename.upper():
        # "preview": "score: 0, reason: 无法找到合适的类别"  && "ename": "CERT_DATE"
        pydantic_data_genius_rule.category = "当前日期"
        pydantic_data_genius_rule.preview += "【日期字段-由程序强制设置规则为当前日期】"
    # 情况2：DG生成的日期完全随机，不符合当前日期
    elif pydantic_data_genius_rule.category == "日期":
        pydantic_data_genius_rule.category = "当前日期"
        pydantic_data_genius_rule.preview += "【日期字段-由程序强制设置规则为当前日期】"
    # 情况3:
    elif pydantic_data_genius_rule.category == "时间":
        pydantic_data_genius_rule.category = "当前时间"
        pydantic_data_genius_rule.preview += "【时间字段-由程序强制设置规则为当前时间】"
    return pydantic_data_genius_rule


def force_update_dg_data_color_id_rule(pydantic_data_genius_rule: PydanticDataGeniusRule):
    """
    强制给data_color_id字段增加dg标识
    :param pydantic_data_genius_rule:
    :return:
    """
    if "DATA_COLOR_ID" in pydantic_data_genius_rule.ename.upper():
        pydantic_data_genius_rule.category = "自定义-字符串"
        pydantic_data_genius_rule.name = "dg_data_color_id"
        pydantic_data_genius_rule.args = {
            "head": "dg_",
            "chars_in": "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "tail": "",
            "max_": "32",
            "min_": "32"
        }
        pydantic_data_genius_rule.preview += "【数据染色字段-由程序强制设置规则为DG前缀】"
    return pydantic_data_genius_rule


if __name__ == '__main__':
    rule1 = PydanticDataGeniusRule(**{
        "col": 9,
        "category": "数字串",
        "name": "",
        "ename": "REASON",
        "cname": "提取原因",
        "preview": "score: 0, reason: 字段示例数据为JSON格式的数组，包含多个对象，每个对象有'mrk'、'dir'、'status'等键，这与预定义的任何类别都不匹配。经过仔细检查，没有发现符合的类别，因此置信度设为0。",
        "value": "[{\"mrk\":\"郑云\",\"dir\":\"0\",\"status\":\"2\"}]",
        "args": {}
    })
    rule2 = PydanticDataGeniusRule(**{
      "col": 10,
      "category": "时间绝对秒",
      "name": "",
      "ename": "FIRST_TIME",
      "cname": "首次关联时间",
      "preview": "score: 90, reason: 字段示例数据'1745333599'是一个时间戳，表示自1970年1月1日以来的秒数，与<configs>中'时间绝对秒'条目匹配。",
      "value": "1745333599",
      "args": {}
    })
    rule3 = PydanticDataGeniusRule(**{
      "col": 5,
      "category": "手机号",
      "name": "",
      "ename": "SECOND_VALUE",
      "cname": "属性类型二的值",
      "preview": "score: 90, reason: 字段示例数据'18871733578'是11位数字，符合中国大陆手机号码的格式，与<configs>中'手机号'条目匹配。",
      "value": "18871733578",
      "args": {}
    })
    rule4 = PydanticDataGeniusRule(**{
      "col": 7,
      "category": "数字串",
      "name": "",
      "ename": "DATA_COLOR_ID",
      "cname": "来源",
      "preview": "score: 0, reason: 无法找到合适的类别，因为'137C005'包含字母和数字，但没有匹配的预定义类别。",
      "value": "137C005",
      "args": {}
    })
    rule5 = PydanticDataGeniusRule(**{
      "col": 10,
      "category": "数字串",
      "name": "",
      "ename": "SOME_TIME",
      "cname": "关联时间",
      "preview": "score: 0, reason: 。",
      "value": "1745333599",
      "args": {}
    })
    rule6 = PydanticDataGeniusRule(**{
      "col": 10,
      "category": "数字串",
      "name": "",
      "ename": "SOME_DATE",
      "cname": "关联日期",
      "preview": "score: 0, reason: 。",
      "value": "1745333599",
      "args": {}
    })
    rules = [rule1, rule2, rule3, rule4, rule5, rule6]
    print([(r.category, r.name) for r in rules])
    rules = [force_update_dg_rule(rule) for rule in rules]
    print([(r.category, r.name) for r in rules])
