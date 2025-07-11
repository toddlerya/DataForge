#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/10 10:13
# @Author   : guoqun X2590
# @FileName : utils.py
# @Project  : DataForge


from typing import Optional

from fastapi import Request


def extract_client_ip(request: Request) -> Optional[str]:
    """
    从请求中提取真实的客户端IP，按优先级检查各种可能的头部字段
    :param request:
    :return:
    """
    ip_headers = ["X-Forwarded-For", "X-Real-IP", "X-Forwarded", "X-Cluster-Client-IP"]
    for header in ip_headers:
        # X-Forwarded-For可能包含多个IP，格式：client, proxy1, proxy2
        ip = request.headers.get(header)
        if ip:
            if header == "X-Forwarded-For":
                ip = ip.split(",")[0].strip()

            # 验证IP格式，简单点
            if ip and ip != "unknown":
                return ip

    # 如果所有头部都没有，返回直接连接的客户端IP
    return request.client.host if request.client else "127.0.0.1"
