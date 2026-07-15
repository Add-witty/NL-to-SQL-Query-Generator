"""
Common interface for all schema extractors.

Every concrete extractor (CSV, XLSX, SQLite, SQL — later phases) must
implement `extract` and return the shared internal `Schema` model.
This keeps the Prompt Builder and everything downstream agnostic to
the original input format (see architecture.md).
"""

from abc import ABC, abstractmethod

from app.models.schema import Schema


class SchemaExtractor(ABC):
    """Base interface every schema extractor must implement."""

    @abstractmethod
    def extract(self, file_path: str) -> Schema:
        """
        Read the file at `file_path` and return its Schema.

        Implementations must never invent tables, columns, or
        constraints that cannot be determined from the source data.
        """
        raise NotImplementedError
