import re
import sqlparse
from typing import Dict, List, Optional

def parse_sql(sql: str) -> Dict[str, List[str]]:
    """
    解析SQL语句，提取表名、查询列和WHERE条件

    参数:
        sql: 要解析的SQL字符串

    返回:
        包含解析结果的字典，键为'tables', 'columns', 'conditions'
    """
    # 标准化SQL格式
    formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
    parsed = sqlparse.parse(formatted_sql)[0]

    result = {
        'tables': [],
        'columns': [],
        'conditions': []
    }

    # 提取表名
    from_clause = None
    for token in parsed.tokens:
        if isinstance(token, sqlparse.sql.IdentifierList):
            for identifier in token.get_identifiers():
                if hasattr(identifier, 'get_real_name'):
                    result['tables'].append(identifier.get_real_name())
        elif isinstance(token, sqlparse.sql.Identifier):
            if hasattr(token, 'get_real_name'):
                result['tables'].append(token.get_real_name())
        elif token.is_keyword and token.value.upper() == 'FROM':
            from_clause = True

    # 提取列名
    select_seen = False
    for token in parsed.tokens:
        if token.is_keyword and token.value.upper() == 'SELECT':
            select_seen = True
            continue
        if select_seen:
            if isinstance(token, sqlparse.sql.IdentifierList):
                for identifier in token.get_identifiers():
                    result['columns'].append(str(identifier))
            elif isinstance(token, sqlparse.sql.Identifier):
                result['columns'].append(str(token))
            elif token.is_keyword and token.value.upper() in ('FROM', 'WHERE'):
                select_seen = False

    # 提取WHERE条件
    where_clause = None
    for token in parsed.tokens:
        if token.is_keyword and token.value.upper() == 'WHERE':
            where_clause = token
            break

    if where_clause:
        # 获取WHERE后面的所有token
        where_idx = parsed.tokens.index(where_clause)
        where_tokens = parsed.tokens[where_idx+1:]

        # 组合条件表达式
        condition = ' '.join(str(t) for t in where_tokens)
        result['conditions'] = [condition.strip()]

    return result

def simple_regex_parse(sql: str) -> Dict[str, List[str]]:
    """
    使用正则表达式简单解析SQL（备用方法）
    """
    result = {
        'tables': [],
        'columns': [],
        'conditions': []
    }

    # 提取表名
    table_pattern = r'(?:FROM|JOIN)\s+([\w\.]+)'
    result['tables'] = re.findall(table_pattern, sql, re.IGNORECASE)

    # 提取列名
    select_pattern = r'SELECT\s+(.+?)\s+FROM'
    select_match = re.search(select_pattern, sql, re.IGNORECASE|re.DOTALL)
    if select_match:
        columns = [col.strip() for col in select_match.group(1).split(',')]
        result['columns'] = columns

    # 提取WHERE条件
    where_pattern = r'WHERE\s+(.+)'
    where_match = re.search(where_pattern, sql, re.IGNORECASE)
    if where_match:
        result['conditions'] = [where_match.group(1).strip()]

    return result

if __name__ == "__main__":
    # 示例SQL
    example_sql = """
    SELECT id, name, price
    FROM products
    WHERE price > 100 AND category = 'electronics'
    """

    print("=== 使用sqlparse解析 ===")
    parsed = parse_sql(example_sql)
    print("表名:", parsed['tables'])
    print("列名:", parsed['columns'])
    print("条件:", parsed['conditions'])

    print("\n=== 使用正则表达式解析 ===")
    regex_parsed = simple_regex_parse(example_sql)
    print("表名:", regex_parsed['tables'])
    print("列名:", regex_parsed['columns'])
    print("条件:", regex_parsed['conditions'])