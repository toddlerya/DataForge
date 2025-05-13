for select in parse_one("SELECT a, b + 1 AS c FROM d").find_all(exp.Select):
#     for projection in select.expressions:
#         print(projection.alias_or_name)