import unittest
import sys, os

# ensure src directory is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from mini_sqlglot.parser import parse_one as parse_create_table


class TestDatabricksStructInterval(unittest.TestCase):
    def test_unquoted_interval_table(self):
        sql = """
        CREATE TABLE interval (
            col STRUCT<foo: INT>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_unquoted_interval_column(self):
        sql = """
        CREATE TABLE t (
            interval STRUCT<foo: INT>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_unquoted_interval_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: DOUBLE>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_unquoted_comment_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<comment: STRING>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_unquoted_struct_field(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<struct: INT>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_interval_field_with_comment(self):
        sql = """
        CREATE TABLE t (
            col STRUCT<interval: DOUBLE COMMENT 'description'>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_quoted_identifiers(self):
        sql = """
        CREATE TABLE `interval` (
            `interval` STRUCT<`interval`: DOUBLE COMMENT 'aaa'>
        )
        """
        self.assertIsNotNone(parse_create_table(sql))

    def test_invalid_syntax(self):
        cases = [
            """
            CREATE TABLE t (
                col STRUCT<foo INT>
            )
            """,
            """
            CREATE TABLE t (
                col STRUCT<foo: INT
            )
            """,
            """
            CREATE TABLE t (
                col STRUCT<foo: >
            )
            """
        ]
        for sql in cases:
            with self.assertRaises(Exception):
                parse_create_table(sql)


if __name__ == "__main__":
    unittest.main()
