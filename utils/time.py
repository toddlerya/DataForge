#!/usr/bin/env python
# coding: utf-8
# @File    :   time.py
# @Time    :   2023/11/6 18:53
# @Author  :   guo qun X2590
# @Desc    :   None

from datetime import timezone, date, time
from typing import Any, Tuple, Union
from datetime import datetime, timedelta


from utils.log import logger


def validate_date_format(value):
    try:
        date.fromisoformat(value)
    except ValueError as err:
        return err
    else:
        return None


def validate_time_format(value):
    try:
        time.fromisoformat(value)
    except ValueError as err:
        return err
    else:
        return None


@logger.catch
def now_date_time_str(datetime_format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    获取当前日期时间字符串

    Args:
        datetime_format (str): 日期时间格式. 默认为 `%Y-%m-%d %H:%M:%S`

    Returns:
        str: 格式化后的日期时间字符串
    """
    return datetime.strftime(datetime.now(), datetime_format)


def datetime_str2object(datetime_str: str, datetime_format: str = "%Y-%m-%d %H:%M:%S"):
    """
    年月日字符串转为datetime对象
    Args:
        datetime_str:
        datetime_format:

    Returns:

    """
    try:
        datetime_object = datetime.strptime(datetime_str, datetime_format)
    except Exception as err:
        return False, err, None
    else:
        return True, "ok", datetime_object


def datetime_obj2str(
    datetime_obj: datetime, datetime_format: str = "%Y-%m-%d %H:%M:%S"
):
    """
    datetime对象转为字符串
    Args:
        datetime_obj:
        datetime_format:

    Returns:

    """
    try:
        datetime_str = datetime.strftime(datetime_obj, datetime_format)
    except Exception as err:
        return False, err, None
    else:
        return True, "ok", datetime_str


@logger.catch(reraise=True)
def datetime_2timestamp(datetime_obj: datetime, unit: str = "second") -> int:
    """
    将东八区中国标准时间年月日时分秒字符串转为unix时间戳
    Args:
        datetime_obj: 日期时间对象
        unit: 时间戳单位, 默认为second, 可选millisecond
    Returns:

    """
    datetime_obj.timestamp()
    timestamp = datetime_obj.replace(
        tzinfo=timezone(timedelta(hours=8), name="Asia/Shanghai")
    ).timestamp()
    if unit == "second":
        timestamp = int(timestamp)
    elif unit == "millisecond":
        timestamp = int(timestamp * 1000)
    return timestamp


@logger.catch(reraise=True)
def timestamp2_datetime(
    timestamp: Union[int, float], hours: int = 8
) -> Tuple[bool, str, Any]:
    """
    将unix时间戳转为东八区中国标准时间 日期时间对象

    Args:
        timestamp (int, float): unix时间戳
        hours (int): 时区, 默认东八区
    Returns:
        datetime: 日期时间对象
    """
    if isinstance(timestamp, (int, float)):
        datetime_obj = datetime.utcfromtimestamp(timestamp) + timedelta(hours=hours)
        return True, "ok", datetime_obj
    else:
        return False, "unix timestamp not int or float", None


def next_time(
    base_date: str = "",
    base_time: str = "",
    days_offset: int = 0,
    hours_offset: int = 0,
    minutes_offset: int = 0,
    seconds_offset: int = 0,
) -> tuple[str, ValueError] | tuple[Any, None]:
    """
    计算下一次的日期时间

    Args:
        base_date (str, optional): 默认基准日期. Defaults to datetime.now().strftime("%Y-%m-%d").
        base_time (str, optional): 默认基准时间. Defaults to datetime.now().strftime("%H:%M:%S").
        days_offset (int, optional): 天数偏移量. Defaults to 0.
        hours_offset (int, optional): 小时偏移量. Defaults to 0.
        minutes_offset (int, optional): 分钟偏移量. Defaults to 0.
        seconds_offset (int, optional): 秒数偏移量. Defaults to 0.
    """

    def __offset_value_int_validate(value: int, name: str):
        if not isinstance(value, int):
            return ValueError(f"{name}参数必须为整数")
        else:
            return None

    if base_date.strip() == "":
        base_date = datetime.now().strftime("%Y-%m-%d")
    if base_time.strip() == "":
        base_time = datetime.now().strftime("%H:%M:%S")

    logger.trace(
        f"next_time args==> base_date: {base_date} base_time: {base_time} "
        f"days_offset: {days_offset} hours_offset: {hours_offset} "
        f"minutes_offset: {minutes_offset} seconds_offset: {seconds_offset}"
    )
    # 校验参数是否合法
    for check_result in [
        validate_date_format(base_date),
        validate_time_format(base_time),
        __offset_value_int_validate(value=days_offset, name="days_offset"),
        __offset_value_int_validate(value=hours_offset, name="hours_offset"),
        __offset_value_int_validate(value=minutes_offset, name="minutes_offset"),
        __offset_value_int_validate(value=seconds_offset, name="seconds_offset"),
    ]:
        if check_result:
            return "", check_result
    next_time_base = datetime.strptime(f"{base_date} {base_time}", "%Y-%m-%d %H:%M:%S")
    delta = timedelta(
        days=days_offset,
        hours=hours_offset,
        minutes=minutes_offset,
        seconds=seconds_offset,
    )
    next_time = next_time_base + delta
    logger.trace(
        f"next_time ==> current_time: {datetime.now()} "
        f"next_time_base: {next_time_base} delta: [{delta}] next_time: {next_time}"
    )
    # 格式 2023-04-24T22:11:03+08:00 %Y-%m-%dT%H:%M:%S%z，其中 %Y 表示年份，%m 表示月份，%d 表示日，%H 表示小时，%M 表示分钟，%S 表示秒，%z 表示时区偏移量
    status, message, datetime_str = datetime_obj2str(
        next_time, "%Y-%m-%dT%H:%M:%S+08:00"
    )
    if status is False:
        return "", ValueError(message)
    return datetime_str, None
