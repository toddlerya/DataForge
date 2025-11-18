#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/28 14:59 
# @Author   : guoqun X2590
# @FileName : run.py.py
# @Project  : DataForge


from uvicorn import Server, Config
from fastapi import FastAPI
from chainlit.utils import mount_chainlit

app = FastAPI()


@app.get("/health")
def read_main():
    return {"message": "Hi"}


mount_chainlit(app=app, target="app_fmdb_insert_sql_gen/app.py", path="/")


if __name__ == "__main__":
    Server(Config(app=app, host="0.0.0.0", port=9804, workers=2)).run()
