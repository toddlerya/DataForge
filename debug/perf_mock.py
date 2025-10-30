#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/4 9:23
# @Author   : guoqun X2590
# @FileName : run.py
# @Project  : DataForge

import asyncio
from random import randint, uniform

from fastapi import FastAPI, Request
from loguru import logger
from uvicorn import Config, Server

app = FastAPI()


@app.get("/perf")
async def read_main(request: Request):
    # 获取所有查询参数
    query_params = request.query_params
    # 提取 min_delay 和 max_delay，支持 float 转换
    min_delay = float(query_params.get("min_delay", 0.5))
    max_delay = float(query_params.get("max_delay", 2.0))
    # 确保 min <= max
    if min_delay > max_delay:
        min_delay, max_delay = max_delay, min_delay
    # 随机睡眠
    current_delay = uniform(min_delay, max_delay)
    logger.info(
        f"min_delay={min_delay} max_delay={max_delay} current_delay={current_delay}"
    )
    await asyncio.sleep(current_delay)
    random_message = "太牛逼啦" * randint(100, 1000)
    return {
        "message": random_message,
        "delay": f"{min_delay}~{max_delay}s",
        "received_params": dict(query_params),
    }


if __name__ == "__main__":
    Server(Config(app=app, host="0.0.0.0", port=9999, workers=1)).run()
