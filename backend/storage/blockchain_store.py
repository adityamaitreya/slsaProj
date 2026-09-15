"""
Blockchain + IPFS implementation of ProvenanceStore.

This is System A (Decentralized) in the research comparison.
Implementation is done in Phase B (Stages B1-B3).

For now this is a stub — it inherits the interface and raises
NotImplementedError so any accidental use fails loudly.
"""

from models.provenance import ProvenanceRecord, StoreResult, VerificationResult, VerificationStatus
from storage.base import ProvenanceStore, StorageError

class BlockchainIPFSStore(ProvenanceStore):
    """
    Stores provenance records using IPFS + Ethereum smart contract.

    IPFS  : stores the full provenance JSON, returns a CID
    Chain : stores artifact_digest + provenance_hash + IPFS CID on-chain

    Phase B implementation:
        Stage B1 — IPFS backend
        Stage B2 — Solidity smart contract
        Stage B3 — Connect both together
    """

    def __init__(self, ipfs_url: str, rpc_url: str, contract_address: str):
        self.ipfs_url = ipfs_url
        self.rpc_url = rpc_url
        self.contract_address = contract_address
        self.backend_name = "blockchain_ipfs"

    def store(self, record: ProvenanceRecord) -> StoreResult:
        # Phase B — Stage B3
        raise NotImplementedError("BlockchainIPFSStore.store() — implement in Stage B3")

    def retrieve(self, artifact_digest: str) -> ProvenanceRecord:
        # Phase B — Stage B3
        raise NotImplementedError("BlockchainIPFSStore.retrieve() — implement in Stage B3")

    def verify_integrity(self, artifact_digest: str) -> VerificationResult:
        # Phase B — Stage B3
        raise NotImplementedError("BlockchainIPFSStore.verify_integrity() — implement in Stage B3")

    def health_check(self) -> bool:
        # Phase B — Stage B3
        raise NotImplementedError("BlockchainIPFSStore.health_check() — implement in Stage B3")
