# ADM_GRAPH_NODE_FLIGHT表-提示词效果测试

> 测试的模型：`test.DeepSeek-R1-Distill-Qwen-14B-AWQ`
> 参数：`SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.6, top_p=0.95, top_k=-1, min_p=0.0, seed=None, stop=[], stop_token_ids=[], bad_words=[], include_stop_str_in_output=False, ignore_eos=False, max_tokens=9354, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, truncate_prompt_tokens=None, guided_decoding=None, extra_args=None)`

## 字段映射填充Agent-提示词测试

### 测试1
#### 提示词

````markdown
你是一个数据治理业务专家，现在请完成如下任务。
# 任务
理解表的名称、字段信息，映射到FakerFactory工具的参数中，输出表的字段与工具参数的映射字典关关系，并回填表字段信息的list[dict]结构，每个字段的dict增加两个字段参数: map_arg, reason。
# 表名称
- 中文名称: 航班节点表
- 英文名称: ADM_GRAPH_NODE_FLIGHT
# 表字段信息
```json
[{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识'}, {'name': '航班号', 'ename': 'FLIG_NO', 'desc': '航班号'}, {'name': '始发机场名称', 'ename': 'DEP_AIR', 'desc': '始发机场名称'}, {'name': '终点机场名称', 'ename': 'ARR_AIR', 'desc': '终点机场名称'}, {'name': '始发站行政区划代码', 'ename': 'DEP_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空'}, {'name': '终点站行政区划代码', 'ename': 'ARR_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空'}]
```
# FakerFactory工具参数
|     参数     | 说明                                                         |
| :----------: | ------------------------------------------------------------ |
|    color     | 颜色                                                         |
|     job      | 职业                                                         |
|     name     | 中文名字                                                     |
|     sex      | 性别                                                         |
|   address    | 地址信息（地区编号、邮编、固话区号、省市信息、社区名称、社区简称、经纬度） |
|    idcard    | 大陆居民身份证号码                                           |
|     age      | 年龄                                                         |
| mobilephone  | 移动电话号码                                                 |
|    email     | 电子邮箱                                                     |
|     imid     | IM类型的用户ID                                               |
|   nickname   | 用户昵称                                                     |
|   username   | 用户名                                                       |
|   password   | 用户密码                                                     |
|   website    | 网站地址                                                     |
|     url      | 网址URL（随机http或https）                                   |
|   airport    | 国内机场信息（IATA编码、城市名称、ICAO编码、机场名称、城市拼音） |
|    voyage    | 国内航班号                                                   |
| airlineinfo  | 国内航空公司信息（代号、中文名称）                           |
|  traintrips  | 火车班次（覆盖高铁、动车、特快、普快、城际、旅游专线）       |
|  trainseat   | 火车座号                                                     |
|  flightseat  | 飞机座号                                                     |
|     ipv4     | ipv4的点分型IP地址                                           |
|     ipv6     | ipv6的点分型IP地址                                           |
|     mac      | mac地址（随机大小写，分隔符）                                |
|  useragent   | 浏览器请求头                                                 |
|     imsi     | IMSI（目前只支持国内460开头的）                              |
|     imei     | IMEI（目前支持中国、英国、美国）                             |
|     meid     | MEID（随机大小写）                                           |
|   deviceid   | DEVICEID（设备编号）                                         |
|   telphone   | 固定电话（暂时只支持国内号码）                               |
|   citycode   | 国内长途区号                                                 |
| specialphone | 特殊电话号码（比如10086、110）                               |
| capturetime  | 当前时间绝对秒（10位数字）                                   |
|     date     | 当前时间，数据库日期格式{YYYYMMDD,hh:mm:ss}                  |
|   carbrand   | 汽车品牌（中文）                                             |
````



#### 结果

http://172.17.55.71:13579/s/92b9a56b-4519-49f6-9eab-f84757ced77a

