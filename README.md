# mini_sqlglot

A lightweight SQL parser for a small subset of Databricks DDL, focusing on `CREATE TABLE` statements with `STRUCT` types. This project demonstrates handling of Databricks identifier keyword rules and provides a simple AST.

## Features

- Parses `CREATE TABLE` statements with nested `STRUCT` types
- Supports unquoted identifiers, including keywords like `interval`, `comment`, and `struct` when used in identifier contexts
- Allows quoted identifiers using backticks
- Optional `COMMENT` clause on struct fields

## Installation

No installation required. Use Python 3.10+ and set the `PYTHONPATH` to the `src` directory.

## Usage

```python
from mini_sqlglot.parser import parse_one

sql = """
CREATE TABLE t (
    col STRUCT<interval: INT, foo: STRING>
)
"""

ast = parse_one(sql)
print(ast)
```

## Testing

Run tests with:

```bash
$ export PYTHONPATH=src
$ pytest
```

or on Windows PowerShell:

```powershell
$env:PYTHONPATH="src"; pytest
```
