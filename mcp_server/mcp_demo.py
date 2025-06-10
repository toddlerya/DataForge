#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/16 16:32
# @Author   : guoqun X2590
# @FileName : mcp_demo.py
# @Project  : PreviewDataForge

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("demo")


def add(a: int, b: int) -> int:
    """
    Adds a and b
    :param a: first int
    :param b: second int
    :return:
    """
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """
    Multiply a and b
    :param a: first int
    :param b: second int
    :return:
    """
    return a * b


@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
