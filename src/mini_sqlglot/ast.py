from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class StructField:
    name: str
    type_name: str
    comment: Optional[str] = None


@dataclass(frozen=True)
class ColumnDef:
    name: str
    struct_fields: List[StructField]


@dataclass(frozen=True)
class CreateTable:
    table_name: str
    columns: List[ColumnDef]