```json
[
    {
        "name": "航班唯一标识",
        "ename": "FLIGHT",
        "desc": "航班唯一标识",
        "map_arg": "voyage",
        "reason": "映射到Faker的国内航班号参数"
    },
    {
        "name": "航班号",
        "ename": "FLIG_NO",
        "desc": "航班号",
        "map_arg": "voyage",
        "reason": "映射到Faker的国内航班号参数"
    },
    {
        "name": "始发机场名称",
        "ename": "DEP_AIR",
        "desc": "始发机场名称",
        "map_arg": "airport",
        "reason": "映射到Faker的国内机场信息参数"
    },
    {
        "name": "终点机场名称",
        "ename": "ARR_AIR",
        "desc": "终点机场名称",
        "map_arg": "airport",
        "reason": "映射到Faker的国内机场信息参数"
    },
    {
        "name": "始发站行政区划代码",
        "ename": "DEP_CITY_CODE",
        "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
        "map_arg": "citycode",
        "reason": "映射到Faker的国内长途区号参数"
    },
    {
        "name": "终点站行政区划代码",
        "ename": "ARR_CITY_CODE",
        "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
        "map_arg": "citycode",
        "reason": "映射到Faker的国内长途区号参数"
    }
]
```

#### 评价
- "航班唯一标识"字段映射错误，映射到了`voyage`，
  - 期望是`airlineinfo`
- "始发站行政区划代码"、"终点站行政区划代码"映射错误，映射到了`citycode`国内长途区号
  - 期望是`address.zipcode`

### 测试2
补充`FakerFactory`工具参数说明的中文含义

#### 修改1
`address    | 地址信息（地区编号、邮编、固话区号、省市信息、社区名称、社区简称、经纬度） `
改为
`address    | 地址信息（**行政区划代码**、邮编、固话区号、省市信息、社区名称、社区简称、经纬度） `
#### 修改2
`| airlineinfo  | 国内航空公司信息（代号、中文名称）                           |`
改为
`| airlineinfo  | 国内航空公司信息（代号、航班唯一标识、中文名称）                |`

#### 提示词

````markdown
你是一个数据治理业务专家，现在请完成如下任务。
# 任务
理解表的名称、字段信息，映射到FakerFactory工具的参数中，输出表的字段与工具参数的映射字典关关系，并回填表字段信息的list[dict]结构，每个字段的dict增加两个字段参数: map_arg, reason。
# 表名称
- 中文名称: 航班节点表
- 英文名称: ADM_GRAPH_NODE_FLIGHT
# 表字段信息
```json
[{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识'}, {'name': '航班号', 'ename': 'FLIG_NO', 'desc': '航班号'}, {'name': '始发机场名称', 'ename': 'DEP_AIR', 'desc': '始发机场名称'}, {'name': '终点机场名称', 'ename': 'ARR_AIR', 'desc': '终点机场名称'}, {'name': '始发站行政区划代码', 'ename': 'DEP_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空'}, {'name': '终点站行政区划代码', 'ename': 'ARR_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空'}]
```
# FakerFactory工具参数
|     参数     | 说明                                                         |
| :----------: | ------------------------------------------------------------ |
|    color     | 颜色                                                         |
|     job      | 职业                                                         |
|     name     | 中文名字                                                     |
|     sex      | 性别                                                         |
|   address    | 地址信息（行政区划代码、邮编、固话区号、省市信息、社区名称、社区简称、经纬度） |
|    idcard    | 大陆居民身份证号码                                           |
|     age      | 年龄                                                         |
| mobilephone  | 移动电话号码                                                 |
|    email     | 电子邮箱                                                     |
|     imid     | IM类型的用户ID                                               |
|   nickname   | 用户昵称                                                     |
|   username   | 用户名                                                       |
|   password   | 用户密码                                                     |
|   website    | 网站地址                                                     |
|     url      | 网址URL（随机http或https）                                   |
|   airport    | 国内机场信息（IATA编码、城市名称、ICAO编码、机场名称、城市拼音） |
|    voyage    | 国内航班号                                                   |
| airlineinfo  | 国内航空公司信息（代号、航班唯一标识、中文名称）                           |
|  traintrips  | 火车班次（覆盖高铁、动车、特快、普快、城际、旅游专线）       |
|  trainseat   | 火车座号                                                     |
|  flightseat  | 飞机座号                                                     |
|     ipv4     | ipv4的点分型IP地址                                           |
|     ipv6     | ipv6的点分型IP地址                                           |
|     mac      | mac地址（随机大小写，分隔符）                                |
|  useragent   | 浏览器请求头                                                 |
|     imsi     | IMSI（目前只支持国内460开头的）                              |
|     imei     | IMEI（目前支持中国、英国、美国）                             |
|     meid     | MEID（随机大小写）                                           |
|   deviceid   | DEVICEID（设备编号）                                         |
|   telphone   | 固定电话（暂时只支持国内号码）                               |
|   citycode   | 国内长途区号                                                 |
| specialphone | 特殊电话号码（比如10086、110）                               |
| capturetime  | 当前时间绝对秒（10位数字）                                   |
|     date     | 当前时间，数据库日期格式{YYYYMMDD,hh:mm:ss}                  |
|   carbrand   | 汽车品牌（中文）                                             |
````

