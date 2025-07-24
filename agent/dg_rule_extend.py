#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/24 14:55 
# @Author   : guoqun X2590
# @FileName : dg_rule_extend.py
# @Project  : DataForge


from agent.state import PydanticDataGeniusRule
from agent.utils import today_timestamp_range


def force_update_dg_timestamp_rule(pydantic_data_genius_rule: PydanticDataGeniusRule):
    """
    强制设置DG的时间戳规则
    1. LLM推荐的score为0时，针对字段名称为明显的时间字段的，程序固定回填时间戳，时间戳区间默认取当天时间区间
    2. 当LLM推荐的DG规则为`时间绝对秒`时，默认替换DG规则为`自定义-数字`，然后参数取今日的时间戳范围
    :param pydantic_data_genius_rule:
    :return: PydanticDataGeniusRule
    """
    start_timestamp, end_timestamp = today_timestamp_range()
    # 情况1：部分时间字段推荐不准，兜底逻辑
    if pydantic_data_genius_rule.preview.startswith("score: 0") and "_TIME" in pydantic_data_genius_rule.ename.upper():
        # "preview": "score: 0, reason: 无法找到合适的类别"  && "ename": "DELETE_TIME"
        pydantic_data_genius_rule.category = "自定义-数字"
        pydantic_data_genius_rule.args = {
            "max_": end_timestamp,
            "min_": start_timestamp
        }
        pydantic_data_genius_rule.preview += "【时间字段-由程序强制设置规则为今日时间戳】"
    # 情况2：DG生成的时间戳完全随机，不符合当前时间区间
    elif pydantic_data_genius_rule.category == "时间绝对秒":
        pydantic_data_genius_rule.category = "自定义-数字"
        pydantic_data_genius_rule.args = {
            "max_": end_timestamp,
            "min_": start_timestamp
        }
        pydantic_data_genius_rule.preview += "【时间字段-由程序强制设置规则为今日时间戳】"
    return pydantic_data_genius_rule
