from __future__ import annotations
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class Token:
    kind: str
    text: str


# Intentionally small keyword set for the exercise
KEYWORDS = {
    "CREATE", "TABLE", "STRUCT", "COMMENT", "DOUBLE",
    "INTERVAL",
}


def tokenize(sql: str) -> List[Token]:
    tokens: List[Token] = []
    i = 0
    n = len(sql)

    while i < n:
        ch = sql[i]

        if ch.isspace():
            i += 1
            continue

        if ch in "(),:<>":
            tokens.append(Token(kind=ch, text=ch))
            i += 1
            continue

        if ch == "`":
            # backticked identifier
            j = i + 1
            while j < n and sql[j] != "`":
                j += 1
            inner = sql[i + 1 : j]
            tokens.append(Token(kind="IDENT", text=inner))
            i = j + 1
            continue

        if ch == "'":
            # single-quoted string (no escapes handled intentionally)
            j = i + 1
            while j < n and sql[j] != "'":
                j += 1
            lit = sql[i + 1 : j]
            tokens.append(Token(kind="STRING", text=lit))
            i = j + 1
            continue

        # bare word
        j = i
        while j < n and (sql[j].isalnum() or sql[j] == "_"):
            j += 1
        word = sql[i:j]
        upper = word.upper()

        if upper in KEYWORDS:
            tokens.append(Token(kind="KW", text=upper))
        else:
            tokens.append(Token(kind="IDENT", text=word))

        i = j

    tokens.append(Token(kind="EOF", text=""))
    return tokens
