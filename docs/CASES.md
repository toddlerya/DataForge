# 工具

## FakerFactory

### 目前已经支持的数据类型

即columns字段的可选参数

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

### 单次请求数据返回上限为10000条

即number参数的取值区间为[1,10000]

### 使用方法

http://{IP}:8001/api/v1/fakerfactory?number={条数}&columns={字段参数[多个字段以英文逗号分隔]}



# ADM_GRAPH_NODE_FLIGHT

## 表结构字段含义如下

```json
[
  {
    "name": "航班唯一标识",
    "ename": "FLIGHT",
    "desc": "航班唯一标识"
  },
  {
    "name": "航班号",
    "ename": "FLIG_NO",
    "desc": "航班号"
  },
  {
    "name": "始发机场名称",
    "ename": "DEP_AIR",
    "desc": "始发机场名称"
  },
  {
    "name": "终点机场名称",
    "ename": "ARR_AIR",
    "desc": "终点机场名称"
  },
  {
    "name": "始发站行政区划代码",
    "ename": "DEP_CITY_CODE",
    "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空"
  },
  {
    "name": "终点站行政区划代码",
    "ename": "ARR_CITY_CODE",
    "desc": "CODE_ADDR_PHY_0001\n若无法归一化，则填空"
  }
]

```

## 建表语句

```sql
CREATE TABLE
  fmdbmeta.ADM_GRAPH_NODE_FLIGHT (
    flight STRING,
    flig_no STRING,
    dep_air STRING,
    arr_air STRING,
    dep_city_code STRING,
    arr_city_code STRING
  ) PARTITIONED BY (p1 string, p2 string, p3 string, p4 string) LOCATION 'hdfs://ngpcluster/nebula_datacenter/import/daml/data/adm/graph/node/ADM_GRAPH_NODE_FLIGHT' TBLPROPERTIES (
    'hive.output.file.extension' = '.nb',
    'serialization.null.format' = ''
  ) ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t' STORED AS TEXTFILE 
```

## 河图任务SQL

```json
[
  {
    "project_name": "核心资产-WA方向-关系上图",
    "dev_dir_name": "数据应用-关系上图-点提取",
    "workflow_name": "航班",
    "job_id": "cece840b-dfd4-435e-86cd-9b34d223fc7c",
    "flag": 2,
    "job_desc": "图库：航班节点"
  }
]
```

```sql
-- Modify: 李雯萍
-- Time:20191228
-- Description:增加起始机场和到达机场所对应的地市
-- Modify: cc
-- Time:20230420
-- Description:目前暂增加dw_wa_adm_graph_dicloader空函数，保证函数包中字典能同时加载到
-- -------------------------------------------------
INSERT INTO fmdbmeta.ADM_GRAPH_NODE_FLIGHT
SELECT md5_id(FLIG_NO, '\t', DEP_AIR, '\t', ARR_AIR) AS FLIGHT,
       FLIG_NO                                       AS FLIG_NO,
       DEP_AIR                                       AS DEP_AIR,
       ARR_AIR                                       AS ARR_AIR,
       DEP_CITY_CODE                                 AS DEP_CITY_CODE,
       ARR_CITY_CODE                                 AS ARR_CITY_CODE
FROM (
         SELECT FLIG_NO       AS FLIG_NO,
                dw_wa_adm_graph_dicloader('123') AS TEST,
                DEP_AIR       AS DEP_AIR,
                ARR_AIR       AS ARR_AIR,
                DEP_CITY_CODE AS DEP_CITY_CODE,
                ARR_CITY_CODE AS ARR_CITY_CODE
         FROM fmdbmeta.ADM_GRAPH_NODE_FLIGHT ADM_GRAPH_NODE_FLIGHT
         UNION
         SELECT FLIG_NUM                                           AS FLIG_NO,
                dw_wa_adm_graph_dicloader('123') AS TEST,
                map_finder(DEPARTURE_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_NAME.DIC')            AS DEP_AIR,
                map_finder(ARR_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_NAME.DIC')                  AS ARR_AIR,
                map_finder(DEPARTURE_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_ADDI_CODE.DIC') AS DEP_CITY_CODE,
                map_finder(ARR_AIR, 'PYRAMID_ADM_MAPPING_AIRPORT_ADDI_CODE.DIC')       AS ARR_CITY_CODE
         FROM fmdbmeta.DWS_PER_RES_DAY_DCFLIGHT DWS_PER_RES_DAY_DCFLIGHT
         WHERE FLIG_NUM IS NOT NULL
           AND DEPARTURE_AIR IS NOT NULL
           AND ARR_AIR IS NOT NULL
     ) ADM_GRAPH_NODE_FLIGHT_TMP
GROUP BY FLIG_NO,
         DEP_AIR,
         ARR_AIR,
         DEP_CITY_CODE,
         ARR_CITY_CODE
```

