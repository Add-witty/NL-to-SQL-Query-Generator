from pathlib import Path
from typing import Union

import pandas as pd

from app.extractors.base import BaseSchemaExtractor
from app.models.schema import Column, Schema, SourceType, Table

_DTYPE_MAP = {
    "int64": "integer",
    "float64": "float",
    "bool": "boolean",
    "object": "text",
    "datetime64[ns]": "datetime",
}


class CSVSchemaExtractor(BaseSchemaExtractor):
    """
    Extracts a single-table Schema from a CSV file (see
    supported_format.md: "CSV - Single table").

    CSV files carry no primary/foreign key metadata, so every column
    is extracted with is_primary_key=False and is_foreign_key=False.
    Data types are inferred from the pandas dtype of each column.
    """

    def extract(self, source: Union[str, Path]) -> Schema:
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"CSV file not found: {path}")

        if path.suffix.lower() != ".csv":
            raise ValueError(f"Expected a .csv file, got: {path.suffix}")

        dataframe = pd.read_csv(path)

        columns = [
            Column(
                name=column_name,
                data_type=self._map_dtype(dataframe[column_name].dtype),
            )
            for column_name in dataframe.columns
        ]

        table = Table(name=path.stem, columns=columns)

        return Schema(source_type=SourceType.CSV, tables=[table])

    @staticmethod
    def _map_dtype(dtype) -> str:
        return _DTYPE_MAP.get(str(dtype), "text")
