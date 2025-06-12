import json

import requests

data = {"task":  {"step": "2", "name": "goodluck", "type_": "模型",
                 "modelName": "pyramid...V1.9.14...数仓...NB_APP_ADM_PORTRAIT_CASE_SARYXQ_TMP...odsV2.3.0",
                 "mode": "edit", "task_id": "24f37bc5-535d-48e0-a3ba-8041832c49b4", "duration": "undefined 秒",
                 "output_filesize": "8.05 KB"},
        "rules": [{"category": "姓名", "ename": "AJBH", "name": "", "args": {}, "value": "", "cname": "案件编号",
                   "preview": "刘平", "col": 1},
                  {"category": "姓名拼音", "ename": "SARYXQ", "name": "", "args": {}, "value": "",
                   "cname": "涉案人员详情", "preview": "wangfengying", "col": 2}],
        "separator": "",
        "rows": 1000,
        "cols": 2,
        "send": {"send_type": 1, "tip": "无配置，点击刷新或添加。", "connect_test": True,
                 "connect_test_tip": "connect test success!", "table_test": True, "table_test_tip": "",
                 "schema": "public"},
        "saveRuleFile": False,
        "blockSize": 100000,
        "source": "",
        "alam": {"isRule": "1", "rule": "", "name": ""},
        }

# resp = requests.post("http://172.17.55.30/genius/task/add/", data=data,
#                     headers={'content-type': 'application/x-www-form-urlencoded; charset=UTF-8'})
# print(resp.status_code)
# print(resp.content)
import httpx

with httpx.Client() as client:
    resp = client.get("http://172.17.55.30/genius/generate-record/", params={"limit": "10"})
    print(resp.status_code)
    print(resp.url)
    print(resp.headers)