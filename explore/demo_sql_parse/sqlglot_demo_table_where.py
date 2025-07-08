import sqlglot
from sqlglot import exp


def extract_table_where_combinations(sql):
    """
    提取 SQL 中的表名和 WHERE 条件的组合
    :param sql: 输入的 SQL 字符串
    :return: 包含表名和 WHERE 条件的字典列表
    """
    # 解析 SQL
    parsed = sqlglot.parse_one(sql)

    # 存储结果
    results = []

    # 提取所有表名
    tables = [table.name for table in parsed.find_all(exp.Table)]

    # 提取所有 WHERE 条件
    where_conditions = []
    for where_node in parsed.find_all(exp.Where):
        condition = where_node.this.sql()
        where_conditions.append(condition)

    # 组合表名和 WHERE 条件
    for table in tables:
        results.append(
            {
                "table": table,
                "where_conditions": where_conditions,  # 假设所有 WHERE 条件都与表相关
            }
        )

    return results


# 示例 SQL
demo_sql = """INSERT INTO
  fmdbmeta.ADM_DOMAIN_KNOWLEDGE
SELECT
  daw_udf_md5(
    DOMAIN,
    '\t',
    FIRST_CATEGORY,
    '\t',
    SECOND_CATEGORY,
    '\t',
    CATEGORY_RULE
  ) AS MD_ID,
  DOMAIN AS DOMAIN,
  FIRST_CATEGORY AS FIRST_CATEGORY,
  SECOND_CATEGORY AS SECOND_CATEGORY,
  CATEGORY_RULE AS CATEGORY_RULE,
  UPDATETIME AS UPDATETIME,
  CREATOR AS CREATOR,
  UPLOAD_AREA_CODE AS UPLOAD_AREA_CODE
FROM(
    SELECT
      daw_domain_udf_get_format_domain(DOMAIN, cast_to_int('40')) AS DOMAIN,
      '0002' AS FIRST_CATEGORY,
      daw_udf_generic_dic_map(
        string_concat(FIRST_CATEGORY, SECOND_CATEGORY, ''),
        'zcbcategory.dic'
      ) as SECOND_CATEGORY,
      '1' AS CATEGORY_RULE,
      CREATE_TIME AS UPDATETIME,
      null as CREATOR,
      cast_to_int(local_city_code()) as UPLOAD_AREA_CODE
    FROM
      massdata.ADM_DOMAIN_CATEGORY
    where
      FIRST_CATEGORY = '003'
      and (
        SECOND_CATEGORY = '0012'
        or SECOND_CATEGORY = '0013'
        or SECOND_CATEGORY = '0014'
        or SECOND_CATEGORY = '0015'
        or SECOND_CATEGORY = '0016'
        or SECOND_CATEGORY = '0031'
      )
    UNION ALL
    SELECT
      daw_domain_udf_get_format_domain(
        string_concat(SERVER_IPV4_STR, PORT, ':'),
        cast_to_int('40')
      ) AS DOMAIN,
      '0008' AS FIRST_CATEGORY,
      '00080001' SECOND_CATEGORY,
      '1' AS CATEGORY_RULE,
      cast_to_long(UPDATE_TIME) AS UPDATETIME,
      null as CREATOR,
      cast_to_int(local_city_code()) as UPLOAD_AREA_CODE
    FROM
      fmdbmeta.DAW_ODS_PROXY_URL_COLLECT
    WHERE
      STATUS = '1'
  ) t
WHERE
  DOMAIN IS NOT NULL"""


