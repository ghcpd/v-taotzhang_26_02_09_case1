# Bug Analysis Report

## Bug Identification

After analyzing the codebase, here are the **6 bugs** identified:

### Bug 1: INTERVAL in KEYWORDS set (tokenizer.py, line 15)
**Location**: `src/mini_sqlglot/tokenizer.py`, line 15
**Issue**: `INTERVAL` is included in the KEYWORDS set, causing the tokenizer to treat unquoted `interval` as a keyword (KW) instead of an identifier (IDENT).
**Impact**: Any use of `interval` without backticks will be tokenized as KW, breaking parsing when it should be an identifier.

```python
KEYWORDS = {
    "CREATE", "TABLE", "STRUCT", "COMMENT", "DOUBLE",
    "INTERVAL",  # <-- BUG: Should not be a reserved keyword for ANSI compliance
}
```

---

### Bug 2: parse_struct_field only accepts IDENT for field names (parser.py, lines 72-76)
**Location**: `src/mini_sqlglot/parser.py`, lines 72-76
**Issue**: The parser strictly requires struct field names to be IDENT tokens, rejecting KW tokens.
**Impact**: Even if a keyword should be allowed as an identifier (per Databricks ANSI), it will be rejected.

```python
def parse_struct_field(self) -> StructField:
    tok = self.cur()

    # field name
    if tok.kind == "IDENT":  # <-- BUG: Only accepts IDENT, not KW
        field_name = self.eat("IDENT").text
    else:
        # for now, require identifiers only
        raise ParseError(f"Expected struct field IDENT, got {tok.kind}:{tok.text}")
```

---

### Bug 3: parse_column only accepts IDENT for column names (parser.py, line 55)
**Location**: `src/mini_sqlglot/parser.py`, line 55
**Issue**: The parser strictly requires column names to be IDENT tokens, rejecting KW tokens.
**Impact**: Cannot use keywords like `interval` as column names without backticks.

```python
def parse_column(self) -> ColumnDef:
    name = self.eat("IDENT").text  # <-- BUG: Only accepts IDENT, not KW
    self.eat("KW", "STRUCT")
```

---

### Bug 4: Table name parsing only accepts IDENT (parser.py, line 44)
**Location**: `src/mini_sqlglot/parser.py`, line 44
**Issue**: The parser strictly requires table names to be IDENT tokens, rejecting KW tokens.
**Impact**: Cannot use keywords like `interval` as table names without backticks.

```python
def parse(self) -> CreateTable:
    self.eat("KW", "CREATE")
    self.eat("KW", "TABLE")
    table = self.eat("IDENT").text  # <-- BUG: Only accepts IDENT, not KW
```

---

### Bug 5: COMMENT in KEYWORDS set causes similar issues (tokenizer.py, line 15)
**Location**: `src/mini_sqlglot/tokenizer.py`, line 15
**Issue**: `COMMENT` is in the KEYWORDS set but may need to be used as an identifier in some contexts.
**Impact**: Cannot use `comment` as a field name, column name, or table name without backticks.

```python
KEYWORDS = {
    "CREATE", "TABLE", "STRUCT", "COMMENT", "DOUBLE",  # <-- COMMENT should be contextual
    "INTERVAL",
}
```

---

### Bug 6: STRUCT in KEYWORDS set causes similar issues (tokenizer.py, line 15)
**Location**: `src/mini_sqlglot/tokenizer.py`, line 15
**Issue**: `STRUCT` is in the KEYWORDS set but may need to be used as an identifier in some contexts.
**Impact**: Cannot use `struct` as a field name without backticks.

```python
KEYWORDS = {
    "CREATE", "TABLE", "STRUCT", "COMMENT", "DOUBLE",  # <-- STRUCT should be contextual
    "INTERVAL",
}
```

---

## Root Cause Analysis

The fundamental issues are:

1. **Tokenizer design flaw**: The tokenizer categorizes words as either KW or IDENT globally, without considering context. In SQL, many keywords can also be used as identifiers depending on context.

2. **Parser rigidity**: The parser strictly enforces IDENT tokens for all identifier positions, rather than accepting both IDENT and KW tokens and treating them as identifiers when used in identifier contexts.

## Solution Approach

**Option 1 (Minimal fix)**: Remove non-truly-reserved keywords from KEYWORDS set (like INTERVAL), keeping only structural keywords (CREATE, TABLE, STRUCT).

**Option 2 (Better fix)**: Make the parser context-aware - accept both IDENT and KW tokens in identifier positions and treat KW tokens as identifiers in those contexts.

**Option 3 (Proper fix)**: Implement context-sensitive tokenization or reserved vs. non-reserved keyword distinction as Databricks/ANSI SQL specifies.