#### 结果

http://172.17.55.71:13579/s/96507daf-6c67-4f6d-9a64-3dad7c3c1966

```json
{
  "表名称": {
    "中文名称": "航班节点表",
    "英文名称": "ADM_GRAPH_NODE_FLIGHT"
  },
  "表字段与工具参数映射关系": [
    {
      "name": "航班唯一标识",
      "ename": "FLIGHT",
      "desc": "航班唯一标识",
      "map_arg": "airlineinfo",
      "reason": "airlineinfo参数包含航班唯一标识"
    },
    {
      "name": "航班号",
      "ename": "FLIG_NO",
      "desc": "航班号",
      "map_arg": "voyage",
      "reason": "voyage参数对应国内航班号"
    },
    {
      "name": "始发机场名称",
      "ename": "DEP_AIR",
      "desc": "始发机场名称",
      "map_arg": "airport",
      "reason": "airport参数包含机场城市名称"
    },
    {
      "name": "终点机场名称",
      "ename": "ARR_AIR",
      "desc": "终点机场名称",
      "map_arg": "airport",
      "reason": "airport参数包含机场城市名称"
    },
    {
      "name": "始发站行政区划代码",
      "ename": "DEP_CITY_CODE",
      "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
      "map_arg": "address",
      "reason": "address参数包含行政区划代码"
    },
    {
      "name": "终点站行政区划代码",
      "ename": "ARR_CITY_CODE",
      "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空",
      "map_arg": "address",
      "reason": "address参数包含行政区划代码"
    }
  ]
}
```

#### 评价

全对了

#### 总结

需要将工具的参数注释说明，统一为公司数仓体系的术语

## 仿真测试数据生成Agent-提示词测试

### 测试1

#### 提示词

````markdown
你是一个数仓业务专家，现在请完成如下任务。
# 任务
根据表结构字段信息与样例数据映射关系的映射关系、样例数据、表的sql条件等信息构造表的测试数据
# 要求
1. 数据尽可能真实；
2. 不知道的的数据含义不要随便生成，请遵循表字段与样例数据映射关系和样例数据；
3. 遵循表的sql条件，确保生成的数据满足sql条件。
# 表结构字段信息与样例数据映射关系
```json
{'表名称': {'中文名称': '航班节点表', '英文名称': 'ADM_GRAPH_NODE_FLIGHT'}, '表字段与工具参数映射关系': [{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识', 'map_arg': 'airlineinfo', 'reason': 'airlineinfo参数包含航班唯一标识'}, {'name': '航班号', 'ename': 'FLIG_NO', 'desc': '航班号', 'map_arg': 'voyage', 'reason': 'voyage参数对应国内航班号'}, {'name': '始发机场名称', 'ename': 'DEP_AIR', 'desc': '始发机场名称', 'map_arg': 'airport', 'reason': 'airport参数包含机场城市名称'}, {'name': '终点机场名称', 'ename': 'ARR_AIR', 'desc': '终点机场名称', 'map_arg': 'airport', 'reason': 'airport参数包含机场城市名称'}, {'name': '始发站行政区划代码', 'ename': 'DEP_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空', 'map_arg': 'address', 'reason': 'address参数包含行政区划代码'}, {'name': '终点站行政区划代码', 'ename': 'ARR_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空', 'map_arg': 'address', 'reason': 'address参数包含行政区划代码'}]}
```
# 样例数据
```json
[{'address': {'area_code': '512022114000', 'area_name': '四川,资阳,乐至,东山', 'city_code': '0832', 'lat': '30.200743', 'lng': '105.114734', 'name': '东山镇', 'short_name': '东山', 'zip_code': '641503'}, 'airlineinfo': {'code': 'JD', 'name': '金鹿航空'}, 'airport': {'city': '毕节', 'iata_code': 'BFJ', 'icao_code': 'ZUBJ', 'name': '毕节飞雄机场', 'pinyin': 'BIJIE'}, 'voyage': 'EU229'}, {'address': {'area_code': '331002008232', 'area_name': '浙江,台州,椒江,章安,黄礁', 'city_code': '0576', 'lat': '28.673726', 'lng': '121.442676', 'name': '黄礁村委会', 'short_name': '黄礁', 'zip_code': '318017'}, 'airlineinfo': {'code': 'KA', 'name': '港龙航空'}, 'airport': {'city': '银川', 'iata_code': 'INC', 'icao_code': 'ZLIC', 'name': '银川河东国际机场', 'pinyin': 'YINCHUAN'}, 'voyage': 'UO6194'}]
```
# 表SQL条件
```json
[{'table_name': 'ADM_GRAPH_NODE_FLIGHT', 'where_condition': 'FLIG_NO is not null and DEP_AIR is not null and ARR_AIR is not null'}]
```
````

