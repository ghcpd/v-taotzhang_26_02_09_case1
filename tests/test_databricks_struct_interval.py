"""
Regression tests for Databricks identifier/keyword handling.

Tests verify that keywords like 'interval', 'comment', and 'struct'
can be used as identifiers in appropriate contexts without backticks,
following Databricks ANSI compliance for context-dependent keywords.
"""

import unittest
from mini_sqlglot.parser import parse_one, ParseError
from mini_sqlglot.ast import CreateTable, ColumnDef, StructField


class TestKeywordAsTableName(unittest.TestCase):
    """Test keywords used as table names (Bug 4)"""

    def test_table_name_interval_unquoted(self):
        """interval as table name (unquoted)"""
        sql = "CREATE TABLE interval (col STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.table_name, "interval")
        self.assertEqual(len(result.columns), 1)

    def test_table_name_interval_quoted(self):
        """interval as table name (quoted with backticks)"""
        sql = "CREATE TABLE `interval` (col STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.table_name, "interval")

    def test_table_name_comment_unquoted(self):
        """comment as table name (unquoted)"""
        sql = "CREATE TABLE comment (col STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.table_name, "comment")

    def test_table_name_struct_unquoted(self):
        """struct as table name (unquoted)"""
        sql = "CREATE TABLE struct (col STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.table_name, "struct")


class TestKeywordAsColumnName(unittest.TestCase):
    """Test keywords used as column names (Bug 5)"""

    def test_column_name_interval_unquoted(self):
        """interval as column name (unquoted)"""
        sql = "CREATE TABLE t (interval STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(len(result.columns), 1)
        self.assertEqual(result.columns[0].name, "interval")

    def test_column_name_interval_quoted(self):
        """interval as column name (quoted with backticks)"""
        sql = "CREATE TABLE t (`interval` STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.columns[0].name, "interval")

    def test_column_name_comment_unquoted(self):
        """comment as column name (unquoted)"""
        sql = "CREATE TABLE t (comment STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.columns[0].name, "comment")

    def test_column_name_struct_unquoted(self):
        """struct as column name (unquoted)"""
        sql = "CREATE TABLE t (struct STRUCT<foo: INT>)"
        result = parse_one(sql)
        self.assertIsInstance(result, CreateTable)
        self.assertEqual(result.columns[0].name, "struct")

    def test_multiple_columns_with_keywords(self):
        """Multiple columns with keyword names"""
        sql = "CREATE TABLE t (interval STRUCT<foo: INT>, comment STRUCT<bar: STRING>)"
        result = parse_one(sql)
        self.assertEqual(len(result.columns), 2)
        self.assertEqual(result.columns[0].name, "interval")
        self.assertEqual(result.columns[1].name, "comment")


class TestKeywordAsStructFieldName(unittest.TestCase):
    """Test keywords used as struct field names (Bug 6)"""

    def test_struct_field_interval_unquoted(self):
        """interval as struct field name (unquoted)"""
        sql = "CREATE TABLE t (col STRUCT<interval: INT>)"
        result = parse_one(sql)
        self.assertEqual(len(result.columns[0].struct_fields), 1)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "interval")
        self.assertEqual(field.type_name, "INT")

    def test_struct_field_interval_quoted(self):
        """interval as struct field name (quoted with backticks)"""
        sql = "CREATE TABLE t (col STRUCT<`interval`: INT>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "interval")

    def test_struct_field_comment_unquoted(self):
        """comment as struct field name (unquoted)"""
        sql = "CREATE TABLE t (col STRUCT<comment: INT>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "comment")

    def test_struct_field_struct_unquoted(self):
        """struct as struct field name (unquoted)"""
        sql = "CREATE TABLE t (col STRUCT<struct: INT>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "struct")

    def test_struct_field_double_unquoted(self):
        """double as struct field name (unquoted)"""
        sql = "CREATE TABLE t (col STRUCT<double: INT>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "double")

    def test_multiple_struct_fields_with_keywords(self):
        """Multiple struct fields with keyword names"""
        sql = "CREATE TABLE t (col STRUCT<interval: INT, comment: STRING, struct: DOUBLE>)"
        result = parse_one(sql)
        fields = result.columns[0].struct_fields
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name, "interval")
        self.assertEqual(fields[1].name, "comment")
        self.assertEqual(fields[2].name, "struct")

    def test_struct_field_with_comment_and_keyword_field_name(self):
        """Struct field with keyword name and COMMENT clause"""
        sql = "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'time interval'>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "interval")
        self.assertEqual(field.type_name, "DOUBLE")
        self.assertEqual(field.comment, "time interval")

    def test_struct_field_mixed_keywords_and_regular_names(self):
        """Mix of keyword and regular identifiers in struct fields"""
        sql = "CREATE TABLE t (col STRUCT<foo: INT, interval: STRING, bar: DOUBLE, comment: INT>)"
        result = parse_one(sql)
        fields = result.columns[0].struct_fields
        self.assertEqual(len(fields), 4)
        self.assertEqual(fields[0].name, "foo")
        self.assertEqual(fields[1].name, "interval")
        self.assertEqual(fields[2].name, "bar")
        self.assertEqual(fields[3].name, "comment")


