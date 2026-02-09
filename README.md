# Mini SQLGlot - Databricks Identifier/Keyword Handling Fix

A lightweight SQL parsing module supporting Databricks DDL with proper handling of context-dependent keywords as identifiers.

## Overview

This project provides a minimal implementation of a Databricks SQL parser that correctly handles keywords like `interval`, `comment`, and `struct` as identifiers in appropriate contexts, following Databricks' ANSI compliance rules.

## Problem Statement

Previously, the parser incorrectly treated context-dependent keywords as globally reserved, preventing valid Databricks SQL from parsing:

```sql
-- These should work but previously failed:
CREATE TABLE interval (col STRUCT<foo: INT>)
CREATE TABLE t (interval STRUCT<foo: INT>)
CREATE TABLE t (col STRUCT<interval: INT>)
CREATE TABLE t (col STRUCT<comment: STRING>)
```

## Solution

The fix implements a two-part approach:

1. **Tokenizer**: Separated "structural" keywords (CREATE, TABLE) from "context-dependent" keywords (INTERVAL, COMMENT, STRUCT, DOUBLE), keeping only structural keywords as globally reserved.

2. **Parser**: Modified identifier parsing in three contexts to accept both IDENT and KW tokens:
   - Table names
   - Column names
   - Struct field names

This allows keywords to be used as identifiers while still maintaining proper syntax validation.

## Architecture

```
src/mini_sqlglot/
├── __init__.py          # Public API export
├── tokenizer.py         # SQL tokenization
├── parser.py            # SQL parsing with keyword handling
└── ast.py              # Abstract Syntax Tree definitions

tests/
└── test_databricks_struct_interval.py  # Comprehensive regression tests

scripts/
└── smoke_repro.py      # Minimal reproduction and verification script
```

## Key Changes

### Tokenizer (`tokenizer.py`)

**Before:**
```python
KEYWORDS = {
    "CREATE", "TABLE", "STRUCT", "COMMENT", "DOUBLE", "INTERVAL",
}
```

**After:**
```python
# Structural keywords only - globally reserved
KEYWORDS = {
    "CREATE", "TABLE",
}
```

Context-dependent keywords are now tokenized as IDENT when not in their structural role.

### Parser (`parser.py`)

**Before:**
```python
def parse_column(self):
    name = self.eat("IDENT").text  # Strict requirement for IDENT
    self.eat("KW", "STRUCT")
```

**After:**
```python
def parse_column(self):
    col_tok = self.cur()
    if col_tok.kind not in ("IDENT", "KW"):  # Accept both
        raise ParseError(...)
    name = self.eat(col_tok.kind).text
```

Similar changes applied to table name parsing and struct field name parsing.

## Usage

```python
from mini_sqlglot import parse_one

# Keywords as table names
sql = "CREATE TABLE interval (col STRUCT<foo: INT>)"
result = parse_one(sql)
assert result.table_name == "interval"

# Keywords as column names
sql = "CREATE TABLE t (interval STRUCT<foo: INT>)"
result = parse_one(sql)
assert result.columns[0].name == "interval"

# Keywords as struct field names
sql = "CREATE TABLE t (col STRUCT<interval: INT>)"
result = parse_one(sql)
assert result.columns[0].struct_fields[0].name == "interval"

# With COMMENT clause
sql = "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'description'>)"
result = parse_one(sql)
field = result.columns[0].struct_fields[0]
assert field.name == "interval"
assert field.comment == "description"
```

## Testing

### Run All Tests

```powershell
# Windows
$env:PYTHONPATH="src"
python -m pytest tests/ -v

# Or use the provided script
.\run_tests.ps1
```

### Test Coverage

The comprehensive test suite (`tests/test_databricks_struct_interval.py`) includes:

