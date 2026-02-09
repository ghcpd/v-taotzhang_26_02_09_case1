# Databricks STRUCT Identifier Behavior - Feature Specification

## Overview

This specification documents the expected behavior of the Databricks SQL parser for handling keywords as identifiers in STRUCT field contexts, aligned with Databricks' ANSI compliance for context-dependent keywords.

## Requirements

### 1. Keywords Must Be Usable as Identifiers Without Backticks

The parser MUST accept the following keywords as unquoted identifiers in appropriate contexts:

- `INTERVAL` - used in type definitions, table names, column names, struct field names
- `COMMENT` - used in field names, struct field names (not just as COMMENT keyword)
- `STRUCT` - used as a type name, struct field name (not just as STRUCT keyword)
- `DOUBLE` - used as a field name (in addition to its role as a type keyword)

**Rationale**: Per Databricks documentation, these are not truly reserved keywords but rather context-dependent keywords that should be usable as identifiers when appropriate.

### 2. Supported Contexts

Keywords as identifiers MUST work in these contexts:

#### 2.1 Table Names
```sql
CREATE TABLE interval (col STRUCT<foo: INT>)
CREATE TABLE comment (col STRUCT<foo: INT>)
CREATE TABLE struct (col STRUCT<foo: INT>)
```

**Expected Behavior**: Successful parse with table_name = "interval" (or comment, struct)

#### 2.2 Column Names
```sql
CREATE TABLE t (interval STRUCT<foo: INT>)
CREATE TABLE t (comment STRUCT<foo: INT>)
CREATE TABLE t (struct STRUCT<foo: INT>)
```

**Expected Behavior**: Successful parse with column.name = "interval" (or comment, struct)

#### 2.3 Struct Field Names
```sql
CREATE TABLE t (col STRUCT<interval: INT>)
CREATE TABLE t (col STRUCT<comment: STRING>)
CREATE TABLE t (col STRUCT<struct: DOUBLE>)
CREATE TABLE t (col STRUCT<double: INT>)
```

**Expected Behavior**: Successful parse with struct_field.name = "interval" (or comment, struct, double)

#### 2.4 Struct Field Names with COMMENT Clauses
```sql
CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'time interval'>)
CREATE TABLE t (col STRUCT<comment: STRING COMMENT 'field comment'>)
CREATE TABLE t (col STRUCT<struct: INT COMMENT 'struct definition'>)
```

**Expected Behavior**: Successful parse with:
- struct_field.name = "interval" (or comment, struct)
- struct_field.type_name = appropriate type
- struct_field.comment = comment text

### 3. Backward Compatibility - Quoted Identifiers

All existing quoted identifier syntax MUST continue to work:

```sql
CREATE TABLE `interval` (col STRUCT<foo: INT>)
CREATE TABLE t (`interval` STRUCT<foo: INT>)
CREATE TABLE t (col STRUCT<`interval`: INT>)
CREATE TABLE t (col STRUCT<`comment`: STRING>)
CREATE TABLE t (col STRUCT<`struct`: DOUBLE>)
CREATE TABLE t (col STRUCT<`interval`: DOUBLE COMMENT 'text'>)
```

**Expected Behavior**: All should parse successfully with appropriate identifier values

### 4. Invalid Syntax Must Still Fail

The following invalid patterns MUST continue to fail with appropriate ParseError:

```sql
-- Missing colon
CREATE TABLE t (col STRUCT<foo INT>)

-- Missing closing bracket
CREATE TABLE t (col STRUCT<foo: INT)

-- Missing type after colon
CREATE TABLE t (col STRUCT<foo:>)

-- Missing STRUCT keyword
CREATE TABLE t (col <foo: INT>)

-- Missing opening parenthesis
CREATE TABLE t col STRUCT<foo: INT>

-- Missing closing parenthesis
CREATE TABLE t (col STRUCT<foo: INT>
```

**Expected Behavior**: ParseError raised with descriptive message

