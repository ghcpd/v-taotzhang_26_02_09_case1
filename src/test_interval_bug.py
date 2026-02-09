import unittest
from mini_sqlglot.parser import parse_one as parse_create_table

class TestStructIntervalField(unittest.TestCase):
    """Test cases to expose bugs with 'interval' and other keyword handling"""
    
    def test_struct_with_interval_field_unquoted(self):
        """Bug: unquoted 'interval' as struct field name fails"""
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: INT, foo: STRING>
        )
        """
        # This should parse successfully per Databricks ANSI compliance
        try:
            result = parse_create_table(sql)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Parsing failed for unquoted interval field: {e}")

    def test_struct_with_interval_field_quoted(self):
        """Control test: quoted 'interval' should work"""
        sql = """
        CREATE TABLE t (
            col STRUCT<`interval`: INT, foo: STRING>
        )
        """
        try:
            result = parse_create_table(sql)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Parsing failed for quoted interval field: {e}")

    def test_column_name_interval_unquoted(self):
        """Bug: unquoted 'interval' as column name fails"""
        sql = """
        CREATE TABLE t (
            interval STRUCT<foo: INT>
        )
        """
        try:
            result = parse_create_table(sql)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Parsing failed for unquoted interval as column name: {e}")

    def test_table_name_interval_unquoted(self):
        """Bug: unquoted 'interval' as table name fails"""
        sql = """
        CREATE TABLE interval (
            col STRUCT<foo: INT>
        )
        """
        try:
            result = parse_create_table(sql)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Parsing failed for unquoted interval as table name: {e}")

    def test_struct_with_comment_field_unquoted(self):
        """Bug: unquoted 'comment' as struct field name fails"""
        sql = """
        CREATE TABLE t (
            col STRUCT<comment: INT, foo: STRING>
        )
        """
        try:
            result = parse_create_table(sql)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Parsing failed for unquoted comment field: {e}")

    def test_struct_with_struct_field_unquoted(self):
        """Bug: unquoted 'struct' as struct field name fails"""
        sql = """
        CREATE TABLE t (
            col STRUCT<struct: INT, foo: STRING>
        )
        """
        try:
            result = parse_create_table(sql)
            self.assertIsNotNone(result)
        except Exception as e:
            self.fail(f"Parsing failed for unquoted struct field: {e}")

if __name__ == "__main__":
    unittest.main()
