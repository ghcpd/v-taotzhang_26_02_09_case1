from mini_sqlglot.parser import parse_one

sqls = [
    "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'aaa'>)",
    "CREATE TABLE interval (col STRUCT<foo: INT>)",
]

for sql in sqls:
    print("SQL:", sql)
    try:
        tree = parse_one(sql)
        print("Parsed:", tree)
    except Exception as e:
        print("Error:", e)
    print()
