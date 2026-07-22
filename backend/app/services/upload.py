import io

from fastapi import UploadFile

from app.extractors.csv_extractor import extract_schema_from_csv, sanitize_table_name
from app.models.schema import Schema

ALLOWED_EXTENSION = ".csv"
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


class UploadValidationError(ValueError):
    pass


class SchemaExtractionError(ValueError):
    pass


def _validate_extension(filename: str | None) -> None:
    if not filename or not filename.lower().endswith(ALLOWED_EXTENSION):
        raise UploadValidationError(
            "Only .csv files are supported by this endpoint."
        )


def _validate_size(contents: bytes) -> None:
    if len(contents) == 0:
        raise UploadValidationError("Uploaded file is empty.")
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise UploadValidationError(
            f"File exceeds the {MAX_FILE_SIZE_MB}MB upload limit."
        )


async def extract_schema_from_uploaded_csv(file: UploadFile) -> Schema:
    _validate_extension(file.filename)

    contents = await file.read()
    _validate_size(contents)

    table_name = sanitize_table_name(file.filename)

    try:
        return extract_schema_from_csv(io.BytesIO(contents), table_name)
    except ValueError as exc:
        raise SchemaExtractionError(str(exc)) from exc
