#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/29 14:43 
# @Author   : guoqun X2590
# @FileName : app.py.py
# @Project  : DataForge

import json
import chainlit as cl
import pandas as pd
from chainlit.input_widget import Select, Switch, Slider, Tags


@cl.step(type="tool")
async def tool(table_name: str):
    await cl.sleep(2)
    return f"Response from the tool. table_name: {table_name}"


@cl.on_chat_start
async def start():
    settings = await cl.ChatSettings(
        [
            Select(
                id="model",
                label="DeepSeek",
                values=["DeepSeek-R1-Distill-Qwen-14B-AWQ"],
                initial_index=0
            ),
            Switch(id="Streaming", label="Stream Toknes", initial=True),
            Slider(
                id="temperature",
                label="temperature",
                initial=0.6,
                min=0,
                max=2,
                step=0.1
            ),
            Tags(id="停止符", label="停止符", initial=["Answer:"])
        ],
    ).send()

    print(settings)

    res = await cl.AskUserMessage(content="请输入你需要构造的表名称", timeout=20).send()
    print("hello", cl.user_session.get("id"))
    if res:
        tool_res = await tool(res.get("output", ""))
        await cl.Message(
            content=f"收到: \ntable_name: {res['output']}\ntool_res: {tool_res}"
        ).send()


@cl.on_settings_update
async def setup_agent(settings):
    print("on_setting_update", settings)
    await cl.send_window_message(f"change settings: {settings}")


@cl.on_message
async def message_test(message: cl.Message):
    content = message.content
    print(f"message: {content}")

    if "表格" in content:
        data = {
            'area_code': ['371502101297', '632822100208', '451424205205', '420902101211', '610323106202',
                          '230231105211',
                          '330602101233', '410522105211', '410727200000', '371122120200'],
            'area_name': ['山东,聊城,东昌府,沙镇,小吕', '青海,海西,都兰,察汉乌苏,上滩东', '广西,崇左,大新,恩城,如龙',
                          '湖北,孝感,孝南,孝南区西河,双堰', '陕西,宝鸡,岐山,青化,凤家庄',
                          '黑龙江,齐齐哈尔,拜泉,国富,卫民',
                          '浙江,绍兴,越城,灵芝,大庆寺', '河南,安阳,安阳,柏庄,后林都', '河南,新乡,封丘,城关',
                          '山东,日照,莒县,果庄,前果庄村'],
            'city_code': ['0635', '0977', '1771', '0712', '0917', '0452', '0575', '0372', '0373', '0633'],
            'lat': ['36.338237', '36.301119', '22.735910', '31.003230', '34.408778', '47.686409', '30.086804',
                    '36.208688',
                    '35.041198', '35.778071'],
            'lng': ['115.791973', '98.090831', '107.096186', '114.018159', '107.819450', '126.337441', '120.533014',
                    '114.372285', '114.418882', '118.745254'],
            'name': ['小吕村委会', '上滩东村委会', '如龙村民委员会', '双堰村委会', '凤家庄村委会', '卫民村民委员会',
                     '大庆寺村委会', '后林都村民委员会', '城关乡', '前果庄村村委会'],
            'short_name': ['小吕', '上滩东', '如龙', '双堰', '凤家庄', '卫民', '大庆寺', '后林都', '城关', '前果庄村'],
            'zip_code': ['252032', '816199', '532311', '432013', '722402', '164703', '312066', '455111', '453399',
                         '276533']}
        df = pd.DataFrame(data)
        elements = [cl.Dataframe(data=df, display="inline", name="DataFrame")]
        await cl.Message(content="仿真数据", elements=elements).send()
    elif "文件" in content:
        elements = [
            cl.File(
                name="2025-W14_1744074746.md",
                url="http://172.17.55.71:9000/Other/DepartmentWeekReport/2025-W14_1744074746.md",
                display="inline"
            ),
        ]
        await cl.Message(content="文件下载", elements=elements).send()
    else:
        await cl.Message(content=content).send()


@cl.on_chat_end
def end():
    print("goodbye", cl.user_session.get("id"))
