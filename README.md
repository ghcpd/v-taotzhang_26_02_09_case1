# Databricks Identifier/Keyword Handling Fix

## Problem
The mini SQL parser incorrectly treated certain words (`interval`, `comment`, `struct`) as globally reserved keywords, preventing their use as identifiers without backticks in Databricks DDL statements. This violated Databricks' ANSI SQL compliance, where these words should be usable as identifiers in appropriate contexts.

## Root Cause
1. **Tokenizer Issue**: Words like `INTERVAL` were included in the global `KEYWORDS` set, causing them to be tokenized as `KW` tokens instead of `IDENT` tokens.
2. **Parser Rigidity**: The parser strictly required `IDENT` tokens for identifier positions (table names, column names, struct field names), rejecting `KW` tokens even when they should be valid identifiers.

## Solution
1. **Removed unnecessary keywords**: Removed `INTERVAL` from the `KEYWORDS` set since it wasn't used as a reserved keyword in the grammar.
2. **Modified parser to accept KW tokens as identifiers**: Added `eat_ident_or_kw()` method and updated parsing logic to accept both `IDENT` and `KW` tokens in identifier positions.
3. **Preserved case sensitivity**: Modified tokenizer to preserve the original case of tokens while still recognizing keywords case-insensitively.

## Changes Made

### `src/mini_sqlglot/tokenizer.py`
- Removed `"INTERVAL"` from `KEYWORDS` set
- Modified token creation to preserve original case for `KW` tokens

### `src/mini_sqlglot/parser.py`
- Added `eat_ident_or_kw()` method to accept both `IDENT` and `KW` tokens
- Updated `parse()` to use `eat_ident_or_kw()` for table names
- Updated `parse_column()` to use `eat_ident_or_kw()` for column names
- Updated `parse_struct_field()` to accept `KW` tokens for field names

## Before/After Examples

### Before (Failed)
```sql
CREATE TABLE interval (col STRUCT<foo: INT>)  -- ParseError
CREATE TABLE t (interval STRUCT<foo: INT>)   -- ParseError
CREATE TABLE t (col STRUCT<interval: DOUBLE>) -- ParseError
```

### After (Success)
```sql
CREATE TABLE interval (col STRUCT<foo: INT>)  -- ✓ Parses successfully
CREATE TABLE t (interval STRUCT<foo: INT>)   -- ✓ Parses successfully
CREATE TABLE t (col STRUCT<interval: DOUBLE>) -- ✓ Parses successfully
```

## Testing
Run the comprehensive test suite:
```bash
python -m pytest tests/test_databricks_struct_interval.py -v
```

The test suite covers:
- Unquoted keywords as table names, column names, and struct field names
- Quoted identifiers still work
- Invalid syntax still fails appropriately
- COMMENT clauses with keyword identifiers

## API Compatibility
The public API `parse_one(sql: str, read: str = "databricks") -> CreateTable` remains unchanged. All existing valid syntax continues to work.