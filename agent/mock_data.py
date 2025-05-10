# coding: utf-8
# @Time:     2025/5/7 16:03
# @Author:   toddlerya
# @Filen_name: mock_data.py
# @Project:  DataForge


class MockTableMetadata:
    ODS_TC_DOMAIN_WHOIS = [
        {
            "desc": "md5(SEARCH_URL,URL_DOMAIN,URL)",
            "en_name": "MD_ID",
            "cn_name": "系统数据唯一标识ID",
        },
        {
            "desc": "从原始数据里面获取，这里指业务的更新时间，选取数据的业务性质的更新时间，默认更新时间不可大于当前时间，对于无业务更新时间统一约定为-1",
            "en_name": "UPD_TIME",
            "cn_name": "更新时间",
        },
        {
            "desc": "字段说明：域名（二级域名，部分二级域名会带有国家后缀，也认定为二级域名）\n样例数据：www.qdsrmyy.com",
            "en_name": "DOMAIN",
            "cn_name": "域名",
        },
        {
            "desc": "字段说明：域名的唯一标识，是注册服务商分配的一个ID\n样例数据：113108974_domain_com-vrsn",
            "en_name": "REGISTRY_DOMAIN_ID",
            "cn_name": "域名ID",
        },
        {
            "desc": "样例数据：Xin Net Technology Corporation",
            "en_name": "REGISTRAR",
            "cn_name": "注册服务商",
        },
        {
            "desc": "字段说明：注册服务商互联网数字分配机构ID\n样例数据：120",
            "en_name": "REGISTRAR_IANA_ID",
            "cn_name": "注册服务商IANA ID",
        },
        {
            "desc": "字段说明：注册服务商WHOIS服务器(whois 用来查询域名的ip以及所有者等信息的传输协议)\n样例数据：whois.paycenter.com.cn",
            "en_name": "REGISTRAR_WHOIS_SERVER",
            "cn_name": "注册服务商WHOIS服务器",
        },
        {
            "desc": "样例数据：http://www.xinnet.com",
            "en_name": "REGISTRAR_URL",
            "cn_name": "注册服务商网址",
        },
        {
            "desc": "样例数据：supervision@xinnet.com",
            "en_name": "REGISTRAR_CONTACT_EMAIL",
            "cn_name": "注册服务商电子邮件",
        },
        {
            "desc": "样例数据：86.4008182233",
            "en_name": "REGISTRAR_CONTACT_PHONE",
            "cn_name": "注册服务商联系电话",
        },
        {
            "desc": "字段说明：域名的建立时间\n样例数据：1078214400",
            "en_name": "CREATION_TIME",
            "cn_name": "域名建立时间",
        },
        {
            "desc": "样例数据：JS",
            "en_name": "REGISTRANT_PROVINCE",
            "cn_name": "注册省名称",
        },
        {
            "desc": "样例数据：CN",
            "en_name": "REGISTRANT_COUNTRY",
            "cn_name": "注册国家名称",
        },
        {
            "desc": "样例数据：supervision@xinnet.com",
            "en_name": "REGISTRANT_EMAIL",
            "cn_name": "注册电子邮件",
        },
        {
            "desc": "样例数据：supervision@xinnet.com",
            "en_name": "ADMIN_EMAIL",
            "cn_name": "管理员电子邮件",
        },
        {
            "desc": "样例数据：supervision@xinnet.com",
            "en_name": "TECH_EMAIL",
            "cn_name": "技术单位电子邮件",
        },
    ]

    ADM_DOMAIN_WHOIS = [
        {"desc": "MD5(DOMAIN)", "en_name": "MD_ID", "cn_name": "md5主键"},
        {
            "desc": "域名（二级域名，ipv4、ipv6保留原格式，部分二级域名会带有国家后缀，也认定为二级域名）\n例：\nbaidu.com\nbaidu.com.cn\n12.12.12.12",
            "en_name": "DOMAIN",
            "cn_name": "域名",
        },
        {
            "desc": "注册域名ID",
            "en_name": "REGISTRY_DOMAIN_ID",
            "cn_name": "注册域名ID",
        },
        {
            "desc": "注册商WHOIS服务器",
            "en_name": "REGISTRAR_WHOIS_SERVER",
            "cn_name": "注册商WHOIS服务器",
        },
        {"desc": "注册商网址", "en_name": "REGISTRAR_URL", "cn_name": "注册商网址"},
        {"desc": "建立时间", "en_name": "CREATION_TIME", "cn_name": "建立时间"},
        {"desc": "注册商", "en_name": "REGISTRAR", "cn_name": "注册商"},
        {
            "desc": "注册机构IANA ID",
            "en_name": "REGISTRAR_IANA_ID",
            "cn_name": "注册机构IANA ID",
        },
        {
            "desc": "注册服务商联系电子邮件",
            "en_name": "REGISTRAR_CONTACT_EMAIL",
            "cn_name": "注册服务商联系电子邮件",
        },
        {
            "desc": "注册服务商联系电话",
            "en_name": "REGISTRAR_CONTACT_PHONE",
            "cn_name": "注册服务商联系电话",
        },
        {
            "desc": "注册单位名称",
            "en_name": "REGISTRANT_ORGANIZATION",
            "cn_name": "注册单位名称",
        },
        {"desc": "注册省", "en_name": "REGISTRANT_PROVINCE", "cn_name": "注册省"},
        {"desc": "注册国家", "en_name": "REGISTRANT_COUNTRY", "cn_name": "注册国家"},
        {
            "desc": "注册人电子邮件",
            "en_name": "REGISTRANT_EMAIL",
            "cn_name": "注册人电子邮件",
        },
        {"desc": "管理员省", "en_name": "ADMIN_PROVINCE", "cn_name": "管理员省"},
        {"desc": "管理员国家", "en_name": "ADMIN_COUNTRY", "cn_name": "管理员国家"},
        {
            "desc": "管理员联系电子邮件",
            "en_name": "ADMIN_EMAIL",
            "cn_name": "管理员联系电子邮件",
        },
        {"desc": "最后更新时间", "en_name": "LAST_TIME", "cn_name": "最后更新时间"},
        {"desc": "注册人", "en_name": "REGISTRANT", "cn_name": "注册人"},
    ]


if __name__ == "__main__":
    print(MockTableMetadata().__dir__())
    print(MockTableMetadata().__getattribute__("ADM_DOMAIN_WHOIS"))
