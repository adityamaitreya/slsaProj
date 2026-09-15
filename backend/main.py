"""
FastAPI application entry point for the SLSA Provenance Backend.

This is the REST API that sits in front of the storage layer.
The same API works with both PostgreSQL and Blockchain+IPFS backends
because it only talks to the ProvenanceStore interface.

Endpoints:
    POST /provenance          → store a new provenance record
    GET  /provenance/{digest} → retrieve by artifact digest
    POST /verify/{digest}     → verify integrity of stored provenance
    GET  /health              → backend health check
    GET  /                    → API info
"""

import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from models.provenance import (
    ProvenanceRecord, StoreResult, VerificationResult, VerificationStatus
)
from storage.base import (
    ProvenanceStore, RecordNotFoundError, DuplicateRecordError, StorageError
)
from storage.postgres_store import PostgreSQLStore

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Application startup and shutdown ─────────────────────────────────────────

store: ProvenanceStore = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Runs on startup and shutdown.
    Initialises the storage backend based on STORAGE_BACKEND env var.
    """
    global store

    backend = os.getenv("STORAGE_BACKEND", "postgresql")
    logger.info(f"Starting SLSA Provenance API with backend: {backend}")

    if backend == "postgresql":
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            raise RuntimeError("DATABASE_URL environment variable not set")
        store = PostgreSQLStore(db_url)
        logger.info("PostgreSQL store initialised")
    else:
        raise RuntimeError(f"Unknown backend: {backend}. Use 'postgresql' or 'blockchain_ipfs'")

    yield  # API runs here

    logger.info("Shutting down SLSA Provenance API")

# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="SLSA Provenance API",
    description="""
REST API for storing and verifying software supply chain provenance.

Supports two interchangeable storage backends:
- **PostgreSQL** (System B — Centralized)
- **Blockchain + IPFS** (System A — Decentralized, Phase B)

Part of the SLSA supply chain provenance verification research project.
    """,
    version="1.0.0",
    lifespan=lifespan
)

# Allow React dashboard to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request/Response models ───────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    backend: str
    database_connected: bool
    environment: str

class APIInfo(BaseModel):
    name: str
    version: str
    backend: str
    endpoints: list

# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/", response_model=APIInfo, tags=["Info"])
def root():
    """API information and available endpoints."""
    return APIInfo(
        name="SLSA Provenance API",
        version="1.0.0",
        backend=os.getenv("STORAGE_BACKEND", "postgresql"),
        endpoints=[
            "GET  /              → API info",
            "GET  /health        → Health check",
            "POST /provenance    → Store provenance record",
            "GET  /provenance/{digest} → Retrieve provenance",
            "POST /verify/{digest}     → Verify artifact integrity",
        ]
    )

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """
    Check if the API and storage backend are healthy.
    Used by Docker health checks and monitoring.
    """
    db_healthy = store.health_check() if store else False
    return HealthResponse(
        status="healthy" if db_healthy else "degraded",
        backend=os.getenv("STORAGE_BACKEND", "postgresql"),
        database_connected=db_healthy,
        environment=os.getenv("ENVIRONMENT", "development")
    )

@app.post(
    "/provenance",
    response_model=StoreResult,
    status_code=status.HTTP_201_CREATED,
    tags=["Provenance"]
)
def store_provenance(record: ProvenanceRecord):
    """
    Store a new provenance record.

    Called by the CI/CD pipeline after each build to register
    the artifact's provenance package (SLSA + SBOM + signature).

    Returns 201 Created on success.
    Returns 409 Conflict if the digest already exists.
    """
    try:
        result = store.store(record)
        logger.info(f"Stored provenance for {record.artifact_digest[:20]}...")
        return result
    except DuplicateRecordError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Provenance record already exists: {str(e)}"
        )
    except StorageError as e:
        logger.error(f"Storage error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage error: {str(e)}"
        )

@app.get(
    "/provenance/{artifact_digest:path}",
    response_model=ProvenanceRecord,
    tags=["Provenance"]
)
def get_provenance(artifact_digest: str):
    """
    Retrieve a provenance record by artifact digest.

    The digest format is sha256:abc123...
    Use :path so FastAPI handles the colon correctly.

    Returns 404 if no record exists for this digest.
    """
    try:
        record = store.retrieve(artifact_digest)
        return record
    except RecordNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No provenance record found for digest: {artifact_digest}"
        )
    except StorageError as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@app.post(
    "/verify/{artifact_digest:path}",
    response_model=VerificationResult,
    tags=["Verification"]
)
def verify_provenance(artifact_digest: str):
    """
    Verify the integrity of a stored provenance record.

    Recomputes the provenance hash and compares it to the stored hash.
    Any modification to the stored provenance will be detected here.

    Returns:
        VALID       - record exists and hash matches
        TAMPERED    - record exists but hash does not match
        NOT_FOUND   - no record for this digest
    """
    try:
        result = store.verify_integrity(artifact_digest)
        logger.info(
            f"Verification for {artifact_digest[:20]}...: {result.status}"
        )
        return result
    except StorageError as e:
        logger.error(f"Verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

# ── Run directly ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        reload=os.getenv("API_DEBUG", "false").lower() == "true",
        log_level="info"
    )
