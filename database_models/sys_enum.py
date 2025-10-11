#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/15 17:04
# @Author   : guoqun X2590
# @FileName : sys_enum.py
# @Project  : DataForge

from enum import Enum


class MetaDataSource(str, Enum):
    data_scope = "数据域"
    pangu = "盘古"
    bdos = "BDOS"
    intelligence_analysis_assistant = "深度搜索预警"
    excel_file = "Excel文件"


class EnvironmentStatus(str, Enum):
    enable = "启用"
    disable = "禁用"
    retired = "废弃"
    new = "新建"
