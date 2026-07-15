# Backend — Natural Language to SQL Generator

## Current status

- FastAPI app with a `/health` endpoint
- Internal `Schema` model (source-agnostic, per `decisions.md`)
- `BaseSchemaExtractor` interface
- `CSVSchemaExtractor` implementation (single-table CSV support)
- Unit tests for the above

Not yet implemented (future roadmap): XLSX/SQLite/SQL extractors,
upload endpoint, Prompt Builder, LLM integration, SQL validation.

## Folder structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # App settings
│   ├── routers/
│   │   ├── __init__.py
│   │   └── health.py        # GET /health
│   ├── models/
│   │   ├── __init__.py
│   │   └── schema.py        # Schema, Table, Column, SourceType
│   └── extractors/
│       ├── __init__.py
│       ├── base.py          # BaseSchemaExtractor interface
│       └── csv_extractor.py # CSV -> Schema
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   └── test_csv_extractor.py
├── requirements.txt
├── pytest.ini
└── README.md
```

## Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Run the backend

```bash
uvicorn app.main:app --reload
```

Verify:

```bash
curl http://127.0.0.1:8000/health
# {"status": "ok"}
```

## Run tests

```bash
pytest
```
