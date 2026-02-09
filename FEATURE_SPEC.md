# Databricks STRUCT Identifier Behavior Specification

## Overview
This document specifies the expected behavior for identifier handling in Databricks DDL parsing, particularly for STRUCT field definitions.

## Requirements

### ANSI SQL Compliance
In Databricks' ANSI SQL mode, the following words are NOT reserved keywords and should be usable as identifiers without backticks:
- `interval`
- `comment`
- `struct`

### Valid Syntax Examples
All of the following must parse successfully:

#### Table Names
```sql
CREATE TABLE interval (col STRUCT<foo: INT>)
```

#### Column Names
```sql
CREATE TABLE t (interval STRUCT<foo: INT>)
```

#### Struct Field Names
```sql
CREATE TABLE t (col STRUCT<interval: DOUBLE>)
CREATE TABLE t (col STRUCT<comment: STRING>)
CREATE TABLE t (col STRUCT<struct: INT>)
```

#### With COMMENT Clauses
```sql
CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'description'>)
```

#### Quoted Identifiers (Always Valid)
```sql
CREATE TABLE `interval` (col STRUCT<foo: INT>)
CREATE TABLE t (`interval` STRUCT<foo: INT>)
CREATE TABLE t (col STRUCT<`interval`: DOUBLE>)
CREATE TABLE t (col STRUCT<`interval`: DOUBLE COMMENT 'aaa'>)
```

### Invalid Syntax (Must Still Fail)
The following syntactically invalid constructs must still raise parse errors:

```sql
-- Missing colon
CREATE TABLE t (col STRUCT<interval DOUBLE>)

-- Missing type
CREATE TABLE t (col STRUCT<interval:>)

-- Missing closing bracket
CREATE TABLE t (col STRUCT<interval: INT)
```

## Implementation Notes
- Keywords should be accepted in identifier positions when used as names
- Case sensitivity should be preserved as written
- Backticked identifiers continue to work as before
- Invalid syntax validation must be maintained