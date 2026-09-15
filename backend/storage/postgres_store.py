"""
PostgreSQL implementation of ProvenanceStore.

This is System B (Centralized) in the research comparison.
It stores provenance records in a standard relational database.

Architecture:
    ProvenanceStore (abstract)
          │
          └── PostgreSQLStore  ← this file
                   │
                   └── PostgreSQL database
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    create_engine, Column, String, Text, DateTime,
    Index, text
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError

from models.provenance import (
    ProvenanceRecord, StoreResult, VerificationResult, VerificationStatus
)
from storage.base import (
    ProvenanceStore, StorageError, RecordNotFoundError, DuplicateRecordError
)

logger = logging.getLogger(__name__)

# ── SQLAlchemy ORM model (the actual database table definition) ───────────

class Base(DeclarativeBase):
    pass

class ProvenanceTable(Base):
    """
    The database table that stores provenance records.

    Each row = one artifact's complete provenance package.
    The artifact_digest is the primary key — one record per artifact.
    """
    __tablename__ = "provenance"

    # Primary key — the artifact's SHA-256 fingerprint
    artifact_digest = Column(String(255), primary_key=True, index=True)

    # Hash of the provenance JSON — used for tamper detection
    provenance_hash = Column(String(255), nullable=False)

    # The full SLSA provenance document stored as JSON text
    provenance_json = Column(Text, nullable=False)

    # The full SBOM stored as JSON text (optional)
    sbom_json = Column(Text, nullable=True)

    # The Cosign signature string (optional)
    signature = Column(Text, nullable=True)

    # Who built it
    builder_identity = Column(String(500), nullable=False)

    # Source code location
    source_repository = Column(String(500), nullable=False)

    # Exact commit that was built
    source_commit = Column(String(255), nullable=False)

    # When this record was stored
    timestamp = Column(DateTime(timezone=True), nullable=False)

    # Index on source_repository for faster lookups by repo
    __table_args__ = (
        Index("ix_provenance_source_repo", "source_repository"),
        Index("ix_provenance_timestamp", "timestamp"),
    )

    def __repr__(self):
        return f"<ProvenanceTable digest={self.artifact_digest[:20]}...>"

# ── PostgreSQLStore implementation ────────────────────────────────────────

class PostgreSQLStore(ProvenanceStore):
    """
    Stores and retrieves provenance records using PostgreSQL.

    Usage:
        store = PostgreSQLStore("postgresql://user:pass@localhost:5432/slsa")
        result = store.store(record)
        record = store.retrieve("sha256:abc123")
    """

    def __init__(self, database_url: str):
        """
        Initialise the store and create the table if it doesn't exist.

        Args:
            database_url: SQLAlchemy connection string
                          e.g. "postgresql://user:pass@localhost:5432/slsa_db"
        """
        self.database_url = database_url
        self.backend_name = "postgresql"

        try:
            # create_engine sets up the connection pool (doesn't connect yet)
                        # pool_size and max_overflow only apply to PostgreSQL (QueuePool)
            # SQLite uses SingletonThreadPool which does not support them
            is_sqlite = database_url.startswith("sqlite")
            engine_kwargs = {"pool_pre_ping": True}
            if not is_sqlite:
                engine_kwargs["pool_size"] = 5
                engine_kwargs["max_overflow"] = 10

            self.engine = create_engine(database_url, **engine_kwargs)

            # SessionLocal is a factory — call it to get a database session
            self.SessionLocal = sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False
            )
            # Create the provenance table if it doesn't already exist
            Base.metadata.create_all(self.engine)
            logger.info("PostgreSQLStore initialised. Table ready.")

        except Exception as e:
            raise StorageError(f"Failed to initialise PostgreSQL store: {e}")

    # ── Implement the 4 required abstract methods ─────────────────────────

    def store(self, record: ProvenanceRecord) -> StoreResult:
        """
        Insert a provenance record into PostgreSQL.

        Steps:
        1. Verify the provenance_hash matches the provenance_json
        2. Convert the Pydantic model to a SQLAlchemy row
        3. Insert into the database
        4. Return a StoreResult confirming success
        """
        # Step 1: Verify hash integrity before storing
        if not self.verify_provenance_hash(record):
            raise StorageError(
                f"Provenance hash mismatch for {record.artifact_digest}. "
                "The record may have been tampered with before storage."
            )

        with self._get_session() as session:
            try:
                # Step 2: Convert Pydantic model → SQLAlchemy row
                row = ProvenanceTable(
                    artifact_digest=record.artifact_digest,
                    provenance_hash=record.provenance_hash,
                    provenance_json=json.dumps(record.provenance_json),
                    sbom_json=json.dumps(record.sbom_json) if record.sbom_json else None,
                    signature=record.signature,
                    builder_identity=record.builder_identity,
                    source_repository=record.source_repository,
                    source_commit=record.source_commit,
                    timestamp=record.timestamp
                )
                # Step 3: Insert
                session.add(row)
                session.commit()

                logger.info(f"Stored provenance for {record.artifact_digest[:20]}...")

                # Step 4: Return confirmation
                return StoreResult(
                    success=True,
                    artifact_digest=record.artifact_digest,
                    backend=self.backend_name,
                    location=f"postgresql/provenance/{record.artifact_digest}"
                )

            except IntegrityError:
                session.rollback()
                raise DuplicateRecordError(record.artifact_digest)

            except Exception as e:
                session.rollback()
                raise StorageError(f"Failed to store record: {e}")

    def retrieve(self, artifact_digest: str) -> ProvenanceRecord:
        """
        Fetch a provenance record from PostgreSQL by artifact digest.
        """
        with self._get_session() as session:
            row = session.get(ProvenanceTable, artifact_digest)

            if row is None:
                raise RecordNotFoundError(artifact_digest)

            # Convert SQLAlchemy row → Pydantic model
            return ProvenanceRecord(
                artifact_digest=row.artifact_digest,
                provenance_hash=row.provenance_hash,
                provenance_json=json.loads(row.provenance_json),
                sbom_json=json.loads(row.sbom_json) if row.sbom_json else None,
                signature=row.signature,
                builder_identity=row.builder_identity,
                source_repository=row.source_repository,
                source_commit=row.source_commit,
                timestamp=row.timestamp
            )

    def verify_integrity(self, artifact_digest: str) -> VerificationResult:
        """
        Retrieve the record and verify its provenance_hash matches.

        This detects if the stored provenance JSON was modified after storage.
        """
        try:
            record = self.retrieve(artifact_digest)
        except RecordNotFoundError:
            return VerificationResult(
                artifact_digest=artifact_digest,
                status=VerificationStatus.NOT_FOUND,
                backend=self.backend_name,
                message="No provenance record found for this digest"
            )

        hash_valid = self.verify_provenance_hash(record)

        return VerificationResult(
            artifact_digest=artifact_digest,
            status=VerificationStatus.VALID if hash_valid else VerificationStatus.TAMPERED,
            backend=self.backend_name,
            checks={
                "provenance_hash_valid": hash_valid,
                "record_found": True,
            },
            message="Provenance integrity verified" if hash_valid else "Provenance hash mismatch — record may be tampered"
        )

    def health_check(self) -> bool:
        """
        Run a simple SELECT 1 query to confirm the database is reachable.
        """
        try:
            with self._get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return False

    # ── Helper methods ────────────────────────────────────────────────────

    def _get_session(self) -> Session:
        """Return a new database session as a context manager."""
        return self.SessionLocal()

    def get_all_digests(self) -> list[str]:
        """Return all stored artifact digests. Useful for testing."""
        with self._get_session() as session:
            rows = session.query(ProvenanceTable.artifact_digest).all()
            return [r[0] for r in rows]

    def delete_record(self, artifact_digest: str) -> bool:
        """Delete a record. Used in tests only."""
        with self._get_session() as session:
            row = session.get(ProvenanceTable, artifact_digest)
            if row is None:
                return False
            session.delete(row)
            session.commit()
            return True
