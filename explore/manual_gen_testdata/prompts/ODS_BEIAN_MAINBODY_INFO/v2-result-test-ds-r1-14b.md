http://172.17.55.71:13579/s/77cf9c3e-7874-4b01-921f-e1eb2009aa56

<details type="reasoning" done="true" duration="58">
<summary>Thought for 58 seconds</summary>
> 好，我现在需要根据用户的要求，生成ODS_BEIAN_MAINBODY_INFO表的仿真测试数据。首先，我要仔细阅读任务要求，确保理解每一个细节。
> 
> 首先，任务要求根据表结构信息和来源样例数据，进行字段的映射关联。这意味着我需要将表结构中的每个字段（ename）与样例数据中的对应字段进行匹配，确保数据的一致性。
> 
> 接下来，遇到表结构中的“dic”有值时，需要参考对应的字典码信息中的id字段值。例如，业务类型对应的字典码是“数据操作类型”，所以我要从该字典中获取id值，如“1”代表新增，“2”代表修改等。
> 
> 然后，数据要尽可能真实，所以我会参考样例数据中的值，同时确保数据的合理性和真实性。例如，身份证号码应该符合格式，地址信息要符合实际的行政区域划分。
> 
> 同时，用户强调不知道的数据含义不要随便生成，这意味着对于不确定的字段，我应该跳过或者保持为空，避免生成错误数据。
> 
> 另外，必须遵循表的SQL条件，确保生成的数据满足这些条件。SQL条件包括id、BUSINESSTYPE、RPBCFTNUM、RPBCFTTYPE、RPBMOBILE、RPBNM、STATUS、UNITPTY这些字段都不是空值。因此，在生成数据时，这些字段必须有有效的值。
> 
> 接下来，我需要分析表结构信息和字典码信息，确保每个字段的正确映射。例如，BUSINESSTYPE字段在字典码中是“数据操作类型”，对应的id有1、2、3，分别代表新增、修改、撤销。因此，在生成数据时，BUSINESSTYPE字段应取这些值中的一个。
> 
> 对于日期字段，如CREATETIME和UPDATETIME，样例数据中的值是以时间戳形式表示的，例如“1704354911000”。我需要生成类似的值，可能使用当前时间或者随机生成的时间戳。
> 
> 地址相关的字段，如PVS、CTY、CRY，分别代表省、市、县区，这些需要符合实际的行政编码。例如，山西省的省编码是140000，长治市的市编码是140400，潞州区的区编码是140403。
> 
> 证件类型方面，负责人证件类型对应的字典码是“常用证件代码”，因此RPBCFTTYPE字段应取如“111”（居民身份证）等值。同样，主办单位证件类型code对应的字典码是“主办单位证件类型分类”，所以UITCFTTYPE字段应取如“1”（统一社会信用代码证）等值。
> 
> 负责人信息方面，RPBNM是姓名，RPBMOBILE是手机号，RPBCFTNUM是证件号码，这些需要合理组合，例如姓名李维超，手机号15698522821，证件号码140402198711292014。
> 
> 状态字段STATUS对应的字典码是“审核状态类型”，所以应取如“2”（审核中）等值。
> 
> 主办单位性质方面，UNITPTY是主分类，如“dw”代表单位，“gr”代表个人。UNITPTY_SUB是子级分类，如“sydw”代表事业单位。
> 
> 最后，确保生成的数据JSON结构与表结构信息中的ename字段一致，字段数量和名称都必须匹配。
> 
> 综合以上分析，我会按照每个字段的要求，生成相应的仿真数据，确保满足所有条件，并保持数据的真实性和一致性。
</details>
```json
[
    {
        "ID": "01325837e1dd44649172689a91f7e3a4",
        "BUSINESSTYPE": "1",
        "CREATETIME": "1704354911000",
        "PVS": "140000",
        "CTY": "140400",
        "CRY": "140403",
        "IDECARDBACKID": "http://127.0.0.1:9999/index/attach_20241107181019/c58ecd71-96a9-441c-a2d9-3251a96aef1a.jpg",
        "IDECARDFRONTID": "http://127.0.0.1:9999/index/attach_20241107181019/e231c9c7-bc4b-4663-a396-fc535f56c8f8.jpg",
        "IDECARDGROUPID": "",
        "IDECARDVALID": "2099059200000",
        "LGLNM": "郝少峰",
        "MEM": "",
        "OFFTEL": "0355-3559106",
        "RPBADSCRY": "140403",
        "RPBADSCTY": "140400",
        "RPBADSPVS": "140000",
        "RPBADSSTR": "潞州区城北东街67号",
        "RPBCFTID": "",
        "RPBCFTNUM": "140402198711292014",
        "RPBCFTTYPE": "111",
        "RPBMAIL": "2631679238@qq.com",
        "RPBMOBILE": "15698522821",
        "RPBNM": "李维超",
        "STATUS": "2",
        "UITADRUPVS": "140000",
        "UITADRUCTY": "140400",
        "UITADRCRY": "140403",
        "UITADRSTR": "太行东街271号",
        "UITCFTID": "http://127.0.0.1:9999/index/attach_20241107181019/6b1f77e2-293e-4b9e-91ab-d4783330e769.jpg",
        "UITCFTNUM": "121400004062722259",
        "UITCFTTYPE": "1",
        "UITNM": "长治医学院附属和济医院",
        "UITREGADRPVS": "",
        "UITREGADRCTY": "",
        "UITREGADRCRY": "",
        "UITREGADRSTR": "",
        "UNITPTY": "dw",
        "UNITPTY_SUB": "sydw",
        "UPDATETIME": "1704354911000",
        "UPDATEUSER": "",
        "CYBUSRID": "0bb897d51618316093cf9eafa174bd9a",
        "AUDITID": "436daf7e5bdda10a4194fa6e7fb100d9",
        "AUDIT_NAME": "",
        "AUDIT_UNITCODE": "",
        "AUDIT_UNITNAME": "",
        "AUDITTIME": "1705975709000"
    },
    {
        "ID": "0195a22d575c4ca9a232575d8e5d2240",
        "BUSINESSTYPE": "1",
        "CREATETIME": "1701779076000",
        "PVS": "140000",
        "CTY": "140500",
        "CRY": "140581",
        "IDECARDBACKID": "http://127.0.0.1:9999/index/attach_20241107181019/0f536e88-a220-41ce-9123-a60fca32e6ae.jpg",
        "IDECARDFRONTID": "http://127.0.0.1:9999/index/attach_20241107181019/7622a8b4-7a8d-4154-b069-7fb4206910cb.jpg",
        "IDECARDGROUPID": "",
        "IDECARDVALID": "1747238400000",
        "LGLNM": "",
        "MEM": "",
        "OFFTEL": "",
        "RPBADSCRY": "140581",
        "RPBADSCTY": "140500",
        "RPBADSPVS": "140000",
        "RPBADSSTR": "城北社区锦盛苑小区六号楼三单元1501",
        "RPBCFTID": "",
        "RPBCFTNUM": "140581199712018418",
        "RPBCFTTYPE": "111",
        "RPBMAIL": "409126858@qq.com",
        "RPBMOBILE": "18303466786",
        "RPBNM": "琚佳宝",
        "STATUS": "2",
        "UITADRUPVS": "",
        "UITADRUCTY": "",
        "UITADRCRY": "",
        "UITADRSTR": "",
        "UITCFTID": "",
        "UITCFTNUM": "",
        "UITCFTTYPE": "",
        "UITNM": "",
        "UITREGADRPVS": "",
        "UITREGADRCTY": "",
        "UITREGADRCRY": "",
        "UITREGADRSTR": "",
        "UNITPTY": "gr",
        "UNITPTY_SUB": "",
        "UPDATETIME": "1701779076000",
        "UPDATEUSER": "",
        "CYBUSRID": "ae985142ae6cd426bf4dc6d907f9e161",
        "AUDITID": "a883bbca3f8bc8814ff676cb0e91829a",
        "AUDIT_NAME": "",
        "AUDIT_UNITCODE": "",
        "AUDIT_UNITNAME": "",
        "AUDITTIME": "1704333752000"
    },
    {
        "ID": "0306d71f93a6462bbf4de93f55e520ef",
        "BUSINESSTYPE": "1",
        "CREATETIME": "1703344243000",
        "PVS": "140000",
        "CTY": "140400",
        "CRY": "140425",
        "IDECARDBACKID": "http://127.0.0.1:9999/index/attach_20241107181019/f6226ecc-0051-4029-84ca-d89680191db1.jpg",
        "IDECARDFRONTID": "http://127.0.0.1:9999/index/attach_20241107181019/3cbe916d-06d3-4046-8982-b747d3f45ca3.jpg",
        "IDECARDGROUPID": "",
        "IDECARDVALID": "1688054400000",
        "LGLNM": "",
        "MEM": "",
        "OFFTEL": "",
        "RPBADSCRY": "140425",
        "RPBADSCTY": "140400",
        "RPBADSPVS": "140000",
        "RPBADSSTR": "北社乡广武村351号",
        "RPBCFTID": "",
        "RPBCFTNUM": "140425200206268034",
        "RPBCFTTYPE": "111",
        "RPBMAIL": "houcy@geniecc.com",
        "RPBMOBILE": "18838113214",
        "RPBNM": "候超越",
        "STATUS": "2",
        "UITADRUPVS": "",
        "UITADRUCTY": "",
        "UITADRCRY": "",
        "UITADRSTR": "",
        "UITCFTID": "",
        "UITCFTNUM": "",
        "UITCFTTYPE": "",
        "UITNM": "",
        "UITREGADRPVS": "",
        "UITREGADRCTY": "",
        "UITREGADRCRY": "",
        "UITREGADRSTR": "",
        "UNITPTY": "gr",
        "UNITPTY_SUB": "",
        "UPDATETIME": "1703344243000",
        "UPDATEUSER": "",
        "CYBUSRID": "27e0ee75d99d62db84cf101a8046756d",
        "AUDITID": "90ed602fc3a239f835738dfeff08c3ab",
        "AUDIT_NAME": "",
        "AUDIT_UNITCODE": "",
        "AUDIT_UNITNAME": "",
        "AUDITTIME": "1705481109000"
    }
]
```