#### 结果

http://172.17.55.71:13579/s/33b7ac45-40fd-470e-815e-e9ba47a21613

```json
{
  "测试数据": [
    {
      "airlineinfo": {
        "code": "MU",
        "name": "中国国航"
      },
      "airport": {
        "city": "北京",
        "iata_code": "PEK",
        "icao_code": "ZBAA",
        "name": "北京大兴国际机场",
        "pinyin": "BEIJING"
      },
      "voyage": "MU5101",
      "DEP_CITY_CODE": "010",
      "ARR_CITY_CODE": "021"
    },
    {
      "airlineinfo": {
        "code": "CA",
        "name": "国航"
      },
      "airport": {
        "city": "上海",
        "iata_code": "PVG",
        "icao_code": "ZSSS",
        "name": "上海浦东国际机场",
        "pinyin": "SHANGHAI"
      },
      "voyage": "CA1234",
      "DEP_CITY_CODE": "021",
      "ARR_CITY_CODE": "020"
    },
    {
      "airlineinfo": {
        "code": "HU",
        "name": "海南航空"
      },
      "airport": {
        "city": "广州",
        "iata_code": "CAN",
        "icao_code": "ZGGG",
        "name": "广州白云国际机场",
        "pinyin": "GUANGZHOU"
      },
      "voyage": "HU7201",
      "DEP_CITY_CODE": "020",
      "ARR_CITY_CODE": "010"
    },
    {
      "airlineinfo": {
        "code": "CZ",
        "name": "中国南方航空"
      },
      "airport": {
        "city": "深圳",
        "iata_code": "SZX",
        "icao_code": "ZGSZ",
        "name": "深圳宝安国际机场",
        "pinyin": "SHENZHEN"
      },
      "voyage": "CZ3802",
      "DEP_CITY_CODE": "0755",
      "ARR_CITY_CODE": "021"
    }
  ]
}
```

#### 评价

完全错误，没有遵循表的字段信息，按照映射结果字段输出的信息

### 测试2

#### 修改1
增加提示词片段
```markdown
# 输出格式
列表嵌套字典的json结构，每个字典以ename参数为key, 样例数据为value
```
#### 修改2
修改表结构字段信息与样例数据映射关系，明确map_arg对应样例数据的节点值
比如：
`{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识', 'map_arg': 'airlineinfo', 'reason': 'airlineinfo参数包含航班唯一标识'}`
改为
`{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识', 'map_arg': 'airlineinfo.code', 'reason': 'airlineinfo参数包含航班唯一标识'}`

#### 修改3
精简样例数据无用的内容
比如：
`{'address': {'area_code': '512022114000', 'area_name': '四川,资阳,乐至,东山', 'city_code': '0832', 'lat': '30.200743', 'lng': '105.114734', 'name': '东山镇', 'short_name': '东山', 'zip_code': '641503'}`
精简为
`{'address.zipcode': {'zip_code': '641503'}`

#### 提示词

