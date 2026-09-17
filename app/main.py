"""
Entry point for the FastAPI service.
Run with: uvicorn app.main:app --reload
"""
from fastapi import FastAPI
from app.routers import contracts, buyers, stats

app = FastAPI(
    title="Procurement Data API",
    description="Read-only API over Slovak public procurement data, backed by Snowflake.",
    version="0.1.0",
)

app.include_router(contracts.router)
app.include_router(buyers.router)
app.include_router(stats.router)


@app.get("/health", tags=["health"])
def health():
    """Basic liveness check."""
    return {"status": "ok"}


@app.get("/", tags=["health"])
def root():
    return {
        "message": "Procurement Data API is running.",
        "docs": "/docs",
    }
