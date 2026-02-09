import unittest
from mini_sqlglot.parser import parse_one as parse_create_table


class TestDatabricksIdentifierHandling(unittest.TestCase):
    """Comprehensive regression tests for Databricks identifier/keyword handling"""

    # Table name tests
    def test_table_name_interval_unquoted(self):
        """Unquoted 'interval' as table name should parse successfully"""
        sql = "CREATE TABLE interval (col STRUCT<foo: INT>)"
        result = parse_create_table(sql)
        self.assertEqual(result.table_name, "interval")
        self.assertEqual(len(result.columns), 1)

    def test_table_name_interval_quoted(self):
        """Quoted 'interval' as table name should still work"""
        sql = "CREATE TABLE `interval` (col STRUCT<foo: INT>)"
        result = parse_create_table(sql)
        self.assertEqual(result.table_name, "interval")

    # Column name tests
    def test_column_name_interval_unquoted(self):
        """Unquoted 'interval' as column name should parse successfully"""
        sql = "CREATE TABLE t (interval STRUCT<foo: INT>)"
        result = parse_create_table(sql)
        self.assertEqual(result.columns[0].name, "interval")

    def test_column_name_interval_quoted(self):
        """Quoted 'interval' as column name should still work"""
        sql = "CREATE TABLE t (`interval` STRUCT<foo: INT>)"
        result = parse_create_table(sql)
        self.assertEqual(result.columns[0].name, "interval")

    # Struct field name tests
    def test_struct_field_interval_unquoted(self):
        """Unquoted 'interval' as struct field name should parse successfully"""
        sql = "CREATE TABLE t (col STRUCT<interval: DOUBLE>)"
        result = parse_create_table(sql)
        self.assertEqual(result.columns[0].struct_fields[0].name, "interval")
        self.assertEqual(result.columns[0].struct_fields[0].type_name, "DOUBLE")

    def test_struct_field_interval_quoted(self):
        """Quoted 'interval' as struct field name should still work"""
        sql = "CREATE TABLE t (col STRUCT<`interval`: DOUBLE>)"
        result = parse_create_table(sql)
        self.assertEqual(result.columns[0].struct_fields[0].name, "interval")

    def test_struct_field_comment_unquoted(self):
        """Unquoted 'comment' as struct field name should parse successfully"""
        sql = "CREATE TABLE t (col STRUCT<comment: STRING>)"
        result = parse_create_table(sql)
        self.assertEqual(result.columns[0].struct_fields[0].name, "comment")
        self.assertEqual(result.columns[0].struct_fields[0].type_name, "STRING")

    def test_struct_field_struct_unquoted(self):
        """Unquoted 'struct' as struct field name should parse successfully"""
        sql = "CREATE TABLE t (col STRUCT<struct: INT>)"
        result = parse_create_table(sql)
        self.assertEqual(result.columns[0].struct_fields[0].name, "struct")
        self.assertEqual(result.columns[0].struct_fields[0].type_name, "INT")

    # Comment clause tests
    def test_struct_field_with_comment_clause(self):
        """Struct field with COMMENT clause using keyword identifier should work"""
        sql = "CREATE TABLE t (col STRUCT<interval: DOUBLE COMMENT 'description'>)"
        result = parse_create_table(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "interval")
        self.assertEqual(field.type_name, "DOUBLE")
        self.assertEqual(field.comment, "description")

    def test_struct_field_quoted_with_comment_clause(self):
        """Quoted identifier with COMMENT clause should still work"""
        sql = "CREATE TABLE t (col STRUCT<`interval`: DOUBLE COMMENT 'aaa'>)"
        result = parse_create_table(sql)
        field = result.columns[0].struct_fields[0]
        self.assertEqual(field.name, "interval")
        self.assertEqual(field.comment, "aaa")

    # Invalid syntax should still fail
    def test_invalid_struct_missing_colon(self):
        """Missing colon in struct field should fail"""
        sql = "CREATE TABLE t (col STRUCT<interval DOUBLE>)"
        with self.assertRaises(Exception):
            parse_create_table(sql)

    def test_invalid_struct_missing_type(self):
        """Missing type after colon should fail"""
        sql = "CREATE TABLE t (col STRUCT<interval:>)"
        with self.assertRaises(Exception):
            parse_create_table(sql)

    def test_invalid_struct_missing_close(self):
        """Missing closing > should fail"""
        sql = "CREATE TABLE t (col STRUCT<interval: INT)"
        with self.assertRaises(Exception):
            parse_create_table(sql)

    # Multiple fields
    def test_multiple_struct_fields_with_keywords(self):
        """Multiple struct fields using keyword identifiers"""
        sql = "CREATE TABLE t (col STRUCT<interval: INT, comment: STRING, struct: DOUBLE>)"
        result = parse_create_table(sql)
        fields = result.columns[0].struct_fields
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name, "interval")
        self.assertEqual(fields[1].name, "comment")
        self.assertEqual(fields[2].name, "struct")


if __name__ == "__main__":
    unittest.main()