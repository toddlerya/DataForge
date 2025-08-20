#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/20 10:20 
# @Author   : guoqun X2590
# @FileName : trans_unicode.py
# @Project  : DataForge

rule_str = """{"col":21,"category":"当前时间绝对秒","name":"","ename":"DISC_TIME","cname":"发现时间","preview":"score: 0, reason: 该字段存储的是Unix时间戳，表示从1970年1月1日00:00:00 UTC到现在的秒数。","value":"","args":{}}"""


print(rule_str.encode('unicode_escape').decode("utf-8"))