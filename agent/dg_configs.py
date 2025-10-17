DG_SERVER_BASE_URL = "http://172.17.55.30"

DG_TASK_ADD_URL = "genius/task/add/"

DG_GENERATE_TASK_URL = "genius/api/v1/generate_task/"

DG_TASK_HISTORY = "genius/generate-record/"

DG_NEW_TASK = "genius/page/new-task/"

DG_RULE_PREVIEW = "genius/api/v1/preview_line/"

DG_RULE_CATEGORY = "genius/api/v1/rule_category/"

DG_STORAGE_PATH = "/storec/storea/projects/geniusWeb/espresso/media/genius"


BLACK_DG_RULE_CATEGORY_NAMES = [
    "应用编码",
    "资源编码",
    "学历代码",
    "婚姻状况",
    "政治面貌",
    "宗教信仰",
    "血型",
    "职业分类",
    "地址类型",
    "兵役状况",
    "机动车号牌种类代码",
    "身份关系",
    "身份类型代码",
    "好友关系类型代码",
    "案件类型代码",
    "案件来源代码",
    "动作类型",
    "数据来源",
    "网络应用代码",
    "网络制式代码",
    "运营商和基础网络",
    "通讯类型",
    "GA重点行为代码",
    "GA场景关系代码",
    "WA重点内容分类",
    "WA重点内容代码",
    "数据资源来源类型代码",
    "数据集敏感度代码",
]

DG_FIELD_CATEGORY_CONFIG = [
    {"category": "姓名", "value": "向东"},
    {"category": "姓名拼音", "value": "luanyu"},
    {"category": "姓名拼音-多音", "value": "pangguiying,pangguiyang"},
    {"category": "英文姓名", "value": "Jessica Welch"},
    {"category": "年龄", "value": 31},
    {"category": "性别", "value": "男"},
    {"category": "民族", "value": "哈萨克族"},
    {"category": "出生年月", "value": "1956-03-06"},
    {"category": "身份证", "value": "652201199510238272"},
    {"category": "邮箱", "value": "ixiong@gmail.com"},
    {"category": "手机号", "value": "13056636315"},
    {"category": "QQ号", "value": "5518148"},
    {"category": "微信号", "value": "IkbdYmQlUabYTMkCy"},
    {"category": "微信ID", "value": "wxid_6129507924858"},
    {"category": "护照号", "value": "EG2655087"},
    {"category": "国籍", "value": "柬埔塞"},
    {"category": "纬度", "value": "-51.608116"},
    {"category": "经度", "value": "-164.109435"},
    {"category": "经纬度", "value": ["24.28859", "116.11768"]},
    {"category": "省份", "value": "吉林省"},
    {"category": "城市", "value": "银川市"},
    {"category": "邮编", "value": "630534"},
    {"category": "地址", "value": "江苏省徐州市泉山区金江街道汉中路604号"},
    {"category": "街道地址", "value": "滨江街道平江路796号"},
    {"category": "房屋地址", "value": "河南省安阳地区长垣县天梭街道红山路745号"},
    {"category": "房屋编号", "value": "JQ27077503"},
    {"category": "车辆编号", "value": "18721777051"},
    {"category": "车牌号", "value": "陕M7491Q"},
    {"category": "营业执照编号", "value": "15383150799"},
    {"category": "银行卡号", "value": "4559260525670441"},
    {"category": "信用卡号", "value": "4579463093337123271"},
    {"category": "文章", "value": '"这是一段随机的文章文本内容."'},
    {"category": "密码", "value": "i^_Z6!T4hc"},
    {"category": "IMSI", "value": "460097316525136"},
    {"category": "IMEI", "value": "013942485865164"},
    {"category": "MAC", "value": "6a:9f:72:cd:31:58"},
    {"category": "MAC-大写-1", "value": "CD:35:C6:82:B9:13"},
    {"category": "MAC-大写-2", "value": "AE-36-79-34-2B-51"},
    {"category": "地址类型", "value": "其它"},
    {"category": "部标-车架号", "value": "9PXLB89R1GLLJC5AB"},
    {"category": "公司名称", "value": "新宇龙信息传媒有限公司"},
    {"category": "厂商名称", "value": "戴硕电子科技有限公司"},
    {"category": "公司编号", "value": "15260909632"},
    {"category": "单位编号", "value": "JQ34709347"},
    {"category": "社会统一信用代码", "value": "8E482752K81QT213X6"},
    {"category": "IPV4", "value": "64.54.152.90"},
    {"category": "IPV6", "value": "a6b1:69fe:7d55:5b60:ab4a:2fd0:5fda:8c91"},
    {"category": "URL", "value": "https://www.xiuyingjie.cn/"},
    {"category": "域名", "value": "baidu.cn"},
    {"category": "来源数据资源目录编号", "value": "BLIWbYeACgInBTqGZjeJ"},
    {"category": "UUID", "value": "70ac48c5-9829-4b31-9e88-f11bd7b3c211"},
    {"category": "随机主键", "value": "c1331fd2af684b20857198c3a07a3764"},
    {"category": "随机主键-30", "value": "ec63238858a14f4d9632d33c5de92a"},
    {"category": "MD_ID", "value": "624d620a8b8548a5b6ec20a0b333b97e"},
    {"category": "MD5", "value": "2dab48709de636066729e05a51c8ad73"},
    {"category": "随机串", "value": "出现这样当前以及."},
    {"category": "数字串", "value": "264280"},
    {"category": "英文串", "value": "Type budget yet."},
    {"category": "中文串", "value": "好好学习天天向上."},
    {"category": "年", "value": "1976"},
    {"category": "日期", "value": "1975-01-28"},
    {"category": "日期-2", "value": "19790809"},
    {"category": "当前日期", "value": "2025-06-05"},
    {"category": "当前日期-2", "value": "20250605"},
    {"category": "当月日期", "value": "2025-06-05"},
    {"category": "时间", "value": "2022-12-02 16:48:10"},
    {"category": "时间绝对秒", "value": 970229372},
    {"category": "当前时间", "value": "2025-06-05 14:51:09"},
    {"category": "当前时间绝对秒", "value": 1749106269},
    {"category": "当月时间", "value": "2025-06-04 19:14:03"},
    {"category": "当月时间绝对秒", "value": 1748848272},
    {"category": "警情编号", "value": "JQ21390160"},
    {"category": "案件编号", "value": "JQ57848142"},
    {"category": "香烟品牌", "value": "软玉溪"},
]


if __name__ == "__main__":
    # category_slices = []
    #
    # for category, items in DG_FIELD_CATEGORY_CONFIG.items():
    #     category_slices.extend(items)
    # print(f"Total categories: {len(category_slices)}")
    # print(category_slices)

    print([item.get("category") for item in DG_FIELD_CATEGORY_CONFIG])
    # print(json.dumps(category_slices, ensure_ascii=False, indent=2))
    # with open("dg_field_category_config.json", "w", encoding="utf-8") as f:
    #     json.dump(DG_FIELD_CATEGORY_CONFIG, f, ensure_ascii=False, indent=2)
