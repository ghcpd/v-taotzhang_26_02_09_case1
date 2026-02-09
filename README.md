# mini_sqlglot

Lightweight SQL parser for a subset of Databricks DDL, focusing on CREATE TABLE with STRUCT types.

## Features

- Parses `CREATE TABLE` statements with `STRUCT<...>` columns.
- Supports optional `COMMENT '...'` on struct fields.
- Recognizes and allows context-dependent keywords (e.g., `interval`, `comment`, `struct`) as identifiers per Databricks ANSI mode.

## Usage

```python
from mini_sqlglot.parser import parse_one

sql = """
CREATE TABLE t (
    col STRUCT<interval: DOUBLE COMMENT 'aaa'>
)
"""

table = parse_one(sql)
print(table)
```

## Running Tests

A suite of regression tests is provided under `tests/`.

```sh
python -m unittest
```

Or use the provided run scripts:

- `run_tests.sh` (Linux/macOS)
- `run_tests.ps1` (Windows PowerShell)

## Dependencies

See `requirements.txt` and `requirements-dev.txt` for runtime and development dependencies.
