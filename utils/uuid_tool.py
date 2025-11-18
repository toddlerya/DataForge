#!/usr/bin/env python
# coding: utf-8
# @File    :   uuid.py
# @Time    :   2023/11/16 18:18
# @Author  :   guo qun X2590
# @Desc    :   None


import base64
import uuid


def gen_uid(length: int = 10) -> str:
    """
    生成精简位数的唯一字符串

    Args:
        length (int, optional): 期望的唯一字符串长度. Defaults to 10.

    Returns:
        str: 生成的UUID字符串
    """
    # 生成UUID
    uuid_obj = uuid.uuid4()
    # 将UUID转换为Base64字符串
    b64 = base64.urlsafe_b64encode(uuid_obj.bytes)
    string = b64.decode("utf-8")
    # 返回指定长度为的字符串
    if length < 5:
        length = 5
    return string[:length]


def short_uuid(string: str, length: int = 10) -> str:
    """
    精简UUID为指定位数
    :param string:
    :param length:

    Args:
        uuid (str): 36位长度的UUID字符串
        length (int, optional): 期望UUID字符串的长度. Defaults to 10.

    Returns:
        str: _description_
    """
    uuid_str = str(uuid.uuid3(namespace=uuid.NAMESPACE_DNS, name=string))
    b64 = base64.urlsafe_b64encode(uuid_str.encode("utf-8"))
    string = b64.decode("utf-8")
    # 返回指定长度为的字符串
    if length < 5:
        length = 5
    return string[:length]
