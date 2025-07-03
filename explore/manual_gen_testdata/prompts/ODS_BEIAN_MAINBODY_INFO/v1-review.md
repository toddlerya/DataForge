# 错误

## 字段拼写错误
- ds-r1-14b，把`UITADRPVS`字段输出成了`UITADRSPVS`，严重失误，qwen2.5正确。

## 字段丢失

qwen2.5-14b和ds-r1-14b都有这个问题

丢失`UITREGADRPVS`、`UITREGADRCTY`、`UITREGADRCRY`、`UITREGADRSTR`四个字段，
 
```json
[
  {
    "name": "单位注册地址省",
    "ename": "UITREGADRPVS",
    "desc": "",
    "dic": ""
  },
  {
    "name": "单位注册地址市",
    "ename": "UITREGADRCTY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "单位注册地址区县",
    "ename": "UITREGADRCRY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "单位注册详细地址",
    "ename": "UITREGADRSTR",
    "desc": "",
    "dic": ""
  }
]
```