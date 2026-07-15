"""
Upload endpoint.

Scope (deliberately narrow): CSV only. XLSX, SQLite, SQL dump upload,
prompt building, and LLM integration are separate, later tasks.
"""

import io

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.extractors.csv_extractor import extract_schema_from_csv, sanitize_table_name
from app.models.schema import Schema

router = APIRouter()

ALLOWED_EXTENSION = ".csv"
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload", response_model=Schema)
async def upload_csv(file: UploadFile = File(...)) -> Schema:
    _validate_extension(file.filename)

    contents = await file.read()
    _validate_size(contents)

    table_name = sanitize_table_name(file.filename)

    try:
        schema = extract_schema_from_csv(io.BytesIO(contents), table_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return schema


def _validate_extension(filename: str | None) -> None:
    if not filename or not filename.lower().endswith(ALLOWED_EXTENSION):
        raise HTTPException(
            status_code=400,
            detail="Only .csv files are supported by this endpoint.",
        )


def _validate_size(contents: bytes) -> None:
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds the {MAX_FILE_SIZE_MB}MB upload limit.",
        )
