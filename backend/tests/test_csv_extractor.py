import pandas as pd
import pytest

from app.extractors.csv_extractor import CSVSchemaExtractor
from app.models.schema import SourceType


@pytest.fixture
def sample_csv(tmp_path):
    csv_path = tmp_path / "customers.csv"
    dataframe = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Carol"],
            "balance": [10.5, 20.0, 30.75],
            "is_active": [True, False, True],
        }
    )
    dataframe.to_csv(csv_path, index=False)
    return csv_path


def test_extract_returns_schema_with_correct_source_type(sample_csv):
    extractor = CSVSchemaExtractor()

    schema = extractor.extract(sample_csv)

    assert schema.source_type == SourceType.CSV


def test_extract_returns_single_table_named_after_file(sample_csv):
    extractor = CSVSchemaExtractor()

    schema = extractor.extract(sample_csv)

    assert len(schema.tables) == 1
    assert schema.tables[0].name == "customers"


def test_extract_infers_column_names_and_types(sample_csv):
    extractor = CSVSchemaExtractor()

    schema = extractor.extract(sample_csv)
    columns = {col.name: col.data_type for col in schema.tables[0].columns}

    assert columns["id"] == "INTEGER"
    assert columns["name"] == "TEXT"
    assert columns["balance"] == "FLOAT"
    assert columns["is_active"] == "BOOLEAN"


def test_extract_columns_have_no_key_metadata(sample_csv):
    """CSV has no PK/FK metadata, so extractor must not invent any."""
    extractor = CSVSchemaExtractor()

    schema = extractor.extract(sample_csv)

    for column in schema.tables[0].columns:
        assert column.is_primary_key is False
        assert column.is_foreign_key is False
        assert column.references is None


def test_extract_raises_for_missing_file(tmp_path):
    extractor = CSVSchemaExtractor()
    missing_path = tmp_path / "does_not_exist.csv"

    with pytest.raises(FileNotFoundError):
        extractor.extract(missing_path)


def test_extract_raises_for_wrong_extension(tmp_path):
    extractor = CSVSchemaExtractor()
    wrong_file = tmp_path / "data.txt"
    wrong_file.write_text("id,name\n1,Alice")

    with pytest.raises(ValueError):
        extractor.extract(wrong_file)
