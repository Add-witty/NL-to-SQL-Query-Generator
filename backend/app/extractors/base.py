from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union

from app.models.schema import Schema


class BaseSchemaExtractor(ABC):
    """
    Common interface every schema extractor must implement (CSV today;
    XLSX, SQLite, and SQL in later phases).

    Guarantees that the Prompt Builder and downstream services can
    consume a single, source-agnostic Schema object regardless of the
    original file format (see decisions.md).
    """

    @abstractmethod
    def extract(self, source: Union[str, Path]) -> Schema:
        """
        Read the given source file and return a populated Schema.

        Args:
            source: Path to the file to extract the schema from.

        Returns:
            Schema: normalized schema representation.
        """
        raise NotImplementedError
