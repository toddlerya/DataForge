#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/7/2 10:44
# @Author   : guoqun X2590
# @FileName : base.py
# @Project  : DataForge


import pathlib

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html

# from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

from common.initialization import init_env
from server.api.routers import (
    agent_data_gen,
    agent_sql_mode_data_gen,
    dynamic_query,
    task,
)

# 实例化动态任务调度器
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


init_env()

app = FastAPI(
    title="DataForge",
    description="造数·价值",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

__api_path__ = pathlib.Path(__file__).parent.absolute()

app.mount(
    "/static",
    StaticFiles(directory=__api_path__.joinpath("static").absolute()),
    name="static",
)

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
app.include_router(agent_sql_mode_data_gen.router)
app.include_router(dynamic_query.router)
app.include_router(task.router)


# def custion_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema

#     openapi_schema = get_openapi(
#         title="My API",
#         version="1.0.0",
#         description="API文档",
#         routes=app.routes,
#     )

#     openapi_schema["openapi"] = "3.0.1"
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema


# app.openapi = custion_openapi


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url if app.openapi_url else "",
        title=app.title + "- Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_favicon_url="/static/favicon.png",
    )
