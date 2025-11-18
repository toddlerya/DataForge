#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/11/17 15:42
# @Author   : guoqun X2590
# @Desc     :

import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from uvicorn import Config, Server

app = FastAPI()


@app.get("/events")
async def sse_event(request: Request):
    # 获取所有查询参数
    query_params = request.query_params
    # 提取 min_delay 和 max_delay，支持 float 转换
    max_count = int(query_params.get("max_count", 10))

    async def event_generator(max_count):
        count = 0
        while True:
            if count > max_count:
                break
            yield f'data: {{"count": {count}}}\n\n'
            count += 1
            await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(max_count), media_type="text/event-stream")


if __name__ == "__main__":
    Server(Config(app=app, host="0.0.0.0", port=9921, workers=1)).run()
