你是一个数仓业务专家，现在请完成如下任务，
# 任务
生成 ODS_BEIAN_MAINBODY_INFO 表的仿真测试数据
# 要求
1. 根据"表结构信息"与"来源样例数据"，根据字段的英文和中文含义，进行映射关联；
2. 如果遇到"表结构信息"中的"dic"有值，需要参考"字典码信息"对应部分的"id"字段值；
3. 数据尽可能真实；
4. 不知道的的数据含义不要随便生成；
5. 遵循表的sql条件，确保生成的数据满足sql条件。
# 输出格式
列表嵌套字典的json结构，每个字典以"表结构信息"的ename参数为key, 样例数据为value
# 校验要求
输出的仿真数据JSON的字段要与"表结构信息"一致，具体要求是
1. 输出的仿真数据JSON的字段数量要与"表结构信息"的ename数量一致；
2. 输出的仿真数据JSON的字段名称要与"表结构信息"的ename一致；
# 表结构信息
```json
[
  {
    "name": "ID",
    "ename": "ID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "业务类型",
    "ename": "BUSINESSTYPE",
    "desc": "",
    "dic": "数据操作类型"
  },
  {
    "name": "创建时间",
    "ename": "CREATETIME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "归属地-省",
    "ename": "PVS",
    "desc": "",
    "dic": ""
  },
  {
    "name": "归属地-城市",
    "ename": "CTY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "归属地-县区",
    "ename": "CRY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "身份证反面图片文件名",
    "ename": "IDECARDBACKID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "身份证正面图片文件名",
    "ename": "IDECARDFRONTID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "手持身份证照片文件名",
    "ename": "IDECARDGROUPID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "身份证有效期",
    "ename": "IDECARDVALID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "法定代表姓名",
    "ename": "LGLNM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备注",
    "ename": "MEM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "办公室电话",
    "ename": "OFFTEL",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人常住地址县区",
    "ename": "RPBADSCRY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人常住地址城市",
    "ename": "RPBADSCTY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人常住地址省份",
    "ename": "RPBADSPVS",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人常住地详细地址",
    "ename": "RPBADSSTR",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人证件id",
    "ename": "RPBCFTID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人证件号码",
    "ename": "RPBCFTNUM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人证件类型",
    "ename": "RPBCFTTYPE",
    "desc": "",
    "dic": "常用证件代码"
  },
  {
    "name": "负责人电子邮件",
    "ename": "RPBMAIL",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人手机号码",
    "ename": "RPBMOBILE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "负责人姓名",
    "ename": "RPBNM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "状态",
    "ename": "STATUS",
    "desc": "",
    "dic": "审核状态类型"
  },
  {
    "name": "单位办公地址省",
    "ename": "UITADRPVS",
    "desc": "",
    "dic": ""
  },
  {
    "name": "单位办公地址市",
    "ename": "UITADRCTY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "单位办公地址县区",
    "ename": "UITADRCRY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "单位办公详细地址",
    "ename": "UITADRSTR",
    "desc": "",
    "dic": ""
  },
  {
    "name": "主办单位有效证件文件",
    "ename": "UITCFTID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "主办单位证件号码",
    "ename": "UITCFTNUM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "主办单位证件类型code",
    "ename": "UITCFTTYPE",
    "desc": "",
    "dic": "主办单位证件类型分类"
  },
  {
    "name": "主办单位名称",
    "ename": "UITNM",
    "desc": "",
    "dic": ""
  },
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
  },
  {
    "name": "主办单位性质",
    "ename": "UNITPTY",
    "desc": "",
    "dic": "主办单位性质主分类"
  },
  {
    "name": "主办单位性质-子级",
    "ename": "UNITPTY_SUB",
    "desc": "",
    "dic": "网站主办单位性质代码"
  },
  {
    "name": "最后更新时间",
    "ename": "UPDATETIME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "更新人",
    "ename": "UPDATEUSER",
    "desc": "",
    "dic": ""
  },
  {
    "name": "创建人",
    "ename": "CYBUSRID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备案审批人id",
    "ename": "AUDITID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备案审批人姓名",
    "ename": "AUDIT_NAME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备案审批人单位代码",
    "ename": "AUDIT_UNITCODE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备案审批人单位名称",
    "ename": "AUDIT_UNITNAME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "审核时间",
    "ename": "AUDITTIME",
    "desc": "",
    "dic": ""
  }
]
```
# 字典码信息
## 数据操作类型
```json
[{"name": "新增", "id": "1"}, {"name": "修改", "id": "2"}, {"name": "撤销", "id": "3"}]
```
## 常用证件代码
```json
[
  {
    "name": "居民身份证",
    "id": "111"
  },
  {
    "name": "临时居民身份证",
    "id": "112"
  },
  {
    "name": "户口簿",
    "id": "113"
  },
  {
    "name": "中国人民解放军军官证",
    "id": "114"
  },
  {
    "name": "中国人民武装警察部队警官证",
    "id": "115"
  },
  {
    "name": "暂住证",
    "id": "116"
  },
  {
    "name": "出生医学证明",
    "id": "117"
  },
  {
    "name": "中国人民解放军士兵证",
    "id": "118"
  },
  {
    "name": "中国人民武装警察部队士兵证",
    "id": "119"
  },
  {
    "name": "法官证",
    "id": "121"
  }
]
```
## 审核状态类型
```json
[{"name": "草稿", "id": "1"}, {"name": "审核中", "id": "2"}, {"name": "审核通过", "id": "3"}]
```
## 主办单位证件类型分类
```json
[{"name": "统一社会信用代码证", "id": "1"}, {"name": "营业执照证书", "id": "2"}, {"name": "组织机构代码证", "id": "3"}, {"name": "其他", "id": "9"}]
```
## 主办单位性质主分类
```json
[{"name": "个人", "id": "1"}, {"name": "单位", "id": "2"}]
```
## 网站主办单位性质代码
```json
[{"name": "国防机构", "id": "1"}, {"name": "外国在华文化中心", "id": "10"}, {"name": "群众性团体组织", "id": "11"}, {"name": "司法鉴定机构", "id": "12"}, {"name": "宗教团体", "id": "13"}, {"name": "境外机构", "id": "14"}, {"name": "医疗机构", "id": "15"}, {"name": "公证机构", "id": "16"}, {"name": "集体经济", "id": "17"}, {"name": "仲裁机构", "id": "18"}]
```
# 来源样例数据
```json
[
  {
    "ename": "id",
    "cname": "ID",
    "sample": [
      "01325837e1dd44649172689a91f7e3a4",
      "0195a22d575c4ca9a232575d8e5d2240",
      "0306d71f93a6462bbf4de93f55e520ef"
    ]
  },
  {
    "ename": "businessType",
    "cname": "业务类型",
    "sample": [
      "1",
      "1",
      "1"
    ]
  },
  {
    "ename": "createtime",
    "cname": "创建时间",
    "sample": [
      "1704354911000",
      "1701779076000",
      "1703344243000"
    ]
  },
  {
    "ename": "pvs",
    "cname": "归属地-省",
    "sample": [
      "140000",
      "140000",
      "140000"
    ]
  },
  {
    "ename": "cty",
    "cname": "归属地-城市",
    "sample": [
      "140400",
      "140500",
      "140400"
    ]
  },
  {
    "ename": "cry",
    "cname": "归属地-县区",
    "sample": [
      "140403",
      "140581",
      "140425"
    ]
  },
  {
    "ename": "idecardbackid",
    "cname": "身份证反面图片文件",
    "sample": [
      "http://127.0.0.1:9999/index/attach_20241107181019/c58ecd71-96a9-441c-a2d9-3251a96aef1a.jpg",
      "http://127.0.0.1:9999/index/attach_20241107181019/0f536e88-a220-41ce-9123-a60fca32e6ae.jpg",
      "http://127.0.0.1:9999/index/attach_20241107181019/f6226ecc-0051-4029-84ca-d89680191db1.jpg"
    ]
  },
  {
    "ename": "idecardfrontid",
    "cname": "身份证正面图片文件",
    "sample": [
      "http://127.0.0.1:9999/index/attach_20241107181019/e231c9c7-bc4b-4663-a396-fc535f56c8f8.jpg",
      "http://127.0.0.1:9999/index/attach_20241107181019/7622a8b4-7a8d-4154-b069-7fb4206910cb.jpg",
      "http://127.0.0.1:9999/index/attach_20241107181019/3cbe916d-06d3-4046-8982-b747d3f45ca3.jpg"
    ]
  },
  {
    "ename": "idecardgroupid",
    "cname": "手持身份证照片文件",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "idecardvalid",
    "cname": "身份证有效期",
    "sample": [
      "2099059200000",
      "1747238400000",
      "1688054400000"
    ]
  },
  {
    "ename": "lglnm",
    "cname": "法定代表姓名",
    "sample": [
      "郝少峰",
      "",
      ""
    ]
  },
  {
    "ename": "mem",
    "cname": "备注",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "offtel",
    "cname": "办公室电话",
    "sample": [
      "0355-3559106",
      "",
      ""
    ]
  },
  {
    "ename": "rpbadscry",
    "cname": "负责人常住地址县区",
    "sample": [
      "140403",
      "140581",
      "140425"
    ]
  },
  {
    "ename": "rpbadscty",
    "cname": "负责人常住地址城市",
    "sample": [
      "140400",
      "140500",
      "140400"
    ]
  },
  {
    "ename": "rpbadspvs",
    "cname": "负责人常住地址省份",
    "sample": [
      "140000",
      "140000",
      "140000"
    ]
  },
  {
    "ename": "rpbadsstr",
    "cname": "负责人常住地详细地址",
    "sample": [
      "潞州区城北东街67号",
      "城北社区锦盛苑小区六号楼三单元1501",
      "北社乡广武村351号"
    ]
  },
  {
    "ename": "rpbcftid",
    "cname": "负责人证件id",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "rpbcftnum",
    "cname": "负责人证件号码",
    "sample": [
      "140402198711292014",
      "140581199712018418",
      "140425200206268034"
    ]
  },
  {
    "ename": "rpbcfttype",
    "cname": "负责人证件类型",
    "sample": [
      "111",
      "111",
      "111"
    ]
  },
  {
    "ename": "rpbmail",
    "cname": "负责人电子邮件",
    "sample": [
      "2631679238@qq.com",
      "409126858@qq.com",
      "houcy@geniecc.com"
    ]
  },
  {
    "ename": "rpbmobile",
    "cname": "负责人手机号码",
    "sample": [
      "15698522821",
      "18303466786",
      "18838113214"
    ]
  },
  {
    "ename": "rpbnm",
    "cname": "负责人姓名",
    "sample": [
      "李维超",
      "琚佳宝",
      "候超越"
    ]
  },
  {
    "ename": "status",
    "cname": "状态",
    "sample": [
      "2",
      "2",
      "2"
    ]
  },
  {
    "ename": "uitadrpvs",
    "cname": "单位办公地址省",
    "sample": [
      "140000",
      "",
      ""
    ]
  },
  {
    "ename": "uitadrcty",
    "cname": "单位办公地址市",
    "sample": [
      "140400",
      "",
      ""
    ]
  },
  {
    "ename": "uitadrcry",
    "cname": "单位办公地址县区",
    "sample": [
      "140403",
      "",
      ""
    ]
  },
  {
    "ename": "uitadrstr",
    "cname": "单位办公详细地址",
    "sample": [
      "太行东街271号",
      "",
      ""
    ]
  },
  {
    "ename": "uitcftid",
    "cname": "主办单位有效证件文件",
    "sample": [
      "http://127.0.0.1:9999/index/attach_20241107181019/6b1f77e2-293e-4b9e-91ab-d4783330e769.jpg",
      "",
      ""
    ]
  },
  {
    "ename": "uitcftnum",
    "cname": "主办单位证件号码",
    "sample": [
      "121400004062722259",
      "",
      ""
    ]
  },
  {
    "ename": "uitcfttype",
    "cname": "主办单位证件类型code",
    "sample": [
      "tyshxydmz",
      "",
      ""
    ]
  },
  {
    "ename": "uitnm",
    "cname": "主办单位名称",
    "sample": [
      "长治医学院附属和济医院",
      "",
      ""
    ]
  },
  {
    "ename": "uitregadrpvs",
    "cname": "单位注册地址省",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "uitregadrcty",
    "cname": "单位注册地址市",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "uitregadrcry",
    "cname": "单位注册地址区县",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "uitregadrstr",
    "cname": "单位注册详细地址",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "unitpty",
    "cname": "主办单位性质",
    "sample": [
      "dw",
      "gr",
      "gr"
    ]
  },
  {
    "ename": "unitpty_sub",
    "cname": " 主办单位性质-子级   ",
    "sample": [
      "sydw",
      "",
      ""
    ]
  },
  {
    "ename": "updatetime",
    "cname": "最后更新时间",
    "sample": [
      "1704354911000",
      "1701779076000",
      "1703344243000"
    ]
  },
  {
    "ename": "updateuser",
    "cname": "更新人",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "cybusrid",
    "cname": "创建人",
    "sample": [
      "0bb897d51618316093cf9eafa174bd9a",
      "ae985142ae6cd426bf4dc6d907f9e161",
      "27e0ee75d99d62db84cf101a8046756d"
    ]
  },
  {
    "ename": "auditid",
    "cname": "备案审批人id",
    "sample": [
      "436daf7e5bdda10a4194fa6e7fb100d9",
      "a883bbca3f8bc8814ff676cb0e91829a",
      "90ed602fc3a239f835738dfeff08c3ab"
    ]
  },
  {
    "ename": "audit_name",
    "cname": "备案审批人姓名",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "audit_unitcode",
    "cname": "备案审批人单位代码",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "audit_unitname",
    "cname": "备案审批人单位名称",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "audittime",
    "cname": "审核时间",
    "sample": [
      "1705975709000\n",
      "1704333752000\n",
      "1705481109000\n"
    ]
  }
]
```
# 表SQL条件
```json
[{'table_name': 'ODS_BEIAN_MAINBODY_INFO', 'where_condition': 'id is not null and BUSINESSTYPE is not null and RPBCFTNUM is not null and RPBCFTTYPE is not null and RPBMOBILE is not null and RPBNM is not null and STATUS is not null and UNITPTY is not null'}]
```