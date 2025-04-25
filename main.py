def main():
    demo_data = {
        "DATA": {
            "ITEM": [
                {
                    "_attributes": {
                        "key": "I010058",
                        "eng": "id",
                        "chn": "ID"
                    }
                },
                {
                    "_attributes": {
                        "key": "I020039",
                        "eng": "businessType",
                        "chn": "业务类型"
                    }
                },
                {
                    "_attributes": {
                        "key": "C110002",
                        "eng": "createtime",
                        "chn": "创建时间"
                    }
                },
                {
                    "_attributes": {
                        "key": "B030820",
                        "eng": "pvs",
                        "chn": "归属地-省"
                    }
                },
                {
                    "_attributes": {
                        "key": "B030822",
                        "eng": "cty",
                        "chn": "归属地-城市"
                    }
                },
                {
                    "_attributes": {
                        "key": "B030821",
                        "eng": "cry",
                        "chn": "归属地-县区"
                    }
                },
                {
                    "_attributes": {
                        "key": "J080002",
                        "eng": "idecardbackid",
                        "chn": "身份证反面图片文件"
                    }
                },
                {
                    "_attributes": {
                        "key": "J080003",
                        "eng": "idecardfrontid",
                        "chn": "身份证正面图片文件"
                    }
                },
                {
                    "_attributes": {
                        "key": "J080001",
                        "eng": "idecardgroupid",
                        "chn": "手持身份证照片文件"
                    }
                },
                {
                    "_attributes": {
                        "key": "H010023",
                        "eng": "idecardvalid",
                        "chn": "身份证有效期"
                    }
                },
                {
                    "_attributes": {
                        "key": "E020001",
                        "eng": "lglnm",
                        "chn": "法定代表姓名"
                    }
                },
                {
                    "_attributes": {
                        "key": "I010009",
                        "eng": "mem",
                        "chn": "备注"
                    }
                },
                {
                    "_attributes": {
                        "key": "E010006",
                        "eng": "offtel",
                        "chn": "办公室电话"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000430",
                        "eng": "rpbadscry",
                        "chn": "负责人常住地址县区"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000429",
                        "eng": "rpbadscty",
                        "chn": "负责人常住地址城市"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000428",
                        "eng": "rpbadspvs",
                        "chn": "负责人常住地址省份"
                    }
                },
                {
                    "_attributes": {
                        "key": "B030011",
                        "eng": "rpbadsstr",
                        "chn": "负责人常住地详细地址"
                    }
                },
                {
                    "_attributes": {
                        "key": "K001760",
                        "eng": "rpbcftid",
                        "chn": "负责人证件id"
                    }
                },
                {
                    "_attributes": {
                        "key": "E020014",
                        "eng": "rpbcftnum",
                        "chn": "负责人证件号码"
                    }
                },
                {
                    "_attributes": {
                        "key": "E020013",
                        "eng": "rpbcfttype",
                        "chn": "负责人证件类型"
                    }
                },
                {
                    "_attributes": {
                        "key": "B040023",
                        "eng": "rpbmail",
                        "chn": "负责人电子邮件"
                    }
                },
                {
                    "_attributes": {
                        "key": "E020015",
                        "eng": "rpbmobile",
                        "chn": "负责人手机号码"
                    }
                },
                {
                    "_attributes": {
                        "key": "E020012",
                        "eng": "rpbnm",
                        "chn": "负责人姓名"
                    }
                },
                {
                    "_attributes": {
                        "key": "C080002",
                        "eng": "status",
                        "chn": "状态"
                    }
                },
                {
                    "_attributes": {
                        "key": "F010035",
                        "eng": "uitadrpvs",
                        "chn": "单位办公地址省"
                    }
                },
                {
                    "_attributes": {
                        "key": "B020031",
                        "eng": "uitadrcty",
                        "chn": "单位办公地址市"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000423",
                        "eng": "uitadrcry",
                        "chn": "单位办公地址县区"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000788",
                        "eng": "uitadrstr",
                        "chn": "单位办公详细地址"
                    }
                },
                {
                    "_attributes": {
                        "key": "H140009",
                        "eng": "uitcftid",
                        "chn": "主办单位有效证件文件"
                    }
                },
                {
                    "_attributes": {
                        "key": "E010011",
                        "eng": "uitcftnum",
                        "chn": "主办单位证件号码"
                    }
                },
                {
                    "_attributes": {
                        "key": "E010023",
                        "eng": "uitcfttype",
                        "chn": "主办单位证件类型code"
                    }
                },
                {
                    "_attributes": {
                        "key": "E010002",
                        "eng": "uitnm",
                        "chn": "主办单位名称"
                    }
                },
                {
                    "_attributes": {
                        "key": "H140011",
                        "eng": "uitregadrpvs",
                        "chn": "单位注册地址省"
                    }
                },
                {
                    "_attributes": {
                        "key": "H140021",
                        "eng": "uitregadrcty",
                        "chn": "单位注册地址市"
                    }
                },
                {
                    "_attributes": {
                        "key": "F010032",
                        "eng": "uitregadrcry",
                        "chn": "单位注册地址区县"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000787",
                        "eng": "uitregadrstr",
                        "chn": "单位注册详细地址"
                    }
                },
                {
                    "_attributes": {
                        "key": "H220036",
                        "eng": "unitpty",
                        "chn": "主办单位性质"
                    }
                },
                {
                    "_attributes": {
                        "key": "K000331",
                        "eng": "unitpty_sub",
                        "chn": " 主办单位性质-子级   "
                    }
                },
                {
                    "_attributes": {
                        "key": "B050013",
                        "eng": "updatetime",
                        "chn": "最后更新时间"
                    }
                },
                {
                    "_attributes": {
                        "key": "I010004",
                        "eng": "updateuser",
                        "chn": "更新人"
                    }
                },
                {
                    "_attributes": {
                        "key": "I010004",
                        "eng": "cybusrid",
                        "chn": "创建人"
                    }
                },
                {
                    "_attributes": {
                        "key": "I010071",
                        "eng": "auditid",
                        "chn": "备案审批人id"
                    }
                },
                {
                    "_attributes": {
                        "key": "E020012",
                        "eng": "audit_name",
                        "chn": "备案审批人姓名"
                    }
                },
                {
                    "_attributes": {
                        "key": "B030002",
                        "eng": "audit_unitcode",
                        "chn": "备案审批人单位代码"
                    }
                },
                {
                    "_attributes": {
                        "key": "B030003",
                        "eng": "audit_unitname",
                        "chn": "备案审批人单位名称"
                    }
                },
                {
                    "_attributes": {
                        "key": "I010066",
                        "eng": "audittime",
                        "chn": "审核时间"
                    }
                }
            ]
        }
    }

    fake_quanwen_url_prefix = "http://127.0.0.1:9999/index/"
    sample_bcp = "0f6e04009ed2402282f92311666972d9	1	1705742954000	140000	140100	140108	attach_20241107181019/0812d0a6-4ec5-4aff-bcff-743088e005cc.png	attach_20241107181019/851acf95-00fb-48b2-9fa9-f44d1f13eb12.png		2117203200000	赵秋锁			140107	140100	140000	解放北路富力华庭A区		130182198606011915	111		17535122666	王维昭	2	140000	140100	140108	太原市尖草坪区龙城花园小区I幢1单元1003室	attach_20241107181019/d261374f-66f9-453b-b58c-50fee732189d.jpg	91140108MA0L2R9B8M	yyzzzs	山西晋德管业有限公司					dw	qydw	1705742954000		458d54185c3de40db9c63961ad26d48f	edbd3d1df77e15dc4b9b1908cf016512				1706499761000"
    sample_data_slice = sample_bcp.split("\t")
    struct_data = []
    for index, item in enumerate(demo_data["DATA"]["ITEM"]):
        sample_value = sample_data_slice[index]
        if sample_value.startswith("attach"):
            sample_value = fake_quanwen_url_prefix + sample_value
        attr = item["_attributes"]
        print(attr, sample_value)
        struct_data.append({
            "ename": attr.get("eng"),
            "cname": attr.get("chn"),
            "sample": sample_value
        })

    print(struct_data)


if __name__ == "__main__":
    main()
