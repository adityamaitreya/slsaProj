"""
Provenance data models.
These are shared between both storage backends (PostgreSQL and Blockchain+IPFS).
The same data shape goes into both systems — only the storage layer differs.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class VerificationStatus(str, Enum):
    """Possible outcomes of a verification check."""
    VALID = "VALID"
    TAMPERED = "TAMPERED"
    INVALID = "INVALID"
    NOT_FOUND = "NOT_FOUND"

class ProvenanceRecord(BaseModel):
    """
    A complete provenance package for one artifact.

    This is everything we need to verify that an artifact is authentic:
    - artifact_digest   : the SHA-256 of the Docker image (the artifact's fingerprint)
    - provenance_hash   : SHA-256 of the provenance JSON itself (tamper detection)
    - provenance_json   : the full SLSA provenance document
    - sbom_json         : the full SBOM (ingredient list)
    - signature         : the Cosign signature
    - builder_identity  : who built it (GitHub Actions run URL)
    - source_repository : where the source code lives
    - source_commit     : exact git commit SHA
    - timestamp         : when this record was created
    """
    artifact_digest: str = Field(
        ...,
        description="SHA-256 digest of the artifact e.g. sha256:abc123",
        example="sha256:5fbc20ebcfdd3271229ad6e8309a5b2e971f8b3e"
    )
    provenance_hash: str = Field(
        ...,
        description="SHA-256 hash of the provenance_json string"
    )
    provenance_json: dict = Field(
        ...,
        description="Full SLSA provenance document as JSON"
    )
    sbom_json: Optional[dict] = Field(
        default=None,
        description="Full SBOM document as JSON (optional)"
    )
    signature: Optional[str] = Field(
        default=None,
        description="Cosign signature string"
    )
    builder_identity: str = Field(
        ...,
        description="Who built the artifact e.g. GitHub Actions run URL"
    )
    source_repository: str = Field(
        ...,
        description="Source code repository URL"
    )
    source_commit: str = Field(
        ...,
        description="Exact git commit SHA that was built"
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this provenance record was created"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "artifact_digest": "sha256:5fbc20ebcfdd",
                "provenance_hash": "sha256:abc123",
                "provenance_json": {"builder": {"id": "https://github.com/actions"}},
                "builder_identity": "https://github.com/adityamaitreya/slsaProj/actions/runs/123",
                "source_repository": "https://github.com/adityamaitreya/slsaProj",
                "source_commit": "9ed3b5a9102d",
                "timestamp": "2026-09-14T16:00:00Z"
            }
        }

class StoreResult(BaseModel):
    """Returned by store() — confirms the record was saved and where."""
    success: bool
    artifact_digest: str
    backend: str          # "postgresql" or "blockchain_ipfs"
    location: str         # database row ID or blockchain tx hash
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class VerificationResult(BaseModel):
    """Returned by verify() — the final verdict on an artifact."""
    artifact_digest: str
    status: VerificationStatus
    backend: str
    checks: dict = Field(
        default_factory=dict,
        description="Individual check results e.g. {'signature_valid': True}"
    )
    message: str = ""
    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
