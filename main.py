#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/3 14:35 
# @Author   : guoqun X2590
# @FileName : main.py.py
# @Project  : DataForge
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from chainlit.utils import mount_chainlit

app = FastAPI()


@app.get("/app")
def read_main():
    return {"message": "Hi"}


# mount_chainlit(app=app, target="app_data_gen/chatbot.py", path="/data_gen_app")
mount_chainlit(app=app, target="app_table_gen/app.py", path="/table_gen_app")


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=9800, reload=True)
