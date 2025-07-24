import time
from datetime import datetime

table_en_name = "fmdbmeta.DWD_BEH_TRANS_ENTRY"

current_p3_timestamp = int(time.time())
current_p4_date = datetime.strftime(datetime.now(), "%Y%m%d")

insert_sql = f"INSERT INTO {table_en_name} " \
             f"PARTITION (p1='final', p2='update', p3={current_p3_timestamp}, p4={current_p4_date}) " \
             f"VALUES "

table_schema = [
    {"en_name": "MD_ID", "cn_name": "\u552f\u4e00\u6807\u8bc6", "desc": "", "field_type": "string", "is_require": 0,
     "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "PERSON_NO", "cn_name": "\u4eba\u5458_\u7f16\u53f7", "desc": "", "field_type": "string",
     "is_require": 0, "dict_key": "", "dict_name": "", "example": "610326197810054699"},
    {"en_name": "NAME", "cn_name": "\u59d3\u540d", "desc": "", "field_type": "string", "is_require": 0, "dict_key": "",
     "dict_name": "", "example": "\u6b27\u9633\u6676"},
    {"en_name": "NAME_SPELL", "cn_name": "\u59d3\u540d\u6c49\u8bed\u62fc\u97f3", "desc": "", "field_type": "string",
     "is_require": 0, "dict_key": "", "dict_name": "", "example": "ouyangjing"},
    {"en_name": "SEX", "cn_name": "\u6027\u522b\u4ee3\u7801", "desc": "", "field_type": "byte", "is_require": 0,
     "dict_key": "", "dict_name": "\u6027\u522b", "example": "1"},
    {"en_name": "SEX_DESIG", "cn_name": "\u6027\u522b", "desc": "", "field_type": "string", "is_require": 0,
     "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "CRED_NUM", "cn_name": "\u8bc1\u4ef6\u53f7\u7801", "desc": "", "field_type": "string", "is_require": 1,
     "dict_key": "", "dict_name": "", "example": "610326197810054699"},
    {"en_name": "COMM_CERT_CODE", "cn_name": "\u5e38\u7528\u8bc1\u4ef6\u4ee3\u7801", "desc": "", "field_type": "string",
     "is_require": 1, "dict_key": "", "dict_name": "\u5e38\u7528\u8bc1\u4ef6\u4ee3\u7801", "example": "111"},
    {"en_name": "PROF", "cn_name": "\u804c\u4e1a", "desc": "", "field_type": "string", "is_require": 0, "dict_key": "",
     "dict_name": "", "example": ""},
    {"en_name": "CTY_AREA_CODE", "cn_name": "\u56fd\u5bb6\u548c\u5730\u533a\u4ee3\u7801", "desc": "",
     "field_type": "string", "is_require": 0, "dict_key": "",
     "dict_name": "\u56fd\u5bb6\u548c\u5730\u533a\u5b57\u6bcd\u4ee3\u7801\uff08\u4e09\u5b57\u6bcd\uff09",
     "example": "CHN"},
    {"en_name": "CTY_AREA_NAME", "cn_name": "\u56fd\u5bb6\u548c\u5730\u533a\u540d\u79f0", "desc": "",
     "field_type": "string", "is_require": 0, "dict_key": "", "dict_name": "", "example": "\u4e2d\u56fd"},
    {"en_name": "FORWADD_CTY_AREA_CODE", "cn_name": "\u524d\u5f80\u5730_\u56fd\u5bb6\u548c\u5730\u533a\u4ee3\u7801",
     "desc": "", "field_type": "string", "is_require": 0, "dict_key": "",
     "dict_name": "\u56fd\u5bb6\u548c\u5730\u533a\u5b57\u6bcd\u4ee3\u7801\uff08\u4e09\u5b57\u6bcd\uff09",
     "example": "FRA"},
    {"en_name": "FORWADD_CTY_AREA_NAME", "cn_name": "\u524d\u5f80\u5730_\u56fd\u5bb6\u548c\u5730\u533a\u540d\u79f0",
     "desc": "", "field_type": "string", "is_require": 0, "dict_key": "", "dict_name": "",
     "example": "\u6cd5\u5c5e\u6ce2\u91cc\u5c3c\u897f\u4e9a"},
    {"en_name": "OIC_DATE", "cn_name": "\u51fa\u5165\u5883\u65e5\u671f", "desc": "", "field_type": "string",
     "is_require": 1, "dict_key": "", "dict_name": "", "example": "20250626"},
    {"en_name": "OIC_TIME", "cn_name": "\u51fa\u5165\u5883_\u65f6\u95f4", "desc": "", "field_type": "long",
     "is_require": 1, "dict_key": "", "dict_name": "", "example": "1750907984"},
    {"en_name": "OIC_PORT_CODE", "cn_name": "\u51fa\u5165\u5883\u53e3\u5cb8\u4ee3\u7801", "desc": "",
     "field_type": "string", "is_require": 1, "dict_key": "", "dict_name": "\u5165\u51fa\u5883\u53e3\u5cb8\u4ee3\u7801",
     "example": "244"},
    {"en_name": "OIC_PORT_NAME", "cn_name": "\u51fa\u5165\u5883\u53e3\u5cb8\u540d\u79f0", "desc": "",
     "field_type": "string", "is_require": 1, "dict_key": "", "dict_name": "", "example": "\u4e30\u90fd"},
    {"en_name": "OIC_REAS_CODE", "cn_name": "\u51fa\u5165\u5883\u4e8b\u7531\u4ee3\u7801", "desc": "",
     "field_type": "string", "is_require": 1, "dict_key": "", "dict_name": "\u5165\u5883\u4e8b\u7531", "example": "14"},
    {"en_name": "OIC_REAS_NAME", "cn_name": "\u51fa\u5165\u5883\u4e8b\u7531\u540d\u79f0", "desc": "",
     "field_type": "string", "is_require": 1, "dict_key": "", "dict_name": "", "example": "\u5176\u4ed6"},
    {"en_name": "OIC_PER_TCODE", "cn_name": "\u51fa\u5165\u5883\u4eba\u5458\u7c7b\u522b\u4ee3\u7801", "desc": "",
     "field_type": "string", "is_require": 0, "dict_key": "",
     "dict_name": "\u51fa\u5165\u5883\u4eba\u5458\u5206\u7c7b\u4ee3\u7801", "example": "4B"},
    {"en_name": "OIC_PER_TNAME", "cn_name": "\u51fa\u5165\u5883\u4eba\u5458\u7c7b\u522b\u540d\u79f0", "desc": "",
     "field_type": "string", "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "ISSU_CERT_DATE", "cn_name": "\u53d1\u8bc1\u65e5\u671f", "desc": "", "field_type": "string",
     "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "VISA_TCODE", "cn_name": "\u7b7e\u8bc1\uff08\u5c45\u7559\u8bb8\u53ef\uff09\u79cd\u7c7b\u4ee3\u7801",
     "desc": "", "field_type": "string", "is_require": 0, "dict_key": "",
     "dict_name": "\u7b7e\u8bc1\u79cd\u7c7b\u4ee3\u7801", "example": "O"},
    {"en_name": "VISA_TNAME", "cn_name": "\u7b7e\u8bc1\uff08\u5c45\u7559\u8bb8\u53ef\uff09\u79cd\u7c7b\u540d\u79f0",
     "desc": "", "field_type": "string", "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "TRAF_METH_CODE", "cn_name": "\u4ea4\u901a\u65b9\u5f0f\u4ee3\u7801", "desc": "", "field_type": "byte",
     "is_require": 0, "dict_key": "", "dict_name": "\u4ea4\u901a\u65b9\u5f0f\u4ee3\u7801", "example": "4"},
    {"en_name": "TRAF_METH_NAME", "cn_name": "\u4ea4\u901a\u65b9\u5f0f\u540d\u79f0", "desc": "", "field_type": "string",
     "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "NATION_CODE", "cn_name": "\u56fd\u7c4d\u4ee3\u7801", "desc": "", "field_type": "string",
     "is_require": 0, "dict_key": "",
     "dict_name": "\u56fd\u5bb6\u548c\u5730\u533a\u5b57\u6bcd\u4ee3\u7801\uff08\u4e09\u5b57\u6bcd\uff09",
     "example": "CHN"},
    {"en_name": "VISA_NO", "cn_name": "\u7b7e\u8bc1\uff08\u5c45\u7559\u8bb8\u53ef\uff09\u53f7", "desc": "",
     "field_type": "string", "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "TRAF_TOOL_BRIEF_COND", "cn_name": "\u4ea4\u901a\u5de5\u5177_\u7b80\u8981\u60c5\u51b5", "desc": "",
     "field_type": "string", "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "OIC_IDENT", "cn_name": "\u51fa\u5165\u5883_\u6807\u8bc6", "desc": "", "field_type": "string",
     "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "DATA_SOURCE", "cn_name": "\u6570\u636e\u6e90", "desc": "", "field_type": "int", "is_require": 1,
     "dict_key": "", "dict_name": "\u6570\u636e\u6765\u6e90\u4ee3\u7801", "example": "702"},
    {"en_name": "RESOURCE_ID", "cn_name": "\u539f\u59cb\u8d44\u6e90\u7f16\u7801", "desc": "", "field_type": "string",
     "is_require": 1, "dict_key": "", "dict_name": "", "example": "991C1621"},
    {"en_name": "COLLECT_PLACE", "cn_name": "\u53d1\u73b0\u5730", "desc": "", "field_type": "int", "is_require": 1,
     "dict_key": "", "dict_name": "\u884c\u653f\u533a\u5212", "example": "330100"},
    {"en_name": "GET_METHOD", "cn_name": "\u6570\u636e\u53d1\u73b0\u65b9\u5f0f", "desc": "", "field_type": "int",
     "is_require": 0, "dict_key": "", "dict_name": "", "example": ""},
    {"en_name": "COMPANY_CODE", "cn_name": "\u5382\u5546\u7f16\u7801", "desc": "", "field_type": "long",
     "is_require": 0, "dict_key": "",
     "dict_name": "\u5b89\u5168\u7ba1\u7406\u7cfb\u7edf\u5382\u5bb6\u7ec4\u7ec7\u673a\u6784\u4ee3\u7801",
     "example": ""},
    {"en_name": "CAPTURE_TIME", "cn_name": "\u53d1\u73b0\u65f6\u95f4", "desc": "", "field_type": "long",
     "is_require": 1, "dict_key": "", "dict_name": "", "example": "1750907984"},
    {"en_name": "ORIGINAL_ID", "cn_name": "\u539f\u59cb\u6570\u636eID", "desc": "", "field_type": "string",
     "is_require": 1, "dict_key": "", "dict_name": "",
     "example": "3e59c7f4-f6dd-11ee-b6de-0242bcbd0005_514_991C1621_20250626010304_ce6294a5a6b445deb0529dbcb6c3f292u4l8rp"}]

for item in table_schema:
    # print(item.get("field_type"))
    print(item)

with open("1753263919_p0_0.txt", mode="r", encoding="utf-8") as r:
    content = r.readlines()
    for index, line in enumerate(content, start=1):
        line_value_tuple = tuple(line.rstrip("\n").split("\t"))
        insert_sql += str(line_value_tuple)
        print(index, len(content))
        if index < len(content):
            insert_sql += ", "
        else:
            insert_sql += ";"
    print(insert_sql)
