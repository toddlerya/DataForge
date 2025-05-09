#!/usr/bin/env python
# coding: utf-8
# @File    :   gen_faker_data_agent.py
# @Time    :   2025/05/08 16:33:12
# @Author  :   toddlerya
# @Desc    :   None

from typing import Union

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from loguru import logger
from pydantic import ConfigDict, create_model

from agent.llm import chat_llm
from agent.prompt import prompt_gen_faker_data
from agent.state import (
    DataForgeState,
    TableMetadataSchema,
    TableRawFieldSchema,
    UserIntentSchema,
)
from agent.utils import create_model_from_dict


def gen_faker_data_agent(state: DataForgeState) -> dict:
    user_intent = state.get("user_intent", UserIntentSchema())
    table_en_names = user_intent.table_en_names
    table_conditions = user_intent.table_conditions
    table_data_count = user_intent.table_data_count
    table_metadata_array = state.get("table_metadata_array", [])

    logger.debug(f"table_en_names: {table_en_names}")
    logger.debug(f"table_conditions: {table_conditions}")
    logger.debug(f"table_data_count: {table_data_count}")
    logger.debug(
        f"output_fields: {[ele.output_fields for ele in table_metadata_array]}"
    )

    # 生成测试数据
    output_structure = list()
    for table_metadata in table_metadata_array:
        ouput_schema = create_model_from_dict(
            data=table_metadata.output_fields, model_name=table_metadata.table_en_name
        )
        output_structure.append(ouput_schema)
    union_model = create_model(
        "output_structure",
        __config__=ConfigDict(arbitrary_types_allowed=True),
        final_output=(Union[output_structure]),
    )
    structured_llm = chat_llm.with_structured_output(union_model)
    system_message = prompt_gen_faker_data.format(
        table_en_name_array=table_en_names,
        table_field_info_array=[ele.model_dump() for ele in table_metadata_array],
        table_conditions_array=table_conditions,
        table_data_count_array=table_data_count,
    )
    # logger.debug(f"system_message: {system_message}")
    fake_data = structured_llm.invoke(
        [
            system_message,
            "请根据表字段信息生成测试数据",
        ]
    )
    logger.debug(f"fake_data:  {fake_data.final_output}")
    return {"fake_data": fake_data.final_output}


gen_faker_data_builder = StateGraph(DataForgeState)
gen_faker_data_builder.add_node("gen_faker_data_agent", gen_faker_data_agent)

gen_faker_data_builder.add_edge(START, "gen_faker_data_agent")
gen_faker_data_builder.add_edge("gen_faker_data_agent", END)

memory = MemorySaver()
gen_faker_data_graph = gen_faker_data_builder.compile(checkpointer=memory)


