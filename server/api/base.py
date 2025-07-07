#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 10:44
# @Author   : guoqun X2590
# @FileName : base.py
# @Project  : DataForge


import sys

from apscheduler.schedulers.background import BackgroundScheduler

import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from config import (
    CONF_DATA_PATH,
    SAVE_DATA_PATH,
    SQLALCHEMY_AUTO_COMMIT,
    SQLALCHEMY_AUTO_FLUSH,
    SQLALCHEMY_ECHO,
    SQLALCHEMY_URL,
    DG_PLAN_PATH,
    DG_PAYLOAD_PATH,
    TABLE_MODELS_PATH
)
from utils.log import logger
from utils.db import Database
from utils.file import create_dir
from server.api.routers import agent_data_gen

# 实例化动态任务调度器
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


@logger.catch(reraise=True)
def get_db():
    db = Database(
        url=SQLALCHEMY_URL,
        echo=SQLALCHEMY_ECHO,
        auto_flush=SQLALCHEMY_AUTO_FLUSH,
        auto_commit=SQLALCHEMY_AUTO_COMMIT,
    )
    try:
        yield db
    finally:
        db.session.close()


def init_env():
    """
    初始化运行环境
    Returns:

    """
    # 创建数据目录
    for path in [SAVE_DATA_PATH, DG_PLAN_PATH, DG_PAYLOAD_PATH, TABLE_MODELS_PATH, CONF_DATA_PATH]:
        logger.info(f"创建所需目录: {path}")
        status, message = create_dir(str(path))
        if status is False:
            logger.error(message)
            sys.exit(1)


init_env()

app = FastAPI(
    title="DataForge",
    description="造数·价值",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

__api_path__ = pathlib.Path(__file__).parent.absolute()

# app.mount(
#     "/static",
#     StaticFiles(directory=__api_path__.joinpath("static").absolute()),
#     name="static",
# )

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test")
async def test():
    return {"message": "Be Happy"}


app.include_router(agent_data_gen.router)

# @app.get('/docs', include_in_schema=False)
# async def custom_swagger_ui_html():
#     return get_swagger_ui_html(
#         openapi_url=app.openapi_url,
#         title=app.title + '- Swagger UI',
#         oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
#         swagger_js_url='/static/swagger-ui-bundle.js',
#         swagger_css_url='/static/swagger-ui.css',
#         swagger_favicon_url='/static/favicon.png'
#     )
#
#
# @app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
# async def swagger_ui_redirect():
#     return get_swagger_ui_oauth2_redirect_html()
#
#
# @app.get("/redoc", include_in_schema=False)
# async def redoc_html():
#     return get_redoc_html(
#         openapi_url=app.openapi_url,
#         title=app.title + "- ReDoc",
#         redoc_js_url="/static/redoc.standalone.js",
#     )
