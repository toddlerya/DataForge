# coding: utf-8
# @Time:     2025/5/7 16:03
# @Author:   toddlerya
# @FileName: mock_data.py
# @Project:  DataForge


from dataclasses import dataclass, asdict


class MockTableMetadata:
    ODS_POL_EIV_DOMAIN_WHOIS = [
        {
            "desc": "md5(SEARCH_URL,URL_DOMAIN,URL)",
            "ename": "MD_ID",
            "name": "系统数据唯一标识ID",
        },
        {
            "desc": "参考数据来源系统字典，现场对标没有可以补充",
            "ename": "COL_SOUR_SYS",
            "name": "数据采集来源系统",
        },
        {
            "desc": "参考数据来源系统字典对应的名称",
            "ename": "COL_SOUR_SYS_REMARK",
            "name": "数据采集来源系统备注",
        },
        {
            "desc": "参考数据来源部门字典，现场对标没有可以补充",
            "ename": "COL_SOUR_DEP",
            "name": "数据采集来源部门",
        },
        {
            "desc": "填入数据来源的六位行政区划代码",
            "ename": "COL_SOUR_PLAC",
            "name": "数据采集来源地",
        },
        {
            "desc": "指数据接入到大数据平台的时间",
            "ename": "COLL_TIME",
            "name": "采集时间",
        },
        {
            "desc": "从原始数据里面获取，填入STG表的原始表名",
            "ename": "COL_SOUR_TABLE",
            "name": "数据采集来源表名",
        },
        {
            "desc": "从原始数据里面获取，填入STG表的主键值",
            "ename": "ORIG_DATA_ID",
            "name": "原始系统接入主键",
        },
        {
            "desc": "从原始数据里面获取，这里指业务的更新时间，选取数据的业务性质的更新时间，默认更新时间不可大于当前时间，对于无业务更新时间统一约定为-1",
            "ename": "UPD_TIME",
            "name": "更新时间",
        },
        {
            "desc": "从原始数据里面获取，指整条数据是否有效，从原始数据判断数据已经删除填写“1”，否则填“0”",
            "ename": "INFO_DELE_JUDGE_FLAG",
            "name": "信息删除_判断标识",
        },
        {
            "desc": "数据敏感级别编码",
            "ename": "DATA_SENS_LEVE_NO",
            "name": "数据敏感级别编码",
        },
        {
            "desc": "数据库回溯标识符",
            "ename": "DATBAS_RECSOU_TAG",
            "name": "数据库回溯标识符",
        },
        {"desc": "业务标签标识", "ename": "BUS_TAG_FLAG", "name": "业务标签标识"},
        {"desc": "行为标签标识", "ename": "BEH_TAG_FLAG", "name": "行为标签标识"},
        {
            "desc": "字段说明：域名（二级域名，部分二级域名会带有国家后缀，也认定为二级域名）\n样例数据：www.qdsrmyy.com",
            "ename": "DOMAIN",
            "name": "域名",
        },
        {
            "desc": "字段说明：域名的唯一标识，是注册服务商分配的一个ID\n样例数据：113108974_domain_com-vrsn",
            "ename": "REGISTRY_DOMAIN_ID",
            "name": "域名ID",
        },
        {
            "desc": "样例数据：Xin Net Technology Corporation",
            "ename": "REGISTRAR",
            "name": "注册服务商",
        },
        {
            "desc": "字段说明：注册服务商互联网数字分配机构ID\n样例数据：120",
            "ename": "REGISTRAR_IANA_ID",
            "name": "注册服务商IANA ID",
        },
        {
            "desc": "字段说明：注册服务商WHOIS服务器(whois 用来查询域名的ip以及所有者等信息的传输协议)\n样例数据：whois.paycenter.com.cn",
            "ename": "REGISTRAR_WHOIS_SERVER",
            "name": "注册服务商WHOIS服务器",
        },
        {
            "desc": "样例数据：http://www.xinnet.com",
            "ename": "REGISTRAR_URL",
            "name": "注册服务商网址",
        },
        {
            "desc": "样例数据：supervision@xinnet.com",
            "ename": "REGISTRAR_CONTACT_EMAIL",
            "name": "注册服务商电子邮件",
        },
        {
            "desc": "样例数据：86.4008182233",
            "ename": "REGISTRAR_CONTACT_PHONE",
            "name": "注册服务商联系电话",
        },
        {
            "desc": "字段说明：域名的建立时间\n样例数据：1078214400",
            "ename": "CREATION_TIME",
            "name": "域名建立时间",
        },
        {
            "desc": "字段说明：域名的更新时间\n样例数据：1612312997",
            "ename": "UPDATED_TIME",
            "name": "域名更新时间",
        },
        {
            "desc": "字段说明：域名的到期时间\n样例数据：1646284971",
            "ename": "EXPIRATION_TIME",
            "name": "域名到期时间",
        },
        {"desc": "", "ename": "REGISTRANT_ORGANIZATION", "name": "注册单位名称"},
        {"desc": "样例数据：JS", "ename": "REGISTRANT_PROVINCE", "name": "注册省名称"},
        {"desc": "样例数据：CN", "ename": "REGISTRANT_COUNTRY", "name": "注册国家名称"},
        {
            "desc": "样例数据：supervision@xinnet.com",
            "ename": "REGISTRANT_EMAIL",
            "name": "注册电子邮件",
        },
        {"desc": "", "ename": "ADMIN_ORGANIZATION", "name": "管理员单位名称"},
        {"desc": "", "ename": "ADMIN_PROVINCE", "name": "管理员省名称"},
        {"desc": "", "ename": "ADMIN_COUNTRY", "name": "管理员国家名称"},
        {
            "desc": "样例数据：supervision@xinnet.com",
            "ename": "ADMIN_EMAIL",
            "name": "管理员电子邮件",
        },
        {"desc": "", "ename": "TECH_ORGANIZATION", "name": "技术单位名称"},
        {"desc": "", "ename": "TECH_PROVINCE", "name": "技术单位省名称"},
        {"desc": "", "ename": "TECH_COUNTRY", "name": "技术单位国家名称"},
        {
            "desc": "样例数据：supervision@xinnet.com",
            "ename": "TECH_EMAIL",
            "name": "技术单位电子邮件",
        },
    ]

    ADM_DOMAIN_WHOIS = [
        {"desc": "MD5(DOMAIN)", "ename": "MD_ID", "name": "md5主键"},
        {
            "desc": "域名（二级域名，ipv4、ipv6保留原格式，部分二级域名会带有国家后缀，也认定为二级域名）\n例：\nbaidu.com\nbaidu.com.cn\n12.12.12.12",
            "ename": "DOMAIN",
            "name": "域名",
        },
        {"desc": "注册域名ID", "ename": "REGISTRY_DOMAIN_ID", "name": "注册域名ID"},
        {
            "desc": "注册商WHOIS服务器",
            "ename": "REGISTRAR_WHOIS_SERVER",
            "name": "注册商WHOIS服务器",
        },
        {"desc": "注册商网址", "ename": "REGISTRAR_URL", "name": "注册商网址"},
        {"desc": "更新时间", "ename": "UPDATED_TIME", "name": "更新时间"},
        {"desc": "建立时间", "ename": "CREATION_TIME", "name": "建立时间"},
        {"desc": "到期时间", "ename": "EXPIRATION_TIME", "name": "到期时间"},
        {"desc": "注册商", "ename": "REGISTRAR", "name": "注册商"},
        {
            "desc": "注册机构IANA ID",
            "ename": "REGISTRAR_IANA_ID",
            "name": "注册机构IANA ID",
        },
        {
            "desc": "注册服务商联系电子邮件",
            "ename": "REGISTRAR_CONTACT_EMAIL",
            "name": "注册服务商联系电子邮件",
        },
        {
            "desc": "注册服务商联系电话",
            "ename": "REGISTRAR_CONTACT_PHONE",
            "name": "注册服务商联系电话",
        },
        {
            "desc": "注册单位名称",
            "ename": "REGISTRANT_ORGANIZATION",
            "name": "注册单位名称",
        },
        {"desc": "注册省", "ename": "REGISTRANT_PROVINCE", "name": "注册省"},
        {"desc": "注册国家", "ename": "REGISTRANT_COUNTRY", "name": "注册国家"},
        {
            "desc": "注册人电子邮件",
            "ename": "REGISTRANT_EMAIL",
            "name": "注册人电子邮件",
        },
        {
            "desc": "管理员单位名称",
            "ename": "ADMIN_ORGANIZATION",
            "name": "管理员单位名称",
        },
        {"desc": "管理员省", "ename": "ADMIN_PROVINCE", "name": "管理员省"},
        {"desc": "管理员国家", "ename": "ADMIN_COUNTRY", "name": "管理员国家"},
        {
            "desc": "管理员联系电子邮件",
            "ename": "ADMIN_EMAIL",
            "name": "管理员联系电子邮件",
        },
        {"desc": "技术单位名称", "ename": "TECH_ORGANIZATION", "name": "技术单位名称"},
        {"desc": "技术单位省", "ename": "TECH_PROVINCE", "name": "技术单位省"},
        {"desc": "技术单位国家", "ename": "TECH_COUNTRY", "name": "技术单位国家"},
        {
            "desc": "技术单位联系电子邮件",
            "ename": "TECH_EMAIL",
            "name": "技术单位联系电子邮件",
        },
        {"desc": "入库时间", "ename": "CREATE_TIME", "name": "入库时间"},
        {"desc": "最后更新时间", "ename": "LAST_TIME", "name": "最后更新时间"},
        {"desc": "注册人", "ename": "REGISTRANT", "name": "注册人"},
    ]


if __name__ == "__main__":
    print(MockTableMetadata().__dir__())
    print(MockTableMetadata().__getattribute__("ADM_DOMAIN_WHOIS"))
