#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/4/25 15:11 
# @Author   : guoqun X2590
# @FileName : pang_config.py.py
# @Project  : DataForge


import pathlib

bash_path = pathlib.Path(r"F:\GITLAB\DataForge")

cookie_data = "contextPath=/catalog; userToken=a4d587b8de914f50a4064ea25a72f66b; appToken=18a687bb7b9d4e4db6fb70bf99eb81e8; JSESSIONID=463E06C3DD672252069C91EB61629BE9; contextPath=/; citycode=330100; appId=pangu; topoptid=pangu; loginIp=10.0.23.57; loginMac=A4-BB-6D-43-BE-0D; JSESSIONID=49DADF6B91C261DA761666BEC2C988D8; userToken=a4d587b8de914f50a4064ea25a72f66b; appToken=18a687bb7b9d4e4db6fb70bf99eb81e8; sessiongovern=79A1E553E6334C24C7C1A58A522D8453"
pangu_headers = {"Cookie": cookie_data}