### 获取盘古字典信息

https://172.21.4.42:11018/standard/standard/dictionary/list?keyword=%E7%BD%91%E7%AB%99%E8%A7%84%E6%A8%A1%E7%AD%89%E7%BA%A7%E7%B1%BB%E5%9E%8B&parentCode=-1

```json
{
  "status" : 200,
  "data" : [ {
    "id" : "FHWACODE_0198",
    "name" : "网站规模等级类型",
    "description" : "",
    "parentId" : "-1",
    "parentName" : null,
    "nlevel" : "1",
    "whenSubmit" : 0,
    "whoSubmit" : null,
    "code" : 82366,
    "parentCode" : -1,
    "flag" : 1,
    "status" : 1,
    "gabTabCode" : null,
    "gabTabName" : null,
    "userDefine" : 0,
    "gabDicList" : null,
    "isParent" : 0
  } ],
  "msg" : "OK"
}
```

https://172.21.4.42:11018/standard/standard/dictionary/all?id=FHWACODE_0198&nlevel=1&code=82366&keyword=&userDefine=0&pagesize=10&pageno=1

```json
{
  "status" : 200,
  "data" : {
    "pageno" : 1,
    "pagesize" : 10,
    "pages" : 1,
    "totalrows" : 3,
    "start_time" : null,
    "end_time" : null,
    "from" : 1,
    "to" : 3,
    "sort" : "",
    "orderby" : null,
    "datas" : [ {
      "nlevel" : null,
      "code" : 91722,
      "flag" : 1,
      "isParent" : 0,
      "whenSubmit" : 0,
      "validBean" : true,
      "whoSubmit" : null,
      "description" : "",
      "gabDicList" : null,
      "parentId" : null,
      "gabTabName" : null,
      "parentName" : null,
      "userDefine" : 0,
      "parentCode" : 0,
      "name" : "超大型",
      "dicFlag" : 0,
      "id" : "1",
      "gabTabCode" : null,
      "status" : 1
    }, {
      "nlevel" : null,
      "code" : 91723,
      "flag" : 1,
      "isParent" : 0,
      "whenSubmit" : 0,
      "validBean" : true,
      "whoSubmit" : null,
      "description" : "",
      "gabDicList" : null,
      "parentId" : null,
      "gabTabName" : null,
      "parentName" : null,
      "userDefine" : 0,
      "parentCode" : 0,
      "name" : "大型",
      "dicFlag" : 0,
      "id" : "2",
      "gabTabCode" : null,
      "status" : 1
    }, {
      "nlevel" : null,
      "code" : 91724,
      "flag" : 1,
      "isParent" : 0,
      "whenSubmit" : 0,
      "validBean" : true,
      "whoSubmit" : null,
      "description" : "",
      "gabDicList" : null,
      "parentId" : null,
      "gabTabName" : null,
      "parentName" : null,
      "userDefine" : 0,
      "parentCode" : 0,
      "name" : "中小型",
      "dicFlag" : 0,
      "id" : "3",
      "gabTabCode" : null,
      "status" : 1
    } ]
  },
  "msg" : "OK"
}
```