````markdown
你是一个数仓业务专家，现在请完成如下任务。
# 任务
根据表结构字段信息与样例数据映射关系的映射关系、样例数据、表的sql条件等信息构造表的测试数据
# 要求
1. 数据尽可能真实；
2. 不知道的的数据含义不要随便生成，请遵循表字段与样例数据映射关系和样例数据；
3. 遵循表的sql条件，确保生成的数据满足sql条件。
# 输出格式
列表嵌套字典的json结构，每个字典以ename参数为key, 样例数据为value
# 表结构字段信息与样例数据映射关系
```json
{'表名称': {'中文名称': '航班节点表', '英文名称': 'ADM_GRAPH_NODE_FLIGHT'}, '表字段与工具参数映射关系': [{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识', 'map_arg': 'airlineinfo.code', 'reason': 'airlineinfo参数包含航班唯一标识'}, {'name': '航班号', 'ename': 'FLIG_NO', 'desc': '航班号', 'map_arg': 'voyage', 'reason': 'voyage参数对应国内航班号'}, {'name': '始发机场名称', 'ename': 'DEP_AIR', 'desc': '始发机场名称', 'map_arg': 'airport.name', 'reason': 'airport参数包含机场城市名称'}, {'name': '终点机场名称', 'ename': 'ARR_AIR', 'desc': '终点机场名称', 'map_arg': 'airport.name', 'reason': 'airport参数包含机场城市名称'}, {'name': '始发站行政区划代码', 'ename': 'DEP_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空', 'map_arg': 'address.zipcode', 'reason': 'address参数包含行政区划代码'}, {'name': '终点站行政区划代码', 'ename': 'ARR_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空', 'map_arg': 'address.zipcode', 'reason': 'address参数包含行政区划代码'}]}
```
# 样例数据
```json
[{'address.zipcode': {'zip_code': '641503'}, 'airlineinfo': {'code': 'JD', 'name': '金鹿航空'}, 'airport': {'city': '毕节', 'iata_code': 'BFJ', 'icao_code': 'ZUBJ', 'name': '毕节飞雄机场', 'pinyin': 'BIJIE'}, 'voyage': 'EU229'}, {'address': {'zip_code': '318017'}, 'airlineinfo': {'code': 'KA', 'name': '港龙航空'}, 'airport': {'city': '银川', 'iata_code': 'INC', 'icao_code': 'ZLIC', 'name': '银川河东国际机场', 'pinyin': 'YINCHUAN'}, 'voyage': 'UO6194'}]
```
# 表SQL条件
```json
[{'table_name': 'ADM_GRAPH_NODE_FLIGHT', 'where_condition': 'FLIG_NO is not null and DEP_AIR is not null and ARR_AIR is not null'}]
```
````

#### 结果

http://172.17.55.71:13579/s/55b785e9-4a77-4d45-850a-9dd9c938f25c

```json
[
    {
        "FLIGHT": "JD",
        "FLIG_NO": "EU229",
        "DEP_AIR": "毕节",
        "ARR_AIR": "毕节",
        "DEP_CITY_CODE": "641503",
        "ARR_CITY_CODE": "641503"
    },
    {
        "FLIGHT": "KA",
        "FLIG_NO": "UO6194",
        "DEP_AIR": "银川",
        "ARR_AIR": "银川",
        "DEP_CITY_CODE": "318017",
        "ARR_CITY_CODE": "318017"
    }
]
```

#### 评价
数据结构正确，key-value格式正确，但是逻辑错误，因为我的where条件中没有说明出发地和目的地不能相同

### 测试3:

#### 修改1

增加表SQL条件

比如：

`FLIG_NO is not null and DEP_AIR is not null and ARR_AIR is not null`

改为

`FLIG_NO is not null and DEP_AIR is not null and ARR_AIR is not null and DEP_AIR != ARR_AIR and DEP_CITY_CODE != ARR_CITY_CODE`

#### 提示词

