# Feature Specification: Databricks STRUCT Identifier Behavior

This document outlines the expected behavior of the mini_sqlglot parser in `read="databricks"` mode regarding identifier and keyword handling in `CREATE TABLE` statements with `STRUCT` types.

## Context
Databricks SQL supports many keywords that are *contextual* and can be used as identifiers (table names, column names, struct field names) when unquoted. The parser must respect this behavior.

## Requirements

1. **Unquoted identifiers using contextual keywords** must be parsed successfully:
   - `interval` as table name
   - `interval` as column name
   - `interval`, `comment`, `struct` as struct field names
   - Struct fields with `COMMENT` clause using keyword identifiers

2. **Quoted identifiers** (backticks) should continue to work for all cases above.

3. **Invalid struct syntax** must still result in parse errors:
   - Missing colon (`foo INT`)
   - Missing closing angle (`STRUCT<foo: INT`)
   - Missing type (`foo:`)

## Notes
The parser should not globally reserve these keywords; instead, it should accept them as identifiers in appropriate contexts while still recognizing them as keywords where necessary (e.g., the `STRUCT` keyword for type definitions and `COMMENT` for field comments).