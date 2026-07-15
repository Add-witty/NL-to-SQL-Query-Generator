import io

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _csv_file(content: str, filename: str = "employees.csv"):
    return {"file": (filename, io.BytesIO(content.encode("utf-8")), "text/csv")}


def test_upload_valid_csv_returns_schema():
    content = "id,name,salary,hired_at\n1,Alice,75000.50,2020-01-01\n2,Bob,68000,2021-03-15\n"
    response = client.post("/upload", files=_csv_file(content, "employees.csv"))

    assert response.status_code == 200
    body = response.json()

    assert body["source_type"] == "csv"
    assert len(body["tables"]) == 1

    table = body["tables"][0]
    assert table["name"] == "employees"
    assert table["foreign_keys"] == []

    columns = {c["name"]: c for c in table["columns"]}
    assert set(columns.keys()) == {"id", "name", "salary", "hired_at"}
    assert columns["id"]["data_type"] == "INTEGER"
    assert columns["name"]["data_type"] == "TEXT"
    assert columns["salary"]["data_type"] == "FLOAT"

    # CSV has no constraint metadata - never invent primary keys
    assert all(c["is_primary_key"] is False for c in table["columns"])


def test_upload_sanitizes_table_name_from_filename():
    content = "col_a,col_b\n1,2\n"
    response = client.post("/upload", files=_csv_file(content, "2024 Sales Report!.csv"))

    assert response.status_code == 200
    table_name = response.json()["tables"][0]["name"]
    assert table_name == "table_2024_Sales_Report"


def test_upload_rejects_non_csv_extension():
    response = client.post(
        "/upload",
        files={"file": ("data.txt", io.BytesIO(b"col_a,col_b\n1,2\n"), "text/plain")},
    )

    assert response.status_code == 400
    assert "csv" in response.json()["detail"].lower()


def test_upload_rejects_empty_file():
    response = client.post("/upload", files=_csv_file("", "empty.csv"))

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_upload_rejects_csv_with_no_columns():
    # A CSV consisting solely of blank lines has no header/columns.
    response = client.post("/upload", files=_csv_file("\n\n\n", "blank.csv"))

    assert response.status_code == 400


def test_upload_rejects_file_exceeding_size_limit():
    # Build a CSV just over the 10MB limit.
    header = "col_a,col_b\n"
    row = "1,2\n"
    oversized_body = header + row * (11 * 1024 * 1024 // len(row))

    response = client.post("/upload", files=_csv_file(oversized_body, "big.csv"))

    assert response.status_code == 400
    assert "exceeds" in response.json()["detail"].lower()


def test_upload_missing_file_returns_422():
    response = client.post("/upload")
    assert response.status_code == 422
