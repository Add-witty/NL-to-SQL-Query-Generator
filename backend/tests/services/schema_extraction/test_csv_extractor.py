import textwrap

import pytest

from app.models.schema import DataType, SourceType
from app.services.schema_extraction.csv_extractor import (
    CSVSchemaExtractionError,
    CSVSchemaExtractor,
)


def _write_csv(tmp_path, filename: str, content: str):
    path = tmp_path / filename
    path.write_text(textwrap.dedent(content).strip() + "\n")
    return str(path)


@pytest.fixture
def extractor():
    return CSVSchemaExtractor()


class TestTableNaming:
    def test_table_name_derived_from_filename(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "customers.csv", "id,name\n1,Alice")
        schema = extractor.extract(path)
        assert schema.tables[0].name == "customers"

    def test_table_name_sanitized(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "2024 sales-report.csv", "id,amount\n1,10")
        schema = extractor.extract(path)
        # Leading digit prefixed, spaces/hyphens replaced with underscores.
        assert schema.tables[0].name == "t_2024_sales_report"


class TestDataTypeInference:
    def test_integer_column(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "id\n1\n2\n3")
        schema = extractor.extract(path)
        assert schema.tables[0].columns[0].data_type == DataType.INTEGER

    def test_float_column(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "price\n9.99\n10.5\n3.0")
        schema = extractor.extract(path)
        assert schema.tables[0].columns[0].data_type == DataType.FLOAT

    def test_boolean_column(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "is_active\nTrue\nFalse\nTrue")
        schema = extractor.extract(path)
        assert schema.tables[0].columns[0].data_type == DataType.BOOLEAN

    def test_text_column(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "name\nAlice\nBob\nCarol")
        schema = extractor.extract(path)
        assert schema.tables[0].columns[0].data_type == DataType.TEXT

    def test_datetime_column(self, tmp_path, extractor):
        path = _write_csv(
            tmp_path,
            "t.csv",
            "created_at\n2024-01-01\n2024-02-15\n2024-03-30",
        )
        schema = extractor.extract(path)
        assert schema.tables[0].columns[0].data_type == DataType.DATETIME

    def test_mixed_text_with_some_dates_is_still_text(self, tmp_path, extractor):
        # Fewer than the detection threshold of values parse as dates,
        # so this should NOT be misclassified as DATETIME.
        path = _write_csv(
            tmp_path,
            "t.csv",
            "notes\n2024-01-01\nnot a date\nalso not a date\nstill not\nnope",
        )
        schema = extractor.extract(path)
        assert schema.tables[0].columns[0].data_type == DataType.TEXT

    def test_entirely_null_column_is_unknown(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "empty_col\n,\n,\n")
        # Force a column that's fully empty.
        path = _write_csv(tmp_path, "t.csv", "id,empty_col\n1,\n2,\n3,")
        schema = extractor.extract(path)
        empty_col = next(
            c for c in schema.tables[0].columns if c.name == "empty_col"
        )
        assert empty_col.data_type == DataType.UNKNOWN


class TestMultipleColumns:
    def test_extracts_all_columns_in_order(self, tmp_path, extractor):
        path = _write_csv(
            tmp_path,
            "orders.csv",
            "id,customer_name,total,placed_at,is_paid\n"
            "1,Alice,19.99,2024-01-01,True\n"
            "2,Bob,45.00,2024-01-02,False",
        )
        schema = extractor.extract(path)
        table = schema.tables[0]
        names = [c.name for c in table.columns]
        assert names == ["id", "customer_name", "total", "placed_at", "is_paid"]

        by_name = {c.name: c.data_type for c in table.columns}
        assert by_name["id"] == DataType.INTEGER
        assert by_name["customer_name"] == DataType.TEXT
        assert by_name["total"] == DataType.FLOAT
        assert by_name["placed_at"] == DataType.DATETIME
        assert by_name["is_paid"] == DataType.BOOLEAN


class TestNeverInventsKeysOrRelationships:
    def test_no_primary_or_foreign_keys_are_inferred(self, tmp_path, extractor):
        # Even a column named 'id' must NOT be assumed to be a primary key.
        path = _write_csv(
            tmp_path,
            "t.csv",
            "id,customer_id,name\n1,10,Alice\n2,11,Bob",
        )
        schema = extractor.extract(path)
        for column in schema.tables[0].columns:
            assert column.is_primary_key is False
            assert column.is_foreign_key is False
            assert column.references is None


class TestSchemaShape:
    def test_source_type_is_csv(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "id\n1")
        schema = extractor.extract(path)
        assert schema.source_type == SourceType.CSV

    def test_single_table_only(self, tmp_path, extractor):
        path = _write_csv(tmp_path, "t.csv", "id\n1")
        schema = extractor.extract(path)
        assert len(schema.tables) == 1


class TestErrorHandling:
    def test_empty_file_raises(self, tmp_path, extractor):
        path = tmp_path / "empty.csv"
        path.write_text("")
        with pytest.raises(CSVSchemaExtractionError):
            extractor.extract(str(path))

    def test_missing_file_raises(self, extractor):
        with pytest.raises(FileNotFoundError):
            extractor.extract("/does/not/exist.csv")
