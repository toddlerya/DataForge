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
    result = {"tables": [], "columns": [], "conditions": []}

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

    # Translates the query into Spark SQL, formats it, and delimits all of its identifiers
    print(sqlglot.transpile(spark_sql, write="spark", identify=True, pretty=True)[0])

    print("=== 使用sqlglot解析 ===")
    parsed = parse_sql(spark_sql)
    print("表名:", parsed["tables"])
    print("列名:", parsed["columns"])
    print("条件:", parsed["conditions"])
