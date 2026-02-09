# Feature Specification

## Databricks STRUCT Identifier Behavior

According to Databricks' ANSI SQL compliance, certain words are treated as *contextual keywords* and may be used as identifiers unless they conflict with specific grammar rules. The parser must recognize these rules:

- Words such as `interval`, `comment`, and `struct` are not globally reserved and can be used as table names, column names, or struct field names without quoting.
- Quoted identifiers using backticks (`\``) must continue to function as regular identifiers.
- Keywords like `CREATE`, `TABLE`, and `STRUCT` when used as part of the grammar should still be recognized as keywords.

### Examples

```sql
-- valid
CREATE TABLE interval (col STRUCT<foo: INT>);
CREATE TABLE t (interval STRUCT<foo: INT>);
CREATE TABLE t (col STRUCT<interval: DOUBLE>);
CREATE TABLE t (col STRUCT<comment: STRING>);
CREATE TABLE t (col STRUCT<struct: INT>);
CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'desc'>);

-- quoted identifiers
CREATE TABLE `interval` (col STRUCT<foo: INT>);
CREATE TABLE t (`interval` STRUCT<foo: INT>);
CREATE TABLE t (col STRUCT<`interval`: DOUBLE>);
CREATE TABLE t (col STRUCT<`interval`: DOUBLE COMMENT 'aaa'>);

-- invalid syntax (should fail)
CREATE TABLE t (col STRUCT<interval INT>);   -- missing ':'
CREATE TABLE t (col STRUCT<interval: >);      -- missing type
CREATE TABLE t (col STRUCT<interval: INT,>);  -- trailing comma
```

