from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from .ast import CreateTable, ColumnDef, StructField
from .tokenizer import tokenize, Token


class ParseError(Exception):
    pass


@dataclass
class Parser:
    tokens: List[Token]
    pos: int = 0
    read: str = "databricks"

    def cur(self) -> Token:
        return self.tokens[self.pos]

    def eat(self, kind: str, text: Optional[str] = None) -> Token:
        tok = self.cur()
        if tok.kind != kind:
            raise ParseError(f"Expected {kind}, got {tok.kind}:{tok.text}")
        if text is not None and tok.text != text:
            raise ParseError(f"Expected {text}, got {tok.text}")
        self.pos += 1
        return tok

    def maybe_eat(self, kind: str, text: Optional[str] = None) -> Optional[Token]:
        tok = self.cur()
        if tok.kind != kind:
            return None
        if text is not None and tok.text != text:
            return None
        self.pos += 1
        return tok

    def parse(self) -> CreateTable:
        self.eat("KW", "CREATE")
        self.eat("KW", "TABLE")
        # Accept either IDENT or KW as table name (Databricks ANSI compliance)
        table_tok = self.cur()
        if table_tok.kind not in ("IDENT", "KW"):
            raise ParseError(f"Expected table name, got {table_tok.kind}:{table_tok.text}")
        table = self.eat(table_tok.kind).text

        self.eat("(", "(")
        columns: List[ColumnDef] = [self.parse_column()]

        # supports optional additional columns separated by commas
        while self.maybe_eat(",", ","):
            columns.append(self.parse_column())

        self.eat(")", ")")
        self.eat("EOF")
        return CreateTable(table_name=table, columns=columns)

    def parse_column(self) -> ColumnDef:
        # Accept either IDENT or KW as column name (Databricks ANSI compliance)
        col_tok = self.cur()
        if col_tok.kind not in ("IDENT", "KW"):
            raise ParseError(f"Expected column name, got {col_tok.kind}:{col_tok.text}")
        name = self.eat(col_tok.kind).text
        
        # Expect STRUCT keyword (could be KW or IDENT after removing from KEYWORDS)
        struct_tok = self.cur()
        if struct_tok.text != "STRUCT":
            raise ParseError(f"Expected STRUCT, got {struct_tok.text}")
        self.eat(struct_tok.kind)
        self.eat("<", "<")

        fields: List[StructField] = [self.parse_struct_field()]

        while self.maybe_eat(",", ","):
            fields.append(self.parse_struct_field())

        self.eat(">", ">")
        return ColumnDef(name=name, struct_fields=fields)

    def parse_struct_field(self) -> StructField:
        tok = self.cur()

        # field name: accept either IDENT or KW (Databricks ANSI compliance)
        if tok.kind in ("IDENT", "KW"):
            field_name = self.eat(tok.kind).text
        else:
            raise ParseError(f"Expected struct field name, got {tok.kind}:{tok.text}")

        self.eat(":", ":")

        # type name
        type_tok = self.cur()
        if type_tok.kind not in ("KW", "IDENT"):
            raise ParseError("Expected type name")
        type_name = self.eat(type_tok.kind).text

        # optional comment (check for text "COMMENT" regardless of token kind)
        comment = None
        comment_tok = self.cur()
        if comment_tok.text == "COMMENT":
            self.eat(comment_tok.kind)
            # comment literal
            comment = self.eat("STRING").text

        return StructField(name=field_name, type_name=type_name, comment=comment)


def parse_one(sql: str, read: str = "databricks") -> CreateTable:
    tokens = tokenize(sql)
    # dialect hint passed through
    return Parser(tokens=tokens, read=read).parse()
