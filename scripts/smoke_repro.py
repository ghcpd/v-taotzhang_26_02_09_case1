#!/usr/bin/env python3
"""
Smoke test script to demonstrate the Databricks identifier fix.
This script tests the key functionality before and after the fix.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mini_sqlglot.parser import parse_one

def test_case(description, sql, should_pass=True):
    """Test a single SQL case"""
    print(f"\n{description}")
    print(f"SQL: {sql}")
    try:
        result = parse_one(sql)
        if should_pass:
            print("✓ PASS - Parsed successfully")
            return True
        else:
            print("✗ FAIL - Should have failed but parsed successfully")
            return False
    except Exception as e:
        if not should_pass:
            print("✓ PASS - Correctly failed to parse")
            return True
        else:
            print(f"✗ FAIL - Parse error: {e}")
            return False

def main():
    print("Databricks Identifier Handling - Smoke Test")
    print("=" * 50)

    test_cases = [
        # Should pass - unquoted keywords as identifiers
        ("Table name 'interval' (unquoted)", "CREATE TABLE interval (col STRUCT<foo: INT>)", True),
        ("Column name 'interval' (unquoted)", "CREATE TABLE t (interval STRUCT<foo: INT>)", True),
        ("Struct field 'interval' (unquoted)", "CREATE TABLE t (col STRUCT<interval: DOUBLE>)", True),
        ("Struct field 'comment' (unquoted)", "CREATE TABLE t (col STRUCT<comment: STRING>)", True),
        ("Struct field 'struct' (unquoted)", "CREATE TABLE t (col STRUCT<struct: INT>)", True),
        ("Struct field with COMMENT clause", "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'desc'>)", True),

        # Should pass - quoted identifiers
        ("Table name 'interval' (quoted)", "CREATE TABLE `interval` (col STRUCT<foo: INT>)", True),
        ("Column name 'interval' (quoted)", "CREATE TABLE t (`interval` STRUCT<foo: INT>)", True),
        ("Struct field 'interval' (quoted)", "CREATE TABLE t (col STRUCT<`interval`: DOUBLE>)", True),
        ("Quoted field with COMMENT", "CREATE TABLE t (col STRUCT<`interval`: DOUBLE COMMENT 'aaa'>)", True),

        # Should fail - invalid syntax
        ("Missing colon", "CREATE TABLE t (col STRUCT<interval DOUBLE>)", False),
        ("Missing type", "CREATE TABLE t (col STRUCT<interval:>)", False),
        ("Missing closing bracket", "CREATE TABLE t (col STRUCT<interval: INT)", False),
    ]

    passed = 0
    total = len(test_cases)

    for description, sql, should_pass in test_cases:
        if test_case(description, sql, should_pass):
            passed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All smoke tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())