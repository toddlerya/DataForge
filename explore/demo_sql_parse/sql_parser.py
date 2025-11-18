from typing import Dict, List

import sqlglot


def parse_sql(sql: str) -> Dict[str, List[str]]:
    """
    使用 sqlglot 解析SQL语句，提取表名、查询列和WHERE条件

    参数:
        sql: 要解析的SQL字符串

    返回:
        包含解析结果的字典，键为'tables', 'columns', 'conditions'
    """
    result = {"tables": [], "columns": [], "conditions": [], "comments_map": {}}

    try:
        parsed = sqlglot.parse_one(sql)

        # 提取表名
        result["tables"] = [
            table.name for table in parsed.find_all(sqlglot.expressions.Table)
        ]

        # 提取列名
        result["columns"] = [
            col.name for col in parsed.find_all(sqlglot.expressions.Column)
        ]

        result["comments_map"] = [
            col for col in parsed.find_all(sqlglot.expressions.CommentColumnConstraint)
        ]

        # 提取WHERE条件
        where_clause = parsed.find(sqlglot.expressions.Where)
        if where_clause:
            result["conditions"].append(where_clause.sql())

    except Exception as e:
        print(f"解析SQL时出错: {e}")

    return result


if __name__ == "__main__":
    # 示例SQL
    example_sql = """
    SELECT id, name, price
    FROM products
    WHERE price > 100 AND category = 'electronics'
    """

    # Spark SQL requires backticks (`) for delimited identifiers and uses `FLOAT` over `REAL`
    spark_sql = """WITH baz AS (SELECT a, c FROM foo WHERE a = 1) SELECT f.a, b.b, baz.c, CAST("b"."a" AS REAL) d FROM foo f JOIN bar b ON f.a = b.a LEFT JOIN baz ON f.a = baz.a"""

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

    # Translates the query into Spark SQL, formats it, and delimits all of its identifiers
    # print(sqlglot.transpile(demo_sql_1, write="spark", identify=True, pretty=True)[0])
    demo_sql_2 = """INSERT INTO
  TABLE massdata.PHY_ADM_VMODEL_MID10361_TId40592_NId18_170UNJdja
SELECT
  a.dict_id AS dict_id, -- 字典id
  a.dict_pid AS dict_pid, -- 父字典id
  a.dict_type AS dict_type, -- 字典类型
  a.dict_name AS dict_name, -- 字典内容
  a.dict_name_simplify AS dict_name_simplify, -- 字典内容简称
  a.level AS level, -- 字典层级
  a.sort AS sort, -- 排序
  a.create_userid AS create_userid, -- 创建用户id
  a.create_time AS create_time, -- 创建时间
  a.modify_time AS modify_time, -- 修改时间
  a.remark AS remark, -- 备注
  a.status AS status, -- 状态
  a.create_userorg AS create_userorg -- 创建用户组织
FROM
  (
    SELECT
      dict_id,
      dict_pid,
      dict_type,
      dict_name,
      dict_name_simplify,
      level,
      sort,
      create_userid,
      create_time,
      modify_time,
      remark,
      status,
      create_userorg
    FROM
      massdata.zdr_dict_tab
  ) a
WHERE
  dict_type = 'YWCODE_029'
  AND a.status = 0"""

    print("=== 使用sqlglot解析 ===")
    parsed = parse_sql(demo_sql_2)
    print("表名:", parsed["tables"])
    print("列数量:", len(set(parsed["columns"])))
    print("列名", set(parsed["columns"]))
    # print("列名注释", parsed["comments_map"])
    print("条件:", parsed["conditions"])
