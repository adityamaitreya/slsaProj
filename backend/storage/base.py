"""
Abstract storage interface (the "socket").

Both PostgreSQLStore and BlockchainIPFSStore must implement every method here.
The verification engine only ever talks to this interface — never directly
to a database or blockchain. This is what makes the research comparison fair.
"""

import hashlib
import json
from abc import ABC, abstractmethod
from models.provenance import ProvenanceRecord, StoreResult, VerificationResult

class ProvenanceStore(ABC):
    """
    Abstract base class for provenance storage.

    ABC = Abstract Base Class. In Python, if a class inherits from ABC
    and has @abstractmethod methods, you CANNOT instantiate it directly.
    You must create a subclass that implements every abstract method.

    This enforces the contract: every backend MUST implement store(),
    retrieve(), and verify_integrity() or Python will raise an error.
    """

    @abstractmethod
    def store(self, record: ProvenanceRecord) -> StoreResult:
        """
        Save a provenance record to the backend.

        Args:
            record: The complete provenance package to store.

        Returns:
            StoreResult with success flag and location reference.

        Raises:
            StorageError: if the record cannot be saved.
        """
        pass

    @abstractmethod
    def retrieve(self, artifact_digest: str) -> ProvenanceRecord:
        """
        Fetch a provenance record by artifact digest.

        Args:
            artifact_digest: The SHA-256 digest e.g. "sha256:abc123"

        Returns:
            The ProvenanceRecord stored for this artifact.

        Raises:
            RecordNotFoundError: if no record exists for this digest.
            StorageError: if the backend cannot be reached.
        """
        pass

    @abstractmethod
    def verify_integrity(self, artifact_digest: str) -> VerificationResult:
        """
        Check that the stored provenance has not been tampered with.

        This method retrieves the record and runs integrity checks
        specific to each backend:
        - PostgreSQL: recompute provenance_hash and compare
        - Blockchain: compare on-chain hash with stored hash

        Args:
            artifact_digest: The SHA-256 digest to verify.

        Returns:
            VerificationResult with VALID, TAMPERED, or INVALID status.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """
        Check if the backend is reachable and operational.

        Returns:
            True if healthy, False otherwise.
        """
        pass

    # ── Shared utility methods (same for all backends) ────────────────────

    @staticmethod
    def compute_provenance_hash(provenance_json: dict) -> str:
        """
        Compute a deterministic SHA-256 hash of a provenance document.

        We sort the keys before hashing so the hash is the same
        regardless of key order in the JSON.

        This hash is stored alongside the provenance. If anyone modifies
        the provenance document, this hash will no longer match.
        """
        serialized = json.dumps(provenance_json, sort_keys=True, separators=(",", ":"))
        return "sha256:" + hashlib.sha256(serialized.encode()).hexdigest()

    @staticmethod
    def verify_provenance_hash(record: ProvenanceRecord) -> bool:
        """
        Recompute the provenance hash and compare it to the stored one.

        Returns True if they match (not tampered), False if they differ.
        """
        expected = ProvenanceStore.compute_provenance_hash(record.provenance_json)
        return expected == record.provenance_hash

    def __repr__(self):
        return f"<{self.__class__.__name__}>"

# ── Custom exceptions ─────────────────────────────────────────────────────

class StorageError(Exception):
    """Raised when the storage backend cannot complete an operation."""
    pass

class RecordNotFoundError(StorageError):
    """Raised when no provenance record exists for a given digest."""
    def __init__(self, artifact_digest: str):
        self.artifact_digest = artifact_digest
        super().__init__(f"No provenance record found for digest: {artifact_digest}")

class DuplicateRecordError(StorageError):
    """Raised when trying to store a record that already exists."""
    def __init__(self, artifact_digest: str):
        self.artifact_digest = artifact_digest
        super().__init__(f"Record already exists for digest: {artifact_digest}")

