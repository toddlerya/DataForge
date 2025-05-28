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
