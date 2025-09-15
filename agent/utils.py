#!/usr/bin/env python
# coding: utf-8
# @File    :   utils.py
# @Time    :   2025/05/09 15:23:17
# @Author  :   toddlerya
# @Desc    :   None

import json
from datetime import datetime, timezone

import aiofiles


async def save_json_data_async(save_json_path, fake_data):
    async with aiofiles.open(save_json_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(fake_data, ensure_ascii=False, indent=2))


FIELD_TYPE_MAP = {"int": int, "string": str}


def today_timestamp_range() -> tuple[str, str]:
    """
    获取当日开始时间（00:00:00）到当前时刻的时间戳区间范围（以秒为单位）。
    :return: (start_timestamp, end_timestamp)
    """
    # 获取当前时间（UTC+0）
    now = datetime.now(timezone.utc)
    # 获取当天的开始时间（00:00:00）
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    # 获取当前时间的时间戳（秒）
    end_timestamp = int(now.timestamp())
    # 获取当天开始时间的时间戳（秒）
    start_timestamp = int(start_of_day.timestamp())
    return str(start_timestamp), str(end_timestamp)
