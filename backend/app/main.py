from fastapi import FastAPI

from app.api.upload import router as upload_router

app = FastAPI(title="Natural Language to SQL Generator")

app.include_router(upload_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