### 5. Complex Combinations

The parser MUST handle complex combinations of keywords and regular identifiers:

```sql
CREATE TABLE interval (
  col1 STRUCT<foo: INT>,
  comment STRUCT<interval: STRING, bar: DOUBLE>,
  struct STRUCT<comment: INT COMMENT 'nested', baz: STRING>
)
```

**Expected Behavior**: Successful parse with all identifiers recognized correctly:
- Table: "interval"
- Columns: ["col1", "comment", "struct"]
- Fields in col1.comment: ["foo"]
- Fields in comment.comment: ["interval", "bar"]
- Fields in struct.comment: ["comment" (with comment text "nested"), "baz"]

### 6. Regular Identifiers Must Continue to Work

Standard identifier patterns MUST continue to work:

```sql
CREATE TABLE my_table (
  my_column STRUCT<
    field1: INT,
    field_2: STRING,
    my_type: DOUBLE
  >
)
```

**Expected Behavior**: Successful parse with all identifiers preserved

## Implementation Strategy

### Tokenizer Changes

Remove context-dependent keywords from the global KEYWORDS set, keeping only truly structural keywords:

**Before:**
```python
KEYWORDS = {"CREATE", "TABLE", "STRUCT", "COMMENT", "DOUBLE", "INTERVAL"}
```

**After:**
```python
KEYWORDS = {"CREATE", "TABLE"}
```

**Effect**: Context-dependent keywords are tokenized as IDENT when not in structural positions.

### Parser Changes

Modify identifier parsing in three places to accept both IDENT and KW tokens:

1. **Table name parsing** (parse method)
2. **Column name parsing** (parse_column method)
3. **Struct field name parsing** (parse_struct_field method)

Also make parsing of STRUCT keyword and COMMENT keyword more flexible to work regardless of token kind.

## Edge Cases

### E1: Keyword Used as Type Name
```sql
CREATE TABLE t (col STRUCT<foo: INTERVAL>)
```
**Expected**: Should work - INTERVAL is a valid type name

### E2: Multiple Keywords in Same Struct
```sql
CREATE TABLE t (col STRUCT<interval: INT, comment: STRING, struct: DOUBLE>)
```
**Expected**: All should parse successfully

### E3: Whitespace and Formatting
```sql
CREATE TABLE
  interval
(
  comment STRUCT< struct : INT >
)
```
**Expected**: Should parse - whitespace is flexible

### E4: Empty/Single-Field Structs
```sql
CREATE TABLE t (col STRUCT<interval: INT>)
```
**Expected**: Single-field STRUCT with keyword field name should work

## Success Criteria

✅ All 6 identified bugs are fixed
✅ Keywords work unquoted in all identifier positions
✅ Quoted identifiers continue to work
✅ Invalid syntax still fails appropriately
✅ Complex multi-column, multi-field scenarios work
✅ Backward compatibility maintained
✅ 31+ regression tests pass
✅ No new dependencies introduced
✅ Code remains readable and maintainable

## Databricks Compliance

This implementation aligns with Databricks' treatment of context-dependent keywords as documented in:
- [Databricks SQL Language Reference - Reserved Keywords](https://docs.databricks.com/sql/language-manual/sql-ref-keywords.html)
- [Databricks - ANSI Compliance](https://docs.databricks.com/sql/language-manual/)

Per Databricks documentation, keywords like `INTERVAL`, `COMMENT`, and `STRUCT` are not universally reserved and can be used as identifiers in appropriate contexts.

## Testing Strategy

### Unit Tests
- Individual keyword contexts (table, column, struct field)
- Quoted vs unquoted variations
- Invalid syntax patterns
- Comment clause with keywords
- Mixed keywords and regular identifiers

### Integration Tests
- Complex multi-column, multi-field scenarios
- Edge cases
- Backward compatibility verification

### Regression Tests
- All 6 bugs explicitly covered
- Before/after verification
- Error message clarity
