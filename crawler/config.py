#!/usr/bin/env python
# coding: utf-8
# @Time     : 2025/5/13 15:32 
# @Author   : guoqun X2590
# @FileName : config.py
# @Project  : DataForge


data_scope_ip_port = "172.17.63.12:12018"
data_scope_resource_url = f"https://{data_scope_ip_port}/offsite/v1/domain/page/resource"
data_scope_resource_detail_url = f"https://{data_scope_ip_port}/offsite/v1/resource/detail"

bdp_cookie = "contextPath=/offsite; citycode=330000; appId=offsite; topoptid=offsite; userToken=5e15bba8e80b4107a6c0194a6ef5ac4a; appToken=112325b2f01b4e15a8de4a92fbec08a3"
bdp_headers = {
    "Cookie": bdp_cookie
}