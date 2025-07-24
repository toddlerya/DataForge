import time
from datetime import datetime

table_en_name = "fmdbmeta.DWD_BEH_TRANS_ENTRY_RT"

current_p3_timestamp = int(time.time())
current_p4_date = datetime.strftime(datetime.now(), "%Y%m%d")

insert_sql = f"INSERT INTO {table_en_name} " \
             f"PARTITION (p1='final', p2='update', p3={current_p3_timestamp}, p4={current_p4_date}) " \
             f"VALUES "


with open("1753343777_p0_0.txt", mode="r", encoding="utf-8") as r:
    content = r.readlines()
    for index, line in enumerate(content, start=1):
        line_value_tuple = tuple(line.rstrip("\n").split("\t"))
        insert_sql += str(line_value_tuple)
        if index < len(content):
            insert_sql += ", "
        else:
            insert_sql += ";"
    print(insert_sql)
