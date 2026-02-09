"""Minimal reproduction script"""

from mini_sqlglot.parser import parse_one

sql_examples = [
    """
    CREATE TABLE t (
        col STRUCT<interval: INT, foo: STRING>
    )
    """,
    """
    CREATE TABLE interval (
        col STRUCT<foo: INT>
    )
    """,
]

for sql in sql_examples:
    print("SQL:", sql)
    ast = parse_one(sql)
    print("AST:", ast)
    print()