demo_sql_1 = """select 
    a.ID as ID, -- ID
    a.UPLOAD_AREA_CODE as UPLOAD_AREA_CODE, -- 上报地市行政区划代码
    a.ISP_TYPE as ISP_TYPE, -- 运营商信息代码
    a.CAPTURE_TIME as CAPTURE_TIME, -- 截获时间
    a.RELE_DIRECTION_TYPE as RELE_DIRECTION_TYPE, -- 认证关联方向
    a.DATA_SOURCE as DATA_SOURCE, -- 数据来源
    a.SRC_IP as SRC_IP, -- 源IP
    a.DST_IP as DST_IP, -- 宿IP
    a.SRC_IPV6 as SRC_IPV6, -- 源IPv6
    a.DST_IPV6 as DST_IPV6, -- 宿IPv6
    a.SRC_IPID_S as SRC_IPID_S, -- 源IPID
    a.DST_IPID_S as DST_IPID_S, -- 宿IPID
    a.SRC_PORT as SRC_PORT, -- 源端口
    a.DST_PORT as DST_PORT, -- 宿端口
    a.APP_TYPE as APP_TYPE, -- 应用类型
    a.ACTION_TYPE as ACTION_TYPE, -- 动作类别
    a.TOOL_TYPE as TOOL_TYPE, -- 上网工具类型代码
    a.TOOL_NAME as TOOL_NAME, -- 工具名称
    a.MOBILE as MOBILE, -- 无线认证手机号码
    a.AUTH_ACCOUNT as AUTH_ACCOUNT, -- 上网认证帐号
    a.AUTH_TYPE as AUTH_TYPE, -- 上网认证类型
    a.DOMAIN as DOMAIN, -- 域名
    a.URL as URL, -- URL
    a.USERID as USERID, -- 用户ID
    a.USERNAME as USERNAME, -- 用户名
    a.BIND_MOBILE as BIND_MOBILE, -- 用户绑定的手机号码
    a.BIND_EMAIL as BIND_EMAIL, -- 绑定邮箱
    a.REALNAME as REALNAME, -- 姓名
    a.NICKNAME as NICKNAME, -- 昵称
    a.SEND_ACCOUNT as SEND_ACCOUNT, -- 发送者账号
    a.SEND_USERID as SEND_USERID, -- 发送者用户ID
    a.SEND_USERNAME as SEND_USERNAME, -- 发送者用户名
    a.SEND_NICKNAME as SEND_NICKNAME, -- 发送者昵称
    a.SEND_TIME as SEND_TIME, -- 发送时间
    a.CONTENT_S as CONTENT_S, -- 内容
    a.REPLY_CONTENT_S as REPLY_CONTENT_S, -- 评价/评论内容
    a.FILE_NAME as FILE_NAME, -- 文件名称
    a.MAIN_FILE_PATH as MAIN_FILE_PATH, -- 全文路径
    a.PASSWORD as PASSWORD -- 密码
 from ( select DOMAIN,URL,USERID,USERNAME,BIND_MOBILE,BIND_EMAIL,REALNAME,NICKNAME,SEND_ACCOUNT,SEND_USERID,SEND_USERNAME,SEND_NICKNAME,SEND_TIME,CONTENT_S,REPLY_CONTENT_S,FILE_NAME,MAIN_FILE_PATH,PASSWORD,ID,UPLOAD_AREA_CODE,ISP_TYPE,CAPTURE_TIME,RELE_DIRECTION_TYPE,DATA_SOURCE,SRC_IP,DST_IP,SRC_IPV6,DST_IPV6,SRC_IPID_S,DST_IPID_S,SRC_PORT,DST_PORT,APP_TYPE,ACTION_TYPE,TOOL_TYPE,TOOL_NAME,MOBILE,AUTH_ACCOUNT,AUTH_TYPE from massdata.NB_MASS_RESOURCE_ARTICLE) a where a.CAPTURE_TIME>=UNIX_TIMESTAMP()-1*24*3600 AND
 a.APP_TYPE='100000595'
 and a.AUTH_ACCOUNT<>''"""

# 提取表名和 WHERE 条件的组合
results = extract_table_where_combinations(demo_sql_1)
for result in results:
    print(f"表名: {result['table']}, WHERE 条件: {result['where_conditions']}")
