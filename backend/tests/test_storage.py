"""
Tests for the storage interface and PostgreSQL implementation.

We use SQLite (in-memory) instead of real PostgreSQL here.
SQLite is a lightweight database that lives entirely in RAM —
perfect for fast tests with zero setup.

The same SQLAlchemy code works with both SQLite and PostgreSQL
because we only use standard SQL features.
"""

import pytest
import json
from datetime import datetime, timezone

from models.provenance import ProvenanceRecord, VerificationStatus
from storage.base import (
    ProvenanceStore, RecordNotFoundError, DuplicateRecordError, StorageError
)
from storage.postgres_store import PostgreSQLStore

# ── Fixtures (reusable test setup) ───────────────────────────────────────

@pytest.fixture
def store():
    """
    Create a fresh in-memory SQLite store for each test.
    'sqlite:///:memory:' means the database exists only in RAM
    and is destroyed when the test finishes.
    """
    s = PostgreSQLStore("sqlite:///:memory:")
    yield s

@pytest.fixture
def sample_provenance():
    """A valid provenance record we can reuse across tests."""
    provenance_json = {
        "builder": {
            "id": "https://github.com/adityamaitreya/slsaProj/actions/runs/123"
        },
        "buildType": "https://github.com/slsa-framework/slsa-github-generator",
        "subject": [{
            "name": "ghcr.io/adityamaitreya/slsaproj",
            "digest": {"sha256": "5fbc20ebcfdd3271229ad6e8309a5b2e971f8b3e"}
        }]
    }

    # Compute the correct hash using the shared utility
    provenance_hash = ProvenanceStore.compute_provenance_hash(provenance_json)

    return ProvenanceRecord(
        artifact_digest="sha256:5fbc20ebcfdd3271229ad6e8309a5b2e971f8b3e",
        provenance_hash=provenance_hash,
        provenance_json=provenance_json,
        builder_identity="https://github.com/adityamaitreya/slsaProj/actions/runs/123",
        source_repository="https://github.com/adityamaitreya/slsaProj",
        source_commit="9ed3b5a9102d",
        timestamp=datetime.now(timezone.utc)
    )

# ── Interface tests ───────────────────────────────────────────────────────

class TestProvenanceStoreInterface:
    """Verify the abstract interface is enforced correctly."""

    def test_cannot_instantiate_abstract_class(self):
        """ProvenanceStore cannot be used directly."""
        with pytest.raises(TypeError):
            ProvenanceStore()

    def test_postgres_store_is_subclass(self):
        """PostgreSQLStore satisfies the interface."""
        assert issubclass(PostgreSQLStore, ProvenanceStore)

    def test_compute_provenance_hash_is_deterministic(self):
        """Same input always produces the same hash."""
        data = {"key": "value", "nested": {"a": 1}}
        h1 = ProvenanceStore.compute_provenance_hash(data)
        h2 = ProvenanceStore.compute_provenance_hash(data)
        assert h1 == h2

    def test_compute_provenance_hash_detects_change(self):
        """Different input produces a different hash."""
        original = {"builder": "github-actions"}
        tampered = {"builder": "evil-actor"}
        assert ProvenanceStore.compute_provenance_hash(original) != \
               ProvenanceStore.compute_provenance_hash(tampered)

    def test_hash_format_starts_with_sha256(self):
        """Hash always starts with 'sha256:' prefix."""
        h = ProvenanceStore.compute_provenance_hash({"x": 1})
        assert h.startswith("sha256:")

    def test_key_order_does_not_affect_hash(self):
        """JSON key order must not change the hash — we sort keys."""
        a = {"z": 1, "a": 2}
        b = {"a": 2, "z": 1}
        assert ProvenanceStore.compute_provenance_hash(a) == \
               ProvenanceStore.compute_provenance_hash(b)

# ── Store and retrieve tests ──────────────────────────────────────────────

class TestPostgreSQLStore:
    """Test the PostgreSQL (SQLite in tests) implementation."""

    def test_store_returns_success(self, store, sample_provenance):
        """Storing a valid record returns success."""
        result = store.store(sample_provenance)
        assert result.success is True
        assert result.backend == "postgresql"
        assert sample_provenance.artifact_digest in result.location

    def test_retrieve_returns_correct_record(self, store, sample_provenance):
        """After storing, retrieve returns the same record."""
        store.store(sample_provenance)
        retrieved = store.retrieve(sample_provenance.artifact_digest)

        assert retrieved.artifact_digest == sample_provenance.artifact_digest
        assert retrieved.source_commit == sample_provenance.source_commit
        assert retrieved.builder_identity == sample_provenance.builder_identity
        assert retrieved.provenance_json == sample_provenance.provenance_json

    def test_retrieve_not_found_raises_error(self, store):
        """Retrieving a non-existent digest raises RecordNotFoundError."""
        with pytest.raises(RecordNotFoundError) as exc_info:
            store.retrieve("sha256:doesnotexist")
        assert "doesnotexist" in str(exc_info.value)

    def test_duplicate_store_raises_error(self, store, sample_provenance):
        """Storing the same digest twice raises DuplicateRecordError."""
        store.store(sample_provenance)
        with pytest.raises(DuplicateRecordError):
            store.store(sample_provenance)

    def test_store_rejects_tampered_hash(self, store, sample_provenance):
        """A record with a wrong provenance_hash is rejected at store time."""
        sample_provenance.provenance_hash = "sha256:wronghash"
        with pytest.raises(StorageError):
            store.store(sample_provenance)

    def test_health_check_passes(self, store):
        """Health check returns True when database is reachable."""
        assert store.health_check() is True

    def test_get_all_digests_empty(self, store):
        """Empty store returns empty list."""
        assert store.get_all_digests() == []

    def test_get_all_digests_after_store(self, store, sample_provenance):
        """After storing, digest appears in get_all_digests."""
        store.store(sample_provenance)
        digests = store.get_all_digests()
        assert sample_provenance.artifact_digest in digests

# ── Integrity verification tests ─────────────────────────────────────────

class TestVerifyIntegrity:
    """Test tamper detection logic."""

    def test_valid_record_returns_valid(self, store, sample_provenance):
        """Unmodified stored record returns VALID status."""
        store.store(sample_provenance)
        result = store.verify_integrity(sample_provenance.artifact_digest)
        assert result.status == VerificationStatus.VALID
        assert result.checks["provenance_hash_valid"] is True

    def test_not_found_returns_not_found(self, store):
        """Missing record returns NOT_FOUND status."""
        result = store.verify_integrity("sha256:missing")
        assert result.status == VerificationStatus.NOT_FOUND

    def test_tampered_provenance_detected(self, store, sample_provenance):
        """
        If someone modifies the provenance_json in the database directly,
        the hash check detects the tampering.
        """
        store.store(sample_provenance)

        # Simulate a direct database tamper — bypass the store() method
        with store._get_session() as session:
            from storage.postgres_store import ProvenanceTable
            row = session.get(ProvenanceTable, sample_provenance.artifact_digest)
            # Tamper with the stored provenance JSON directly
            tampered = json.loads(row.provenance_json)
            tampered["builder"]["id"] = "https://evil-actor.com"
            row.provenance_json = json.dumps(tampered)
            session.commit()

        # Now verify — should detect the tamper
        result = store.verify_integrity(sample_provenance.artifact_digest)
        assert result.status == VerificationStatus.TAMPERED
        assert result.checks["provenance_hash_valid"] is False
