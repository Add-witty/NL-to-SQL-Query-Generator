"""
Upload endpoint.

Scope (deliberately narrow): CSV only. XLSX, SQLite, SQL dump upload,
prompt building, and LLM integration are separate, later tasks.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.schema import Schema
from app.services.upload import (
    SchemaExtractionError,
    UploadValidationError,
    extract_schema_from_uploaded_csv,
)

router = APIRouter()


@router.post("/upload", response_model=Schema)
async def upload_csv(file: UploadFile = File(...)) -> Schema:
    try:
        return await extract_schema_from_uploaded_csv(file)
    except UploadValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except SchemaExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