- **31 regression tests** organized into 7 test classes
- **Keyword as table name tests**: Verifies keywords work unquoted as table names
- **Keyword as column name tests**: Verifies keywords work unquoted as column names
- **Keyword as struct field name tests**: Verifies keywords work unquoted as struct field names
- **Complex scenario tests**: Mixed keyword/non-keyword identifiers
- **Invalid syntax tests**: Ensures syntactic errors still fail appropriately
- **Type variation tests**: Various type names including keyword types
- **Comment handling tests**: COMMENT clauses with keyword identifiers

### Supported SQL Features

✅ CREATE TABLE with single/multiple columns
✅ STRUCT type definitions with multiple fields
✅ Field-level COMMENT clauses
✅ Backticked identifiers (quoted with backticks)
✅ Keywords as identifiers (interval, comment, struct, double)
✅ Mixed keyword and regular identifiers

### Verified Invalid Patterns (Still Fail as Expected)

❌ Missing colon in struct field definition
❌ Missing closing bracket on STRUCT
❌ Missing type after colon
❌ Missing STRUCT keyword
❌ Missing parentheses

## Files

### Core Implementation
- [src/mini_sqlglot/tokenizer.py](src/mini_sqlglot/tokenizer.py) - Tokenization logic
- [src/mini_sqlglot/parser.py](src/mini_sqlglot/parser.py) - Parsing logic
- [src/mini_sqlglot/ast.py](src/mini_sqlglot/ast.py) - AST definitions
- [src/mini_sqlglot/__init__.py](src/mini_sqlglot/__init__.py) - Public API

### Testing
- [tests/test_databricks_struct_interval.py](tests/test_databricks_struct_interval.py) - Comprehensive regression tests
- [test_interval_bug.py](test_interval_bug.py) - Original bug reproduction tests

### Documentation
- [README.md](README.md) - This file
- [FEATURE_SPEC.md](FEATURE_SPEC.md) - Detailed feature specification

### Scripts
- [scripts/smoke_repro.py](scripts/smoke_repro.py) - Minimal reproduction script

## Scope

### In Scope
- Tokenizer behavior for context-dependent keywords
- Parser behavior for accepting keywords in identifier positions
- Databricks ANSI compliance for keyword handling
- Comment parsing on struct fields

### Out of Scope
- Full SQL dialect coverage beyond CREATE TABLE with STRUCT
- Complex nested types beyond base implementation
- Other SQL statements (SELECT, INSERT, etc.)

## Design Principles

1. **Minimal Changes**: Only modified tokenizer keyword set and parser identifier parsing
2. **Backward Compatible**: All previously valid SQL continues to work
3. **ANSI Compliant**: Follows Databricks documentation for context-dependent keywords
4. **Well-Tested**: 31 regression tests covering all 6 identified bugs
5. **Readable Code**: Clear comments explaining keyword handling strategy

## Verification

Before and after verification with specific test cases:

```python
# Bug 1-3: Keywords now work as identifiers at tokenizer level
# Bug 4: Table names can now be keywords
# Bug 5: Column names can now be keywords
# Bug 6: Struct field names can now be keywords

parse_one("CREATE TABLE interval (col STRUCT<foo: INT>)")           # ✅ Works
parse_one("CREATE TABLE t (interval STRUCT<foo: INT>)")            # ✅ Works
parse_one("CREATE TABLE t (col STRUCT<interval: INT>)")            # ✅ Works
parse_one("CREATE TABLE t (col STRUCT<comment: STRING>)")          # ✅ Works
parse_one("CREATE TABLE t (col STRUCT<struct: INT>)")              # ✅ Works
parse_one("CREATE TABLE t (col STRUCT<interval: INT COMMENT ''>)") # ✅ Works
```

## Requirements

- Python 3.7+
- No external dependencies for core parsing
- pytest for testing (optional, only needed to run test suite)

## Future Enhancements

While out of scope for this fix, potential future improvements include:

- Support for nested STRUCT types
- Support for other Databricks types (ARRAY, MAP)
- SELECT, INSERT, UPDATE, DELETE statements
- More granular dialect-specific tokenization
- Error recovery for better diagnostic messages
