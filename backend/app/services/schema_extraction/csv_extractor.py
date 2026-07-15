"""
CSV schema extractor.

A CSV file has no explicit schema, so this extractor:
  - Treats the whole file as exactly one table.
  - Uses the filename (without extension) as the table name.
  - Infers each column's data type from its values via pandas.

Important limitation (by design, not an oversight):
A CSV carries no primary key / foreign key / relationship metadata.
This extractor never guesses at keys (e.g. "a column named 'id' must
be a primary key") because that would be hallucinated schema
information. Every column is emitted with is_primary_key=False,
is_foreign_key=False, references=None.
"""

import os
import re

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_float_dtype,
    is_integer_dtype,
)

from app.models.schema import Column, DataType, Schema, SourceType, Table
from app.services.schema_extraction.base import SchemaExtractor

# If this fraction (or more) of an object column's non-null values parse
# as dates, the column is classified as DATETIME rather than TEXT.
_DATETIME_DETECTION_THRESHOLD = 0.9

_INVALID_NAME_CHARS = re.compile(r"[^A-Za-z0-9_]+")


class CSVSchemaExtractionError(ValueError):
    """Raised when a CSV file cannot be turned into a valid Schema."""


class CSVSchemaExtractor(SchemaExtractor):
    """Extracts a single-table Schema from a CSV file."""

    def extract(self, file_path: str) -> Schema:
        table_name = self._derive_table_name(file_path)

        try:
            df = pd.read_csv(file_path)
        except pd.errors.EmptyDataError as exc:
            raise CSVSchemaExtractionError(
                f"'{file_path}' is empty; no columns could be read."
            ) from exc
        except pd.errors.ParserError as exc:
            raise CSVSchemaExtractionError(
                f"'{file_path}' could not be parsed as CSV: {exc}"
            ) from exc

        if len(df.columns) == 0:
            raise CSVSchemaExtractionError(
                f"'{file_path}' has no columns; cannot extract a schema."
            )

        columns = [
            Column(
                name=str(column_name),
                data_type=self._infer_data_type(df[column_name]),
                is_primary_key=False,
                is_foreign_key=False,
                references=None,
            )
            for column_name in df.columns
        ]

        table = Table(name=table_name, columns=columns)
        return Schema(source_type=SourceType.CSV, tables=[table])

    @staticmethod
    def _derive_table_name(file_path: str) -> str:
        """Derive a SQL-safe table name from the CSV filename."""
        stem = os.path.splitext(os.path.basename(file_path))[0]
        sanitized = _INVALID_NAME_CHARS.sub("_", stem).strip("_")
        if not sanitized:
            raise CSVSchemaExtractionError(
                f"Could not derive a valid table name from '{file_path}'."
            )
        if sanitized[0].isdigit():
            sanitized = f"t_{sanitized}"
        return sanitized

    @staticmethod
    def _infer_data_type(series: pd.Series) -> DataType:
        """Map a pandas Series' dtype/content to an internal DataType."""
        # A column with no values at all carries no type information.
        # Note: pandas assigns such columns a float64 dtype by
        # convention, so this check must run before the dtype checks
        # below, or an all-null column would be misreported as FLOAT.
        if series.isna().all():
            return DataType.UNKNOWN

        if is_bool_dtype(series):
            return DataType.BOOLEAN
        if is_integer_dtype(series):
            return DataType.INTEGER
        if is_float_dtype(series):
            return DataType.FLOAT
        if is_datetime64_any_dtype(series):
            return DataType.DATETIME

        # Object / string columns: attempt datetime detection before
        # falling back to TEXT.
        non_null = series.dropna()
        if len(non_null) == 0:
            return DataType.UNKNOWN

        parsed = pd.to_datetime(non_null, errors="coerce", format="mixed")
        parse_ratio = parsed.notna().mean()
        if parse_ratio >= _DATETIME_DETECTION_THRESHOLD:
            return DataType.DATETIME

        return DataType.TEXT
