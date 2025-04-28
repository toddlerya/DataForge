http://172.17.55.71:13579/s/e85b0072-60b7-4943-9f08-7c482712049c

<details type="reasoning" done="true" duration="69">
<summary>Thought for 69 seconds</summary>
> 嗯，我现在需要生成ODS_BEIAN_MAINBODY_INFO表的仿真测试数据。首先，我得仔细阅读任务要求，确保我理解每一个步骤。任务要求根据表结构信息和来源样例数据，进行字段的映射关联，同时处理字典码信息，确保数据尽可能真实，不随便生成不知道的数据，并且满足SQL条件。
> 
> 首先，我应该分析表结构信息。表结构中有多个字段，每个字段都有中文名称、英文名称和描述，以及是否有字典码。来源样例数据提供了每个字段的示例值，这对我生成仿真数据很有帮助。
> 
> 接下来，我要处理字典码信息。比如，数据操作类型有三个选项：新增、修改、撤销，分别对应id 1、2、3。常用证件代码有多种，比如居民身份证是111，临时居民身份证是112等等。审核状态类型有草稿、审核中、审核通过，分别对应id 1、2、3。主办单位证件类型分类有统一社会信用代码证、营业执照证书等，id分别是1、2、3、9。主办单位性质主分类有个人和单位，id分别是1、2。网站主办单位性质代码有多个，比如国防机构是1，外国在华文化中心是10，等等。
> 
> 来源样例数据中的每个字段都有多个示例值，这可以帮助我生成仿真数据。例如，id字段有三个示例，都是字符串类型，看起来像是UUID。业务类型字段都是“1”，可能对应新增。创建时间是Unix时间戳，单位办公地址省、城市、县区都是14开头的编码，可能代表山西省。
> 
> 接下来，我需要根据这些信息生成仿真数据。每个字段的值要尽可能真实，同时满足SQL条件：id、BUSINESSTYPE、RPBCFTNUM、RPBCFTTYPE、RPBMOBILE、RPBNM、STATUS、UNITPTY都不能为null。
> 
> 首先，ID字段应该生成类似来源样例的UUID，确保不重复。业务类型根据字典码，选择1、2、3中的一个，来源样例都是1，所以我可以继续使用1。
> 
> 创建时间应该是当前时间或者过去的时间，以Unix时间戳表示。归属地的省、市、县区需要使用正确的编码，比如140000代表山西省，140400代表长治市，140403代表潞州区。
> 
> 身份证相关字段，如反面、正面图片文件名，可以使用示例中的URL结构，但可能需要生成不同的文件名。手持身份证照片文件名在来源样例中为空，所以仿真数据中也可以留空。
> 
> 负责人信息部分，证件类型需要从常用证件代码中选择，比如111代表居民身份证。证件号码应该符合身份证格式，如140402198711292014。负责人姓名可以使用常见的中文名字，如李维超、琚佳宝等。
> 
> 状态字段根据审核状态类型，选择2（审核中）。单位办公地址部分，如果示例中为空，可以留空，或者根据需要补充。主办单位证件类型code需要从主办单位证件类型分类中选择，如1代表统一社会信用代码证。
> 
> 创建人、更新人、备案审批人id可以从来源样例中获取，或者生成类似的UUID。审核时间需要与创建时间相近，确保时间顺序合理。
> 
> 在生成数据时，我需要确保每个字段都有合理的值，并且满足SQL条件。例如，BUSINESSTYPE不能为null，所以每个记录都需要有业务类型。RPBCFTNUM和RPBCFTTYPE也不能为null，所以负责人证件号码和类型必须填写。
> 
> 最后，生成的数据应该是一个列表，每个元素是一个字典，键为字段的ename，值为对应的仿真数据。数据结构要正确，确保JSON格式无误。
> 
> 总结一下，我的步骤是：
> 1. 分析表结构和字典码信息，确定每个字段的可能值。
> 2. 根据来源样例数据，生成仿真数据，确保字段值合理且符合要求。
> 3. 组织数据，生成符合要求的JSON结构，确保每个字段都有正确的值，并满足SQL条件。
</details>
```json
[
  {
    "ID": "e9e3a0e9-2d9e-4f8c-8b35-1a9d80e45d6c",
    "BUSINESSTYPE": "1",
    "CREATETIME": "1705975709000",
    "PVS": "140000",
    "CTY": "140400",
    "CRY": "140403",
    "IDECARDBACKID": "http://127.0.0.1:9999/index/attach_20241107181019/6b1f77e2-293e-4b9e-91ab-d4783330e769.jpg",
    "IDECARDFRONTID": "http://127.0.0.1:9999/index/attach_20241107181019/7622a8b4-7a8d-4154-b069-7fb4206910cb.jpg",
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
    "UITADRSPVS": "140000",
    "UITADRCTY": "140400",
    "UITADRCRY": "140403",
    "UITADRSTR": "太行东街271号",
    "UITCFTID": "http://127.0.0.1:9999/index/attach_20241107181019/6b1f77e2-293e-4b9e-91ab-d4783330e769.jpg",
    "UITCFTNUM": "121400004062722259",
    "UITCFTTYPE": "tyshxydmz",
    "UITNM": "长治医学院附属和济医院",
    "UNITPTY": "dw",
    "UNITPTY_SUB": "sydw",
    "UPDATETIME": "1705975709000",
    "UPDATEUSER": "",
    "CYBUSRID": "436daf7e5bdda10a4194fa6e7fb100d9",
    "AUDITID": "436daf7e5bdda10a4194fa6e7fb100d9",
    "AUDIT_NAME": "",
    "AUDIT_UNITCODE": "",
    "AUDIT_UNITNAME": "",
    "AUDITTIME": "1705975709000"
  },
  {
    "ID": "e9e3a0e9-2d9e-4f8c-8b35-1a9d80e45d6d",
    "BUSINESSTYPE": "1",
    "CREATETIME": "1705975709000",
    "PVS": "140000",
    "CTY": "140500",
    "CRY": "140581",
    "IDECARDBACKID": "http://127.0.0.1:9999/index/attach_20241107181019/f6226ecc-0051-4029-84ca-d89680191db1.jpg",
    "IDECARDFRONTID": "http://127.0.0.1:9999/index/attach_20241107181019/3cbe916d-06d3-4046-8982-b747d3f45ca3.jpg",
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
    "UITADRSPVS": "",
    "UITADRCTY": "",
    "UITADRCRY": "",
    "UITADRSTR": "",
    "UITCFTID": "",
    "UITCFTNUM": "",
    "UITCFTTYPE": "",
    "UITNM": "",
    "UNITPTY": "gr",
    "UNITPTY_SUB": "",
    "UPDATETIME": "1705975709000",
    "UPDATEUSER": "",
    "CYBUSRID": "a883bbca3f8bc8814ff676cb0e91829a",
    "AUDITID": "a883bbca3f8bc8814ff676cb0e91829a",
    "AUDIT_NAME": "",
    "AUDIT_UNITCODE": "",
    "AUDIT_UNITNAME": "",
    "AUDITTIME": "1705975709000"
  },
  {
    "ID": "e9e3a0e9-2d9e-4f8c-8b35-1a9d80e45d6e",
    "BUSINESSTYPE": "1",
    "CREATETIME": "1705975709000",
    "PVS": "140000",
    "CTY": "140400",
    "CRY": "140425",
    "IDECARDBACKID": "http://127.0.0.1:9999/index/attach_20241107181019/c58ecd71-96a9-441c-a2d9-3251a96aef1a.jpg",
    "IDECARDFRONTID": "http://127.0.0.1:9999/index/attach_20241107181019/e231c9c7-bc4b-4663-a396-fc535f56c8f8.jpg",
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
    "UITADRSPVS": "",
    "UITADRCTY": "",
    "UITADRCRY": "",
    "UITADRSTR": "",
    "UITCFTID": "",
    "UITCFTNUM": "",
    "UITCFTTYPE": "",
    "UITNM": "",
    "UNITPTY": "gr",
    "UNITPTY_SUB": "",
    "UPDATETIME": "1705975709000",
    "UPDATEUSER": "",
    "CYBUSRID": "90ed602fc3a239f835738dfeff08c3ab",
    "AUDITID": "90ed602fc3a239f835738dfeff08c3ab",
    "AUDIT_NAME": "",
    "AUDIT_UNITCODE": "",
    "AUDIT_UNITNAME": "",
    "AUDITTIME": "1705975709000"
  }
]
```