````markdown
你是一个数仓业务专家，现在请完成如下任务。
# 任务
根据表结构字段信息与样例数据映射关系的映射关系、样例数据、表的sql条件等信息构造表的测试数据
# 要求
1. 数据尽可能真实；
2. 不知道的的数据含义不要随便生成，请遵循表字段与样例数据映射关系和样例数据；
3. 遵循表的sql条件，确保生成的数据满足sql条件。
# 输出格式
列表嵌套字典的json结构，每个字典以ename参数为key, 样例数据为value
# 表结构字段信息与样例数据映射关系
```json
{'表名称': {'中文名称': '航班节点表', '英文名称': 'ADM_GRAPH_NODE_FLIGHT'}, '表字段与工具参数映射关系': [{'name': '航班唯一标识', 'ename': 'FLIGHT', 'desc': '航班唯一标识', 'map_arg': 'airlineinfo.code', 'reason': 'airlineinfo参数包含航班唯一标识'}, {'name': '航班号', 'ename': 'FLIG_NO', 'desc': '航班号', 'map_arg': 'voyage', 'reason': 'voyage参数对应国内航班号'}, {'name': '始发机场名称', 'ename': 'DEP_AIR', 'desc': '始发机场名称', 'map_arg': 'airport.name', 'reason': 'airport参数包含机场城市名称'}, {'name': '终点机场名称', 'ename': 'ARR_AIR', 'desc': '终点机场名称', 'map_arg': 'airport.name', 'reason': 'airport参数包含机场城市名称'}, {'name': '始发站行政区划代码', 'ename': 'DEP_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空', 'map_arg': 'address.zipcode', 'reason': 'address参数包含行政区划代码'}, {'name': '终点站行政区划代码', 'ename': 'ARR_CITY_CODE', 'desc': 'CODE_ADDR_PHY_0001\n若无法归一化，则填空', 'map_arg': 'address.zipcode', 'reason': 'address参数包含行政区划代码'}]}
```
# 样例数据
```json
[{'address.zipcode': {'zip_code': '641503'}, 'airlineinfo': {'code': 'JD', 'name': '金鹿航空'}, 'airport': {'city': '毕节', 'iata_code': 'BFJ', 'icao_code': 'ZUBJ', 'name': '毕节飞雄机场', 'pinyin': 'BIJIE'}, 'voyage': 'EU229'}, {'address': {'zip_code': '318017'}, 'airlineinfo': {'code': 'KA', 'name': '港龙航空'}, 'airport': {'city': '银川', 'iata_code': 'INC', 'icao_code': 'ZLIC', 'name': '银川河东国际机场', 'pinyin': 'YINCHUAN'}, 'voyage': 'UO6194'}]
```
# 表SQL条件
```json
[{'table_name': 'ADM_GRAPH_NODE_FLIGHT', 'where_condition': 'FLIG_NO is not null and DEP_AIR is not null and ARR_AIR is not null and DEP_AIR != ARR_AIR and DEP_CITY_CODE != ARR_CITY_CODE'}]
```
````

#### 结果

http://172.17.55.71:13579/s/caebb692-b902-4faf-879a-a5f48dd046ea

```json
[
    {
        "FLIGHT": "JD",
        "FLIG_NO": "EU229",
        "DEP_AIR": "毕节飞雄机场",
        "ARR_AIR": "银川河东国际机场",
        "DEP_CITY_CODE": "641503",
        "ARR_CITY_CODE": "318017"
    },
    {
        "FLIGHT": "KA",
        "FLIG_NO": "UO6194",
        "DEP_AIR": "上海虹桥机场",
        "ARR_AIR": "北京首都国际机场",
        "DEP_CITY_CODE": "318017",
        "ARR_CITY_CODE": "100000"
    },
    {
        "FLIGHT": "CZ",
        "FLIG_NO": "CZ389",
        "DEP_AIR": "广州白云国际机场",
        "ARR_AIR": "深圳宝安国际机场",
        "DEP_CITY_CODE": "410000",
        "ARR_CITY_CODE": "440370"
    },
    {
        "FLIGHT": "MU",
        "FLIG_NO": "MU532",
        "DEP_AIR": "成都双流国际机场",
        "ARR_AIR": "重庆江北国际机场",
        "DEP_CITY_CODE": "610204",
        "ARR_CITY_CODE": "401143"
    },
    {
        "FLIGHT": "HU",
        "FLIG_NO": "HU789",
        "DEP_AIR": "海口美兰国际机场",
        "ARR_AIR": "三亚凤凰国际机场",
        "DEP_CITY_CODE": "570100",
        "ARR_CITY_CODE": "571099"
    }
]
```

#### 评价

格式，结构、逻辑都正确，但是LLM编造了4条提供的样例之外的新数据。

### 总结

需要精简样例数据内容，更清晰的明确映射字段和参数的关系。