if __name__ == "__main__":
    print(gen_faker_data_graph.get_graph(xray=True).draw_mermaid())
    thread = {"configurable": {"thread_id": "4895b601-c056-4af3-a1f3-6dfa03837744"}}
    event = gen_faker_data_graph.invoke(
        {
            "user_input": "数据库表名称:\nadm_test\nods_test\n期望表约束条件:\nadm_test: from_city_code != to_city_code and datetime = 20250508 and ods_test.phone = adm_test.phone\nods_test: idcard is not null and phone is not null\n期望生成数据条数:\nadm_test: 10\nods_test: 20",
            "user_intent": UserIntentSchema(
                table_en_names=["ADM_DOMAIN_WHOIS", "ODS_POL_EIV_DOMAIN_WHOIS"],
                table_conditions={
                    "ADM_DOMAIN_WHOIS": "DOMAIN IS NOT NULL",
                    "ODS_POL_EIV_DOMAIN_WHOIS": "DOMAIN IS NOT NULL",
                },
                table_data_count={
                    "ADM_DOMAIN_WHOIS": 2,
                    "ODS_POL_EIV_DOMAIN_WHOIS": 3,
                },
            ),
            "table_metadata_array": [
                TableMetadataSchema(
                    table_en_name="ADM_DOMAIN_WHOIS",
                    table_cn_name="",
                    raw_fields_info=[
                        TableRawFieldSchema(
                            cn_name="md5主键",
                            en_name="MD_ID",
                            desc="MD5(DOMAIN)",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="域名",
                            en_name="DOMAIN",
                            desc="域名（二级域名，ipv4、ipv6保留原格式，部分二级域名会带有国家后缀，也认定为二级域名）\n例：\nbaidu.com\nbaidu.com.cn\n12.12.12.12",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册域名ID",
                            en_name="REGISTRY_DOMAIN_ID",
                            desc="注册域名ID",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册商WHOIS服务器",
                            en_name="REGISTRAR_WHOIS_SERVER",
                            desc="注册商WHOIS服务器",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册商网址",
                            en_name="REGISTRAR_URL",
                            desc="注册商网址",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="更新时间",
                            en_name="UPDATED_TIME",
                            desc="更新时间",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="建立时间",
                            en_name="CREATION_TIME",
                            desc="建立时间",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="到期时间",
                            en_name="EXPIRATION_TIME",
                            desc="到期时间",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册商",
                            en_name="REGISTRAR",
                            desc="注册商",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册机构IANA ID",
                            en_name="REGISTRAR_IANA_ID",
                            desc="注册机构IANA ID",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商联系电子邮件",
                            en_name="REGISTRAR_CONTACT_EMAIL",
                            desc="注册服务商联系电子邮件",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商联系电话",
                            en_name="REGISTRAR_CONTACT_PHONE",
                            desc="注册服务商联系电话",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册单位名称",
                            en_name="REGISTRANT_ORGANIZATION",
                            desc="注册单位名称",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册省",
                            en_name="REGISTRANT_PROVINCE",
                            desc="注册省",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册国家",
                            en_name="REGISTRANT_COUNTRY",
                            desc="注册国家",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册人电子邮件",
                            en_name="REGISTRANT_EMAIL",
                            desc="注册人电子邮件",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员单位名称",
                            en_name="ADMIN_ORGANIZATION",
                            desc="管理员单位名称",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员省",
                            en_name="ADMIN_PROVINCE",
                            desc="管理员省",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员国家",
                            en_name="ADMIN_COUNTRY",
                            desc="管理员国家",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员联系电子邮件",
                            en_name="ADMIN_EMAIL",
                            desc="管理员联系电子邮件",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位名称",
                            en_name="TECH_ORGANIZATION",
                            desc="技术单位名称",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位省",
                            en_name="TECH_PROVINCE",
                            desc="技术单位省",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位国家",
                            en_name="TECH_COUNTRY",
                            desc="技术单位国家",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位联系电子邮件",
                            en_name="TECH_EMAIL",
                            desc="技术单位联系电子邮件",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="入库时间",
                            en_name="CREATE_TIME",
                            desc="入库时间",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="最后更新时间",
                            en_name="LAST_TIME",
                            desc="最后更新时间",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册人",
                            en_name="REGISTRANT",
                            desc="注册人",
                            field_type="",
                        ),
                    ],
                    output_fields={
                        "MD_ID": "",
                        "DOMAIN": "",
                        "REGISTRY_DOMAIN_ID": "",
                        "REGISTRAR_WHOIS_SERVER": "",
                        "REGISTRAR_URL": "",
                        "UPDATED_TIME": "",
                        "CREATION_TIME": "",
                        "EXPIRATION_TIME": "",
                        "REGISTRAR": "",
                        "REGISTRAR_IANA_ID": "",
                        "REGISTRAR_CONTACT_EMAIL": "",
                        "REGISTRAR_CONTACT_PHONE": "",
                        "REGISTRANT_ORGANIZATION": "",
                        "REGISTRANT_PROVINCE": "",
                        "REGISTRANT_COUNTRY": "",
                        "REGISTRANT_EMAIL": "",
                        "ADMIN_ORGANIZATION": "",
                        "ADMIN_PROVINCE": "",
                        "ADMIN_COUNTRY": "",
                        "ADMIN_EMAIL": "",
                        "TECH_ORGANIZATION": "",
                        "TECH_PROVINCE": "",
                        "TECH_COUNTRY": "",
                        "TECH_EMAIL": "",
                        "CREATE_TIME": "",
                        "LAST_TIME": "",
                        "REGISTRANT": "",
                    },
                    map_tool_fields_info=[],
                    mapping_confirmed=False,
                    map_count=-1,
                    no_map_count=-1,
                    human_update_count=-1,
                ),
                TableMetadataSchema(
                    table_en_name="ODS_POL_EIV_DOMAIN_WHOIS",
                    table_cn_name="",
                    raw_fields_info=[
                        TableRawFieldSchema(
                            cn_name="系统数据唯一标识ID",
                            en_name="MD_ID",
                            desc="md5(SEARCH_URL,URL_DOMAIN,URL)",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据采集来源系统",
                            en_name="COL_SOUR_SYS",
                            desc="参考数据来源系统字典，现场对标没有可以补充",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据采集来源系统备注",
                            en_name="COL_SOUR_SYS_REMARK",
                            desc="参考数据来源系统字典对应的名称",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据采集来源部门",
                            en_name="COL_SOUR_DEP",
                            desc="参考数据来源部门字典，现场对标没有可以补充",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据采集来源地",
                            en_name="COL_SOUR_PLAC",
                            desc="填入数据来源的六位行政区划代码",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="采集时间",
                            en_name="COLL_TIME",
                            desc="指数据接入到大数据平台的时间",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据采集来源表名",
                            en_name="COL_SOUR_TABLE",
                            desc="从原始数据里面获取，填入STG表的原始表名",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="原始系统接入主键",
                            en_name="ORIG_DATA_ID",
                            desc="从原始数据里面获取，填入STG表的主键值",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="更新时间",
                            en_name="UPD_TIME",
                            desc="从原始数据里面获取，这里指业务的更新时间，选取数据的业务性质的更新时间，默认更新时间不可大于当前时间，对于无业务更新时间统一约定为-1",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="信息删除_判断标识",
                            en_name="INFO_DELE_JUDGE_FLAG",
                            desc="从原始数据里面获取，指整条数据是否有效，从原始数据判断数据已经删除填写“1”，否则填“0”",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据敏感级别编码",
                            en_name="DATA_SENS_LEVE_NO",
                            desc="数据敏感级别编码",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="数据库回溯标识符",
                            en_name="DATBAS_RECSOU_TAG",
                            desc="数据库回溯标识符",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="业务标签标识",
                            en_name="BUS_TAG_FLAG",
                            desc="业务标签标识",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="行为标签标识",
                            en_name="BEH_TAG_FLAG",
                            desc="行为标签标识",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="域名",
                            en_name="DOMAIN",
                            desc="字段说明：域名（二级域名，部分二级域名会带有国家后缀，也认定为二级域名）\n样例数据：www.qdsrmyy.com",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="域名ID",
                            en_name="REGISTRY_DOMAIN_ID",
                            desc="字段说明：域名的唯一标识，是注册服务商分配的一个ID\n样例数据：113108974_domain_com-vrsn",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商",
                            en_name="REGISTRAR",
                            desc="样例数据：Xin Net Technology Corporation",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商IANA ID",
                            en_name="REGISTRAR_IANA_ID",
                            desc="字段说明：注册服务商互联网数字分配机构ID\n样例数据：120",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商WHOIS服务器",
                            en_name="REGISTRAR_WHOIS_SERVER",
                            desc="字段说明：注册服务商WHOIS服务器(whois 用来查询域名的ip以及所有者等信息的传输协议)\n样例数据：whois.paycenter.com.cn",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商网址",
                            en_name="REGISTRAR_URL",
                            desc="样例数据：http://www.xinnet.com",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商电子邮件",
                            en_name="REGISTRAR_CONTACT_EMAIL",
                            desc="样例数据：supervision@xinnet.com",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册服务商联系电话",
                            en_name="REGISTRAR_CONTACT_PHONE",
                            desc="样例数据：86.4008182233",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="域名建立时间",
                            en_name="CREATION_TIME",
                            desc="字段说明：域名的建立时间\n样例数据：1078214400",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="域名更新时间",
                            en_name="UPDATED_TIME",
                            desc="字段说明：域名的更新时间\n样例数据：1612312997",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="域名到期时间",
                            en_name="EXPIRATION_TIME",
                            desc="字段说明：域名的到期时间\n样例数据：1646284971",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册单位名称",
                            en_name="REGISTRANT_ORGANIZATION",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册省名称",
                            en_name="REGISTRANT_PROVINCE",
                            desc="样例数据：JS",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册国家名称",
                            en_name="REGISTRANT_COUNTRY",
                            desc="样例数据：CN",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="注册电子邮件",
                            en_name="REGISTRANT_EMAIL",
                            desc="样例数据：supervision@xinnet.com",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员单位名称",
                            en_name="ADMIN_ORGANIZATION",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员省名称",
                            en_name="ADMIN_PROVINCE",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员国家名称",
                            en_name="ADMIN_COUNTRY",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="管理员电子邮件",
                            en_name="ADMIN_EMAIL",
                            desc="样例数据：supervision@xinnet.com",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位名称",
                            en_name="TECH_ORGANIZATION",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位省名称",
                            en_name="TECH_PROVINCE",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位国家名称",
                            en_name="TECH_COUNTRY",
                            desc="",
                            field_type="",
                        ),
                        TableRawFieldSchema(
                            cn_name="技术单位电子邮件",
                            en_name="TECH_EMAIL",
                            desc="样例数据：supervision@xinnet.com",
                            field_type="",
                        ),
                    ],
                    output_fields={
                        "MD_ID": "",
                        "COL_SOUR_SYS": "",
                        "COL_SOUR_SYS_REMARK": "",
                        "COL_SOUR_DEP": "",
                        "COL_SOUR_PLAC": "",
                        "COLL_TIME": "",
                        "COL_SOUR_TABLE": "",
                        "ORIG_DATA_ID": "",
                        "UPD_TIME": "",
                        "INFO_DELE_JUDGE_FLAG": "",
                        "DATA_SENS_LEVE_NO": "",
                        "DATBAS_RECSOU_TAG": "",
                        "BUS_TAG_FLAG": "",
                        "BEH_TAG_FLAG": "",
                        "DOMAIN": "",
                        "REGISTRY_DOMAIN_ID": "",
                        "REGISTRAR": "",
                        "REGISTRAR_IANA_ID": "",
                        "REGISTRAR_WHOIS_SERVER": "",
                        "REGISTRAR_URL": "",
                        "REGISTRAR_CONTACT_EMAIL": "",
                        "REGISTRAR_CONTACT_PHONE": "",
                        "CREATION_TIME": "",
                        "UPDATED_TIME": "",
                        "EXPIRATION_TIME": "",
                        "REGISTRANT_ORGANIZATION": "",
                        "REGISTRANT_PROVINCE": "",
                        "REGISTRANT_COUNTRY": "",
                        "REGISTRANT_EMAIL": "",
                        "ADMIN_ORGANIZATION": "",
                        "ADMIN_PROVINCE": "",
                        "ADMIN_COUNTRY": "",
                        "ADMIN_EMAIL": "",
                        "TECH_ORGANIZATION": "",
                        "TECH_PROVINCE": "",
                        "TECH_COUNTRY": "",
                        "TECH_EMAIL": "",
                    },
                    map_tool_fields_info=[],
                    mapping_confirmed=False,
                    map_count=-1,
                    no_map_count=-1,
                    human_update_count=-1,
                ),
            ],
        },
        thread,
        stream_mode="values",
    )