class TestComplexScenarios(unittest.TestCase):
    """Test complex combinations of keyword identifiers"""

    def test_all_keyword_positions(self):
        """Keywords in all identifier positions simultaneously"""
        sql = (
            "CREATE TABLE interval ("
            "  comment STRUCT<struct: INT COMMENT 'nested'>"
            ")"
        )
        result = parse_one(sql)
        self.assertEqual(result.table_name, "interval")
        self.assertEqual(result.columns[0].name, "comment")
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "struct")
        self.assertEqual(field.comment, "nested")

    def test_multiple_columns_mixed_keywords(self):
        """Multiple columns with varied keyword/non-keyword names"""
        sql = (
            "CREATE TABLE interval ("
            "  col1 STRUCT<foo: INT>,"
            "  interval STRUCT<comment: STRING>,"
            "  comment STRUCT<struct: DOUBLE>"
            ")"
        )
        result = parse_one(sql)
        self.assertEqual(result.table_name, "interval")
        self.assertEqual(len(result.columns), 3)
        self.assertEqual(result.columns[0].name, "col1")
        self.assertEqual(result.columns[1].name, "interval")
        self.assertEqual(result.columns[2].name, "comment")


class TestInvalidSyntaxStillFails(unittest.TestCase):
    """Verify that syntactically invalid constructs still fail"""

    def test_missing_colon_in_struct_field(self):
        """Missing : in struct field definition"""
        sql = "CREATE TABLE t (col STRUCT<foo INT>)"
        with self.assertRaises(ParseError):
            parse_one(sql)

    def test_missing_closing_bracket(self):
        """Missing > to close struct"""
        sql = "CREATE TABLE t (col STRUCT<foo: INT)"
        with self.assertRaises(ParseError):
            parse_one(sql)

    def test_missing_type_after_colon(self):
        """Missing type after : in struct field"""
        sql = "CREATE TABLE t (col STRUCT<foo:>)"
        with self.assertRaises(ParseError):
            parse_one(sql)

    def test_missing_struct_keyword(self):
        """Missing STRUCT keyword in column definition"""
        sql = "CREATE TABLE t (col <foo: INT>)"
        with self.assertRaises(ParseError):
            parse_one(sql)

    def test_missing_opening_paren(self):
        """Missing opening parenthesis"""
        sql = "CREATE TABLE t col STRUCT<foo: INT>"
        with self.assertRaises(ParseError):
            parse_one(sql)

    def test_missing_closing_paren(self):
        """Missing closing parenthesis"""
        sql = "CREATE TABLE t (col STRUCT<foo: INT>"
        with self.assertRaises(ParseError):
            parse_one(sql)


class TestTypeVariations(unittest.TestCase):
    """Test struct fields with various type names"""

    def test_type_is_keyword(self):
        """Type name that is also a keyword"""
        sql = "CREATE TABLE t (col STRUCT<interval: INTERVAL>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.type_name, "INTERVAL")

    def test_regular_type_names(self):
        """Regular non-keyword type names"""
        sql = "CREATE TABLE t (col STRUCT<foo: INT, bar: STRING, baz: DOUBLE>)"
        result = parse_one(sql)
        fields = result.columns[0].struct_fields
        self.assertEqual(fields[0].type_name, "INT")
        self.assertEqual(fields[1].type_name, "STRING")
        self.assertEqual(fields[2].type_name, "DOUBLE")


class TestCommentHandling(unittest.TestCase):
    """Test COMMENT clause on struct fields"""

    def test_comment_with_keyword_field_name(self):
        """COMMENT clause on field with keyword name"""
        sql = "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'description'>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "interval")
        self.assertEqual(field.comment, "description")

    def test_comment_with_regular_field_name(self):
        """COMMENT clause on field with regular name"""
        sql = "CREATE TABLE t (col STRUCT<foo: INT COMMENT 'comment text'>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "foo")
        self.assertEqual(field.comment, "comment text")

    def test_comment_keyword_as_field_name(self):
        """Field named 'comment' with comment clause"""
        sql = "CREATE TABLE t (col STRUCT<comment: STRING COMMENT 'a comment field'>)"
        result = parse_one(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "comment")
        self.assertEqual(field.comment, "a comment field")

    def test_multiple_fields_some_with_comments(self):
        """Multiple fields, some with COMMENT clauses"""
        sql = (
            "CREATE TABLE t ("
            "  col STRUCT<"
            "    foo: INT COMMENT 'first',"
            "    interval: STRING,"
            "    bar: DOUBLE COMMENT 'third'"
            "  >"
            ")"
        )
        result = parse_one(sql)
        fields = result.columns[0].struct_fields
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].comment, "first")
        self.assertIsNone(fields[1].comment)
        self.assertEqual(fields[2].comment, "third")


if __name__ == "__main__":
    unittest.main()
