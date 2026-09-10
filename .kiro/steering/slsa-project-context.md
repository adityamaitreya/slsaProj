---
inclusion: auto
name: slsa-project-context
description: Context and best practices for SLSA provenance verification project development
---

# SLSA Project Development Context

## Project Overview
Building a software supply-chain provenance verification system using SLSA with two interchangeable backends:
- System A: Centralized PostgreSQL storage
- System B: Decentralized Blockchain + IPFS storage

## Key Development Principles

### 1. Common Interface Pattern
Always maintain the `ProvenanceStore` abstraction:
```python
class ProvenanceStore:
    def store(self, provenance): pass
    def retrieve(self, digest): pass  
    def verify_integrity(self, provenance): pass
```

### 2. Security-First Development
- Never hardcode secrets or keys
- Use environment variables for all configuration
- Implement proper input validation
- Follow SLSA Level 3 requirements where possible
- Generate SBOMs for all artifacts
- Sign everything with Cosign/Sigstore

### 3. Research Methodology
- Keep both systems identical except for storage layer
- Document all assumptions and limitations
- Use consistent test datasets across experiments
- Measure multiple metrics (latency, throughput, storage, security)
- Run statistical analysis on results

### 4. Tools and Standards
- **SBOM Generation**: Use Syft for generating SPDX-format SBOMs
- **Provenance**: Use GitHub's SLSA generator for v1.0 provenance
- **Signing**: Use Cosign with keyless signing via GitHub OIDC
- **Databases**: PostgreSQL with SQLAlchemy ORM
- **Blockchain**: Solidity smart contracts with Hardhat for local development
- **IPFS**: Use Kubo (go-ipfs) with Python ipfshttpclient
- **API**: FastAPI for all web services
- **Testing**: pytest with comprehensive test coverage
- **Benchmarking**: Locust or k6 for load testing

### 5. Project Structure Standards
```
/
├── app/                    # Sample application to be verified
├── backends/               # Storage implementations
│   ├── postgresql/
│   └── blockchain_ipfs/
├── verification/           # Common verification engine
├── dashboard/             # React frontend
├── benchmarks/            # Performance testing
├── tests/                 # Comprehensive test suite
├── docker/               # Container configurations  
└── docs/                 # Documentation
```

### 6. Environment Setup
Always use:
- Python 3.11+ with virtual environments
- Docker and Docker Compose for containerization
- GitHub Actions for CI/CD
- PostgreSQL 14+ for database backend
- Node.js 18+ for React dashboard

### 7. File References
Key project files to reference:
#[[file:Software_Supply_Chain_Project_Roadmap.md]]
#[[file:DEVELOPMENT_ROADMAP.md]]

### 8. Common Patterns

#### Error Handling
```python
class ProvenanceError(Exception):
    pass

class ProvenanceNotFoundError(ProvenanceError):
    pass

class ProvenanceIntegrityError(ProvenanceError):
    pass
```

#### Configuration Management
```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    blockchain_rpc_url: str
    ipfs_api_url: str
    
    class Config:
        env_file = ".env"
```

#### Logging
```python
import structlog
logger = structlog.get_logger()
```

## Research Focus Areas
When developing, always consider impact on:
1. **Performance**: Verification latency, throughput
2. **Security**: Tamper detection, signature validation
3. **Storage**: Overhead, scalability
4. **Availability**: Failure recovery, redundancy
5. **Cost**: Computational resources, storage costs