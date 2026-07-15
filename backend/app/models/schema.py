from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class SourceType(str, Enum):
    """Origin of the extracted schema."""

    CSV = "csv"
    XLSX = "xlsx"
    SQLITE = "sqlite"
    SQL = "sql"


class ForeignKeyReference(BaseModel):
    """Points to the table/column a foreign key references."""

    table: str
    column: str


class Column(BaseModel):
    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: Optional[ForeignKeyReference] = None


class Table(BaseModel):
    name: str
    columns: List[Column]


class Schema(BaseModel):
    """
    Single internal representation produced by every schema extractor
    (CSV, XLSX, SQLite, SQL), regardless of input source.

    See decisions.md: "Use a single internal Schema model regardless
    of input source" so the Prompt Builder and Validator stay
    independent of how the schema was originally obtained.
    """

    source_type: SourceType
    tables: List[Table]
