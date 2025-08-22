#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/8/21 15:45 
# @Author   : guoqun X2590
# @FileName : graph_tracer.py
# @Project  : DataForge

import asyncio
import logging
import pathlib
import sys
import uuid
from functools import wraps
from typing import Optional, Dict, Any, Callable

from langgraph.graph import StateGraph
from utils.log import TracedLogger


class LangGraphTracer:
    """LangGraph追踪器, 用于在LangGraph节点中诸如trace_uuid"""

    def __init__(self, traced_logger=None):
        self.traced_logger = traced_logger or TracedLogger()

    def trace_node(self, node_name: str):
        """装饰器: 为LangGraph节点添加追踪功能"""

        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(state: Dict[str, Any], *args, **kwargs):
                self.traced_logger.info(f"Entering node: {node_name}")
                self.traced_logger.debug(f"Node {node_name} input state: {state}")

                try:
                    result = await func(state, *args, **kwargs)
                    self.traced_logger.info(f"Exiting node: {node_name} - Success")
                    self.traced_logger.debug(f"Node {node_name} output: {result}")
                    return result
                except Exception as e:
                    self.traced_logger.error(f"Error in node {node_name}: {str(e)}")
                    raise

            @wraps(func)
            def sync_wrapper(state: Dict[str, Any], *args, **kwargs):
                self.traced_logger.info(f"Entering node: {node_name}")
                self.traced_logger.debug(f"Node {node_name} input state: {state}")

                try:
                    result = await func(state, *args, **kwargs)
                    self.traced_logger.info(f"Exiting node: {node_name} - Success")
                    self.traced_logger.debug(f"Node {node_name} output: {result}")
                    return result
                except Exception as e:
                    self.traced_logger.error(f"Error in node {node_name}: {str(e)}")
                    raise

            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper

        return decorator



class TracedStateGraph(StateGraph):
    """继承StateGraph，添加自动追踪功能"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tracer = LangGraphTracer()
        
    def add_node(self, key: str, action, **kwargs):
        """重写add_node方法，添加自动追踪功能"""
        if callable(action):
            traced_action = self.tracer.trace_node(key)(action)
            return super().add_node(key, traced_action, **kwargs)
        else:
            return super().add_node(key, action, **kwargs)

