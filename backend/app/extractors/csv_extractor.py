"""
CSV Schema Extractor.

Reads a single CSV file and infers a Schema (one Table) from its
header and column dtypes. CSV files carry no primary/foreign key
metadata, so those fields are intentionally left as False / empty
rather than guessed - we never invent constraints that aren't in
the source data.
"""

import io
import re
from pathlib import Path
from typing import BinaryIO, Union

import pandas as pd

from app.extractors.base import BaseSchemaExtractor
from app.models.schema import Column, Schema, Table

# Map pandas dtypes to a small, generic set of SQL-ish types.
# Anything unrecognized falls back to TEXT rather than raising,
# since column typing should never block schema extraction.
_DTYPE_MAP = {
    "int64": "INTEGER",
    "int32": "INTEGER",
    "float64": "FLOAT",
    "float32": "FLOAT",
    "bool": "BOOLEAN",
    "datetime64[ns]": "DATETIME",
    "object": "TEXT",
}


def sanitize_table_name(filename: str) -> str:
    """Derive a safe SQL-identifier-like table name from a filename."""
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    stem = stem.strip().replace(" ", "_")
    sanitized = re.sub(r"[^A-Za-z0-9_]", "_", stem)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")

    if not sanitized:
        sanitized = "uploaded_table"
    if sanitized[0].isdigit():
        sanitized = f"table_{sanitized}"

    return sanitized


def _map_dtype(dtype) -> str:
    return _DTYPE_MAP.get(str(dtype), "TEXT")


def extract_schema_from_csv(
    file_obj: Union[BinaryIO, io.BytesIO], table_name: str
) -> Schema:
    """
    Parse a CSV file-like object and return a Schema with a single Table.

    Raises ValueError on empty files or unparseable CSV content, so the
    API layer can translate that into a clean 400 response.
    """
    try:
        df = pd.read_csv(file_obj)
    except pd.errors.EmptyDataError as exc:
        raise ValueError("The CSV file is empty or has no columns.") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Could not parse CSV file: {exc}") from exc

    if len(df.columns) == 0:
        raise ValueError("The CSV file has no columns.")

    columns = [
        Column(name=str(col), data_type=_map_dtype(df[col].dtype))
        for col in df.columns
    ]

    table = Table(name=table_name, columns=columns, foreign_keys=[])
    return Schema(source_type="csv", tables=[table])


class CSVSchemaExtractor(BaseSchemaExtractor):
    def extract(self, source: Union[str, Path]) -> Schema:
        file_path = Path(source)

        if file_path.suffix.lower() != ".csv":
            raise ValueError("Only .csv files are supported by this extractor.")
        if not file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {source}")

        with file_path.open("rb") as file_obj:
            return extract_schema_from_csv(file_obj, sanitize_table_name(file_path.name))
