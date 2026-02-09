#!/usr/bin/env python
"""
Minimal reproduction script for Databricks identifier/keyword handling bugs.

This script demonstrates the fix for 6 related bugs where keywords like
'interval', 'comment', and 'struct' were incorrectly rejected as identifiers.

Run with: python scripts/smoke_repro.py
"""

import sys
from pathlib import Path

# Add src to path so we can import mini_sqlglot
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from mini_sqlglot import parse_one, ParseError


def test_case(description: str, sql: str, should_pass: bool = True) -> bool:
    """Test a single SQL case and report results."""
    try:
        result = parse_one(sql)
        if should_pass:
            print(f"✅ PASS: {description}")
            return True
        else:
            print(f"❌ FAIL: {description} - Expected to fail but passed")
            return False
    except ParseError as e:
        if not should_pass:
            print(f"✅ PASS: {description} (correctly failed with: {e})")
            return True
        else:
            print(f"❌ FAIL: {description}")
            print(f"   Error: {e}")
            return False
    except Exception as e:
        print(f"❌ ERROR: {description}")
        print(f"   Unexpected error: {e}")
        return False


def main():
    """Run smoke tests for all 6 bugs."""
    print("=" * 80)
    print("Databricks Identifier/Keyword Handling - Smoke Test")
    print("=" * 80)
    print()

    passed = 0
    total = 0

    # Bug 1-3: Tokenizer level - keywords now work as identifiers
    print("Bug 1-3: Tokenizer - Context-dependent keywords as identifiers")
    print("-" * 80)

    tests = [
        ("Table name: 'interval'", "CREATE TABLE interval (col STRUCT<foo: INT>)", True),
        ("Table name: 'comment'", "CREATE TABLE comment (col STRUCT<foo: INT>)", True),
        ("Table name: 'struct'", "CREATE TABLE struct (col STRUCT<foo: INT>)", True),
        ("Column name: 'interval'", "CREATE TABLE t (interval STRUCT<foo: INT>)", True),
        ("Column name: 'comment'", "CREATE TABLE t (comment STRUCT<foo: INT>)", True),
        ("Column name: 'struct'", "CREATE TABLE t (struct STRUCT<foo: INT>)", True),
        ("Struct field: 'interval'", "CREATE TABLE t (col STRUCT<interval: INT>)", True),
        ("Struct field: 'comment'", "CREATE TABLE t (col STRUCT<comment: STRING>)", True),
        ("Struct field: 'struct'", "CREATE TABLE t (col STRUCT<struct: DOUBLE>)", True),
    ]

    for desc, sql, should_pass in tests:
        total += 1
        if test_case(desc, sql, should_pass):
            passed += 1

    print()
    print("Bug 4-6: Parser - Accepting keywords in identifier positions")
    print("-" * 80)

    tests = [
        ("Quoted identifier: 'interval'", "CREATE TABLE `interval` (col STRUCT<foo: INT>)", True),
        ("Quoted column: 'interval'", "CREATE TABLE t (`interval` STRUCT<foo: INT>)", True),
        ("Quoted struct field", "CREATE TABLE t (col STRUCT<`interval`: INT>)", True),
        ("With COMMENT clause", "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'desc'>)", True),
    ]

    for desc, sql, should_pass in tests:
        total += 1
        if test_case(desc, sql, should_pass):
            passed += 1

    print()
    print("Invalid Syntax (should still fail)")
    print("-" * 80)

    tests = [
        ("Missing colon", "CREATE TABLE t (col STRUCT<foo INT>)", False),
        ("Missing closing bracket", "CREATE TABLE t (col STRUCT<foo: INT)", False),
        ("Missing type", "CREATE TABLE t (col STRUCT<foo:>)", False),
    ]

    for desc, sql, should_pass in tests:
        total += 1
        if test_case(desc, sql, should_pass):
            passed += 1

    print()
    print("Complex Scenarios")
    print("-" * 80)

    tests = [
        (
            "Multiple keywords in one struct",
            "CREATE TABLE t (col STRUCT<interval: INT, comment: STRING, struct: DOUBLE>)",
            True
        ),
        (
            "Keywords in all positions",
            "CREATE TABLE interval (comment STRUCT<struct: INT COMMENT 'nested'>)",
            True
        ),
    ]

    for desc, sql, should_pass in tests:
        total += 1
        if test_case(desc, sql, should_pass):
            passed += 1

    print()
    print("=" * 80)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 80)

    if passed == total:
        print("✅ All smoke tests passed!")
        return 0
    else:
        print(f"❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
