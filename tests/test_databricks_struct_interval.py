import unittest

from mini_sqlglot.parser import parse_one as parse_create_table


class TestDatabricksStructInterval(unittest.TestCase):
    """Regression tests for keywords as identifiers"""

    def test_unquoted_interval_table_name(self):
        sql = """
        CREATE TABLE interval (
            col STRUCT<foo: INT>
        )
        """
        parse_create_table(sql)  # should not raise

    def test_unquoted_interval_column_name(self):
        sql = """
        CREATE TABLE t (
            interval STRUCT<foo: INT>
        )
        """
        parse_create_table(sql)

    def test_unquoted_interval_struct_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: INT, foo: STRING>
        )
        """
        parse_create_table(sql)

    def test_unquoted_comment_struct_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<comment: INT, foo: STRING>
        )
        """
        parse_create_table(sql)

    def test_unquoted_struct_struct_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<struct: INT, foo: STRING>
        )
        """
        parse_create_table(sql)

    def test_struct_field_with_comment_clause(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: DOUBLE COMMENT 'desc'>
        )
        """
        parse_create_table(sql)

    # quoted identifiers
    def test_quoted_interval_table_name(self):
        sql = """
        CREATE TABLE `interval` (
            col STRUCT<foo: INT>
        )
        """
        parse_create_table(sql)

    def test_quoted_interval_column_name(self):
        sql = """
        CREATE TABLE t (
            `interval` STRUCT<foo: INT>
        )
        """
        parse_create_table(sql)

    def test_quoted_interval_struct_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<`interval`: INT>
        )
        """
        parse_create_table(sql)

    def test_quoted_interval_struct_field_comment(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<`interval`: DOUBLE COMMENT 'aaa'>
        )
        """
        parse_create_table(sql)

    # invalid syntax: should raise ParseError
    def test_missing_colon(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval INT>
        )
        """
        with self.assertRaises(Exception):
            parse_create_table(sql)

    def test_missing_type(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: >
        )
        """
        with self.assertRaises(Exception):
            parse_create_table(sql)

    def test_unclosed_struct(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: INT
        )
        """
        with self.assertRaises(Exception):
            parse_create_table(sql)


if __name__ == "__main__":
    unittest.main()
