http://172.17.55.71:13579/s/49819cae-15a1-4e72-9663-607e707c810d

<details type="reasoning" done="true" duration="78">
<summary>Thought for 78 seconds</summary>
> 嗯，我现在需要生成ODS_BEIAN_MAINBODY_INFO表的仿真测试数据。首先，我得仔细阅读用户提供的任务要求，确保我理解所有的步骤和细节。
> 
> 任务要求包括根据表结构信息和来源样例数据，进行字段的映射关联。如果表结构中的字段有字典码信息，那么需要参考对应的字典码id值。同时，生成的数据要尽可能真实，不知道的数据含义不要随便生成，还要确保满足表的SQL条件。
> 
> 首先，我需要分析表结构信息，确定每个字段的ename和中文含义，以及是否有对应的字典码。例如，BUSINESSTYPE字段对应的是“数据操作类型”字典，所以它的值应该是1、2或3。同样，RPBCFTTYPE对应“常用证件代码”，所以值应该是111到121中的一个。STATUS对应“审核状态类型”，所以是1、2或3。UNITPTY对应“主办单位性质主分类”，所以是1或2。
> 
> 接下来，我要查看来源样例数据，看看每个字段的示例值是什么样的。比如ID的示例是UUID格式的字符串，BUSINESSTYPE的示例都是1，CREATETIME是时间戳，归属地的字段是行政区划代码，证件号码是身份证号，手机号是11位数字，邮箱是常见的格式，地址是具体的街道信息，状态是数字等。
> 
> 然后，我需要根据来源样例数据生成仿真数据。每个字段的值应该尽可能符合实际情况。例如，身份证号码要符合中国的身份证格式，手机号要正确，地址要具体，证件类型要合理。
> 
> 同时，我要确保生成的数据满足SQL条件。SQL条件中提到，id、BUSINESSTYPE、RPBCFTNUM、RPBCFTTYPE、RPBMOBILE、RPBNM、STATUS、UNITPTY这些字段不能为空。因此，仿真数据中这些字段必须有值，不能留空。
> 
> 在生成数据时，我还需要注意字典码的对应关系。例如，RPBCFTTYPE的值必须是常用证件代码中的id，如111代表居民身份证。UNITPTY的值必须是主办单位性质主分类中的id，1代表个人，2代表单位。
> 
> 另外，来源样例数据中有三个记录，所以我需要生成三个仿真数据条目。每个条目中的字段值要与来源样例数据中的结构一致，同时确保字段数量和名称与表结构一致。
> 
> 在处理过程中，我可能会遇到一些不确定的地方。例如，RPBMAIL和RPBMOBILE是否需要特定的格式，或者UITCFTTYPE是否需要特定的值。根据来源样例数据，RPBMAIL是常见的邮箱格式，RPBMOBILE是11位数字， UITCFTTYPE的示例是“tyshxydmz”，但根据字典码，它应该是数字，所以可能需要修正。
> 
> 我还注意到，来源样例数据中有些字段的值为空，比如IDECARDGROUPID和UITADRSTR等。根据任务要求，不知道的数据含义不要随便生成，所以这些字段可以保留为空。
> 
> 最后，我会检查生成的JSON数据，确保每个字段的数量和名称与表结构一致，且满足SQL条件中的非空约束。同时，确保所有字典码字段的值正确无误。
> 
> 总结一下，我的步骤是：
> 1. 分析表结构和字典码信息，确定每个字段的取值范围和映射关系。
> 2. 查看来源样例数据，了解每个字段的示例值和格式。
> 3. 生成仿真数据，确保数据真实且符合格式。
> 4. 检查数据是否满足SQL条件，特别是非空字段。
> 5. 输出符合要求的JSON结构，确保字段一致性和数据正确性。
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
    "UITADRPVS": "140000",
    "UITADRCTY": "140400",
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
    "UNITPTY": "2",
    "UNITPTY_SUB": "1",
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
    "UITADRPVS": "",
    "UITADRCTY": "",
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
    "UNITPTY": "1",
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
    "UITADRPVS": "",
    "UITADRCTY": "",
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
    "UNITPTY": "1",
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