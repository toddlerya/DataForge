#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/29 15:05 
# @Author   : guoqun X2590
# @FileName : web.py.py
# @Project  : DataForge

from chainlit.utils import mount_chainlit
from uvicorn import Config, Server
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def index():
    return {"msg": "ok"}


mount_chainlit(app=app, target=r"app.py", path="/app")

if __name__ == '__main__':
    server = Server(
        Config(
            app=app,
            host='0.0.0.0',
            port=int(8000),
            workers=2
        )
    )
    server.run()
