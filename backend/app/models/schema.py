"""
Internal Schema model.

This is the single, source-agnostic representation produced by every
schema extractor (CSV, XLSX, SQLite, SQL dump). Downstream modules
(Prompt Builder, Validator, LLM Service) depend only on this model and
never on the original file format.

See decisions.md: "Use a single internal Schema model regardless of
input source."
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class DataType(str, Enum):
    """Normalized data types, independent of source-specific type systems."""

    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    BOOLEAN = "BOOLEAN"
    DATETIME = "DATETIME"
    TEXT = "TEXT"
    UNKNOWN = "UNKNOWN"


class SourceType(str, Enum):
    """Where the schema was extracted from."""

    CSV = "CSV"
    XLSX = "XLSX"
    SQLITE = "SQLITE"
    SQL = "SQL"


class Column(BaseModel):
    """A single column within a table."""

    name: str
    data_type: DataType
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references: Optional[str] = Field(
        default=None,
        description=(
            "For foreign key columns, the referenced table/column, "
            "e.g. 'orders.id'. None if not a foreign key or if the "
            "source format cannot express relationships (e.g. CSV)."
        ),
    )


class Table(BaseModel):
    """A single table, made up of columns."""

    name: str
    columns: list[Column]


class Schema(BaseModel):
    """The full extracted schema for one uploaded source."""

    source_type: SourceType
    tables: list[Table]
