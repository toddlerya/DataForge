你是一个数仓业务专家，现在请完成如下任务，
# 任务
生成 ODS_BEIAN_MARKETPLACE_INFO 表的仿真测试数据
# 要求
1. 根据"表结构信息"与"来源样例数据"，根据字段的英文和中文含义，进行映射关联；
2. 数据尽可能真实；
3. 不知道的的数据含义不要随便生成；
4. 遵循表的sql条件，确保生成的数据满足sql条件。
# 输出格式
列表嵌套字典的json结构，每个字典以"表结构信息"的ename参数为key, 样例数据为value
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
    "name": "所属主体ID（主键）",
    "ename": "BUDUNITID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "联系人姓名",
    "ename": "CONTACTOR",
    "desc": "",
    "dic": ""
  },
  {
    "name": "联系人身份证号",
    "ename": "CONTACTORIDNO",
    "desc": "",
    "dic": ""
  },
  {
    "name": "联系人手机号",
    "ename": "CONTACTORPHONE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "创建时间",
    "ename": "CREATETIME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "创建人ID（主键）",
    "ename": "CREATEUSER_ID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "地址：省",
    "ename": "PVS",
    "desc": "",
    "dic": ""
  },
  {
    "name": "地址：地市",
    "ename": "CTY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "地址：县",
    "ename": "CRY",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人证件反面文件",
    "ename": "EMERGENCYER_IDECARDBACKID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人证件正面文件",
    "ename": "EMERGENCYER_IDECARDFRONTID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人证件手持文件",
    "ename": "EMERGENCYER_IDECARDGROUPID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人证件有效期",
    "ename": "EMERGENCYER_IDECARDVALID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人证件号码",
    "ename": "EMERGENCYER_RPBCFTNUM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人证件类型",
    "ename": "EMERGENCYER_RPBCFTTYPE",
    "desc": "",
    "dic": "常用证件代码"
  },
  {
    "name": "应急联络人证件类型中文名",
    "ename": "EMERGENCYER_RPBCFTTYPENOTE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人电子邮箱",
    "ename": "EMERGENCYER_RPBMAIL",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应急联络人手机号",
    "ename": "EMERGENCYER_RPBMOBILE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "工信部备案号",
    "ename": "GXBRECORDNO",
    "desc": "",
    "dic": ""
  },
  {
    "name": "是否为主应用市场",
    "ename": "ISMASTER",
    "desc": "",
    "dic": "判断标识"
  },
  {
    "name": "APP LOGO",
    "ename": "LOGO",
    "desc": "",
    "dic": ""
  },
  {
    "name": "市场名称",
    "ename": "MARKETNAME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "上线时间",
    "ename": "ONLINEDATE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "接入单位名称",
    "ename": "ORGNAME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "应用运行平台",
    "ename": "PLATFORMS",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备案号前缀",
    "ename": "PREFIX",
    "desc": "",
    "dic": ""
  },
  {
    "name": "注册号（备案号）",
    "ename": "REGNO",
    "desc": "",
    "dic": ""
  },
  {
    "name": "注册状态",
    "ename": "REGSTATUS",
    "desc": "",
    "dic": "注册状态"
  },
  {
    "name": "注册完成时间",
    "ename": "REGTIME",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人证件反面",
    "ename": "SAFETYER_IDECARDBACKID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人证件正面",
    "ename": "SAFETYER_IDECARDFRONTID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人证件手持",
    "ename": "SAFETYER_IDECARDGROUPID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人证件有效期",
    "ename": "SAFETYER_IDECARDVALID",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人证件号码",
    "ename": "SAFETYER_RPBCFTNUM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人证件类型",
    "ename": "SAFETYER_RPBCFTTYPE",
    "desc": "",
    "dic": "常用证件代码"
  },
  {
    "name": "安全负责人证件类型中文名",
    "ename": "SAFETYER_RPBCFTTYPENOTE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人电子邮箱",
    "ename": "SAFETYER_RPBMAIL",
    "desc": "",
    "dic": ""
  },
  {
    "name": "安全负责人手机号",
    "ename": "SAFETYER_RPBMOBILE",
    "desc": "",
    "dic": ""
  },
  {
    "name": "业务审核状态",
    "ename": "STATUS",
    "desc": "",
    "dic": "网站备案业务审核状态"
  },
  {
    "name": "单位名称",
    "ename": "UNITNM",
    "desc": "",
    "dic": ""
  },
  {
    "name": "备案审批人ID",
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
# 来源样例数据
```json
[
  {
    "ename": "id",
    "cname": "ID",
    "sample": [
      "test8bbed60ae4f8eb6280585fec071f",
      "test909763856e165a1981bec8cedd13",
      "testba1d3f053f90ade41c93a970cf90"
    ]
  },
  {
    "ename": "BUSINESSTYPE",
    "cname": "业务类型",
    "sample": [
      "1",
      "1",
      "1"
    ]
  },
  {
    "ename": "BUDUNITID",
    "cname": "所属主体ID（主键）",
    "sample": [
      "test369bb4bf4ef59aac06f72d8488d0",
      "test9de5971e4896a6bfd21034f4a3a9",
      "test369bb4bf4ef59aac06f72d8488d0"
    ]
  },
  {
    "ename": "CONTACTOR",
    "cname": "联系人姓名",
    "sample": [
      "郭一凡",
      "赵宏杰",
      "李珍珍"
    ]
  },
  {
    "ename": "CONTACTORIDNO",
    "cname": "联系人身份证号",
    "sample": [
      "140202199309262048",
      "140402197903060010",
      "140321199105044828"
    ]
  },
  {
    "ename": "CONTACTORPHONE",
    "cname": "联系人手机号",
    "sample": [
      "18535117007",
      "13303451505",
      "17735392787"
    ]
  },
  {
    "ename": "createtime",
    "cname": "创建时间",
    "sample": [
      "1704365977000",
      "1705641242000",
      "1704949680000"
    ]
  },
  {
    "ename": "CREATEUSER_ID",
    "cname": "创建人ID（主键）",
    "sample": [
      "test7960836a36a13917aa4ce5ba9834",
      "test872046a9cf1ca64b442e75e5385d",
      "test7960836a36a13917aa4ce5ba9834"
    ]
  },
  {
    "ename": "pvs",
    "cname": "归属地-省",
    "sample": [
      "140000",
      "140000",
      "330000"
    ]
  },
  {
    "ename": "cty",
    "cname": "归属地-城市",
    "sample": [
      "140100",
      "140400",
      "330100"
    ]
  },
  {
    "ename": "cry",
    "cname": "归属地-县区",
    "sample": [
      "140109",
      "140423",
      "330110"
    ]
  },
  {
    "ename": "EMERGENCYER_IDECARDBACKID",
    "cname": "应急联络人证件反面文件",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "EMERGENCYER_IDECARDFRONTID",
    "cname": "应急联络人证件正面文件",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "EMERGENCYER_IDECARDGROUPID",
    "cname": "应急联络人证件手持文件",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "应急联络人证件有效期",
    "cname": "EMERGENCYER_IDECARDVALID",
    "sample": [
      "2042-05-23",
      "2028-10-20",
      "2040-08-27"
    ]
  },
  {
    "ename": "EMERGENCYER_RPBCFTNUM",
    "cname": "应急联络人证件号码",
    "sample": [
      "142433199203270418",
      "140402197903060010",
      "140321199105044828"
    ]
  },
  {
    "ename": "EMERGENCYER_RPBCFTTYPE",
    "cname": "应急联络人证件类型",
    "sample": [
      "111",
      "111",
      "111"
    ]
  },
  {
    "ename": "EMERGENCYER_RPBCFTTYPENOTE",
    "cname": "应急联络人证件类型中文名",
    "sample": [
      "居民身份证",
      "居民身份证",
      "居民身份证"
    ]
  },
  {
    "ename": "应急联络人电子邮箱",
    "cname": "EMERGENCYER_RPBMAIL",
    "sample": [
      "18234088122@126.com",
      "xymidi@163.com",
      "371146181@qq.com"
    ]
  },
  {
    "ename": "EMERGENCYER_RPBMOBILE",
    "cname": "应急联络人手机号",
    "sample": [
      "18234088122",
      "13303451505",
      "17735392787"
    ]
  },
  {
    "ename": "工信部备案号",
    "cname": "GXBRECORDNO",
    "sample": [
      "晋ICP备05000465号",
      "晋ICP备16002266号-1",
      "晋ICP备2023015605号"
    ]
  },
  {
    "ename": "ISMASTER",
    "cname": "是否为主应用市场",
    "sample": [
      "1",
      "1",
      "1"
    ]
  },
  {
    "ename": "LOGO",
    "cname": "APP LOGO",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "MARKETNAME",
    "cname": "市场名称",
    "sample": [
      "小米应用市场",
      "华为应用市场",
      "GooglePlay"
    ]
  },
  {
    "ename": "ONLINEDATE",
    "cname": "上线时间",
    "sample": [
      "2024-02-11",
      "2024-03-11",
      "2024-04-11"
    ]
  },
  {
    "ename": "ORGNAME",
    "cname": "接入单位名称",
    "sample": [
      "赛尔网络有限公司",
      "城北社区锦盛苑小区六号楼三单元1501",
      "北社乡广武村351号"
    ]
  },
  {
    "ename": "PLATFORMS",
    "cname": "应用运行平台",
    "sample": [
      "安卓,IOS",
      "安卓,鸿蒙",
      "安卓,IOS,鸿蒙"
    ]
  },
  {
    "ename": "PREFIX",
    "cname": "备案号前缀",
    "sample": [
      "晋公网安备",
      "晋公网安备",
      "晋公网安备"
    ]
  },
  {
    "ename": "REGNO",
    "cname": "注册号（备案号）",
    "sample": [
      "14010902001625",
      "14042302000160",
      "14032102000213"
    ]
  },
  {
    "ename": "REGSTATUS",
    "cname": "注册状态",
    "sample": [
      "2",
      "2",
      "2"
    ]
  },
  {
    "ename": "REGTIME",
    "cname": "注册完成时间",
    "sample": [
      "15698522821",
      "18303466786",
      "18838113214"
    ]
  },
  {
    "ename": "SAFETYER_IDECARDBACKID",
    "cname": "安全负责人证件反面",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "SAFETYER_IDECARDFRONTID",
    "cname": "安全负责人证件正面",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "SAFETYER_IDECARDGROUPID",
    "cname": "安全负责人证件手持",
    "sample": [
      "",
      "",
      ""
    ]
  },
  {
    "ename": "SAFETYER_IDECARDVALID",
    "cname": "安全负责人证件有效期",
    "sample": [
      "2036-08-12",
      "2028-10-20",
      "2040-08-27"
    ]
  },
  {
    "ename": "SAFETYER_RPBCFTNUM",
    "cname": "安全负责人证件号码",
    "sample": [
      "142225197910111811",
      "140402197903060010",
      "140321199105044828"
    ]
  },
  {
    "ename": "SAFETYER_RPBCFTTYPE",
    "cname": "安全负责人证件类型",
    "sample": [
      "111",
      "111",
      "111"
    ]
  },
  {
    "ename": "SAFETYER_RPBCFTTYPENOTE",
    "cname": "安全负责人证件类型中文名",
    "sample": [
      "居民身份证",
      "居民身份证",
      "居民身份证"
    ]
  },
  {
    "ename": "SAFETYER_RPBMAIL",
    "cname": "安全负责人电子邮箱",
    "sample": [
      "18234088122@126.com",
      "xymidi@163.com",
      "371146181@qq.com"
    ]
  },
  {
    "ename": "SAFETYER_RPBMOBILE",
    "cname": "安全负责人手机号",
    "sample": [
      "13703510316",
      "13303451505",
      "17735392787"
    ]
  },
  {
    "ename": "STATUS",
    "cname": "业务审核状态",
    "sample": [
      "2",
      "2",
      "2"
    ]
  },
  {
    "ename": "UNITNM",
    "cname": "单位名称",
    "sample": [
      "太原理工大学",
      "襄垣县图书馆",
      "山西方客生信息技术服务有限公司"
    ]
  },
  {
    "ename": "AUDITID",
    "cname": "备案审批人ID",
    "sample": [
      "436daf7e5bdda10a4194fa6e7fb100d9",
      "782978019e9c64c7b19188539d7339e2",
      "90ed602fc3a239f835738dfeff08c3ab"
    ]
  },
  {
    "ename": "AUDIT_NAME",
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
      "1705975709000",
      "1705890573000",
      "1705481109000"
    ]
  }
]
```
# 表SQL条件
```json
[{'table_name': 'ODS_BEIAN_MARKETPLACE_INFO', 'where_condition': 'id is not null and BUSINESSTYPE is not null and BUDUNITID is not null and CONTACTOR is not null and CONTACTORIDNO is not null and CONTACTORPHONE is not null and EMERGENCYER_RPBCFTNUM is not null and EMERGENCYER_RPBCFTTYPE is not null and EMERGENCYER_RPBCFTTYPENOTE is not null and EMERGENCYER_RPBMOBILE is not null'}]
```