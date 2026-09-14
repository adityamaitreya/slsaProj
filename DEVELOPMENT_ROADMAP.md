# SLSA Software Supply Chain Provenance Verification
## Development Roadmap & Progress Tracker

---

## 🎯 Project Overview

**Research Goal:** Compare centralized PostgreSQL vs. decentralized Blockchain+IPFS storage for software supply-chain provenance verification.

**Key Principle:** Build ONE pipeline with TWO interchangeable storage backends to isolate storage architecture as the primary experimental variable.

---

## 📋 Phase Progress Tracker

- [ ] **Phase A:** Centralized System (PostgreSQL) - 11 stages
- [ ] **Phase B:** Decentralized System (Blockchain+IPFS) - 4 stages  
- [ ] **Phase C:** Benchmarking & Comparison - 5 stages

**Overall Progress:** 0/20 stages complete (0%)

---

# 🔵 PHASE A — CENTRALIZED SYSTEM (PostgreSQL Backend)

> **Phase Objective:** Build a complete SLSA provenance verification pipeline using PostgreSQL for storage.

## Stage A1: Sample Application
- [x] **Status:** ✅ COMPLETED
- **Objective:** Create a simple Python/Node.js application that serves as our test artifact
- **Key Concepts:** 
  - We need *something* to build - the app content doesn't matter
  - This becomes our "software artifact" that we'll track through the supply chain
- **Tools Used:** Python Flask or Node.js Express
- **Deliverables:**
  - [x] Simple web API (Hello World + version endpoint)
  - [x] Requirements/package files (requirements.txt or package.json)
  - [x] Basic README
- **Success Criteria:** App runs locally and responds to HTTP requests ✅
- **Time Estimate:** 1-2 hours ✅ COMPLETED

---

## Stage A2: Dockerization  
- [x] **Status:** ✅ COMPLETED
- **Objective:** Package the application into a reproducible Docker container
- **Key Concepts:**
  - Docker creates deterministic, hashable artifacts
  - SHA-256 digest uniquely identifies the built image
  - Any change in code → different digest (tamper detection foundation)
- **Tools Used:** Docker, Dockerfile
- **Deliverables:**
  - [x] Dockerfile (multi-stage build for efficiency)
  - [x] .dockerignore file
  - [x] Build script
  - [x] Local build verification
- **Success Criteria:** 
  - Docker image builds successfully ✅
  - Image runs and serves HTTP requests ✅
  - Can extract SHA-256 digest ✅
- **Time Estimate:** 2-3 hours ✅ COMPLETED

---

## Stage A3: GitHub Actions CI/CD Pipeline
- [x] **Status:** ✅ COMPLETED (Local Setup - Ready to Push)  
- **Objective:** Automate the build process with a trusted build environment
- **Key Concepts:**
  - GitHub Actions = trusted builder (not "random laptop")
  - Automatic triggers on code push
  - Reproducible build environment
  - Foundation for provenance generation
- **Tools Used:** GitHub Actions, GitHub Container Registry (GHCR)
- **Deliverables:**
  - [x] `.github/workflows/build.yml` workflow file
  - [x] Docker build automation
  - [x] Push to GHCR (GitHub Container Registry)
  - [x] Extract and save SHA-256 digest
- **Success Criteria:** 
  - Workflow triggers on push ✅ (Local ready - needs GitHub repo)
  - Image builds and pushes successfully ⏳ (Will complete after push)
  - Can access digest from workflow logs ⏳ (Will complete after push)
- **Time Estimate:** 3-4 hours ✅ COMPLETED

---

## Stage A4: SBOM Generation
- [x] **Status:** ✅ COMPLETED
- **Objective:** Generate Software Bill of Materials (ingredient list)
- **Key Concepts:**
  - SBOM = list of all libraries/dependencies in your artifact
  - Critical for vulnerability tracking (e.g., Log4Shell detection)
  - Industry standard for supply chain transparency
- **Tools Used:** Syft (by Anchore)
- **Deliverables:**
  - [x] Integrate Syft into GitHub Actions
  - [x] Generate SBOM in SPDX format
  - [x] Store SBOM as workflow artifact
  - [x] Verify SBOM content accuracy
- **Success Criteria:** 
  - SBOM generates automatically on build ✅
  - Contains all expected dependencies ✅
  - Valid SPDX format ✅
- **Time Estimate:** 2-3 hours ✅ COMPLETED

---

## Stage A5: SLSA Provenance Generation  
- [x] **Status:** ✅ COMPLETED
- **Objective:** Generate cryptographic build receipt (birth certificate)
- **Key Concepts:**
  - SLSA = Supply-chain Levels for Software Artifacts
  - Records WHO built it, WHEN, FROM WHICH repo/commit, ON WHICH system
  - Industry standard (Google, GitHub, npm use this)
  - Tamper-evident build metadata
- **Tools Used:** slsa-framework/slsa-github-generator@v2.0.0
- **Deliverables:**
  - [x] Integrate SLSA generator into workflow (separate `slsa-provenance` job)
  - [x] Generate SLSA v1.0 provenance attached to image in GHCR
  - [x] Provenance references correct image digest, repo, commit, builder
  - [x] Provenance stored as signed OCI attestation in registry
- **Success Criteria:**
  - Provenance generates with each build ✅
  - Contains correct repo, commit, builder info ✅
  - Attached to image digest in GHCR ✅
- **Time Estimate:** 3-4 hours ✅ COMPLETED

---

## Stage A6: Cosign Signing
- [x] **Status:** ✅ COMPLETED
- **Objective:** Cryptographically sign artifact and provenance  
- **Key Concepts:**
  - Digital signatures prove authenticity
  - Sigstore/Cosign = keyless signing (uses OIDC — no private key to manage)
  - If anyone tampers with signed data, signature verification fails
  - Signatures recorded in public Rekor transparency log
- **Tools Used:** Cosign v2.2.3, Sigstore, GitHub OIDC
- **Deliverables:**
  - [x] Cosign installed in workflow via sigstore/cosign-installer@v3
  - [x] Docker image signed with Cosign keyless (cosign sign)
  - [x] SBOM attested with Cosign (cosign attest --type cyclonedx)
  - [x] Signatures pushed to GHCR alongside image
  - [x] Signatures recorded in Rekor public transparency log
  - [x] Verify command documented in build summary
- **Success Criteria:**
  - Image signature generated automatically ✅
  - SBOM attestation pushed to registry ✅
  - Signature verifiable with cosign verify ✅
- **Time Estimate:** 3-4 hours ✅ COMPLETED

---

## Stage A7: Common Storage Interface
- [ ] **Status:** Not Started
- **Objective:** Create pluggable storage abstraction for research comparison
- **Key Concepts:**
  - Abstract interface = "electrical socket" 
  - Two implementations = "plugs" (PostgreSQL vs Blockchain+IPFS)
  - Same verification logic works with both backends
  - **CRITICAL** for fair research comparison
- **Tools Used:** Python abstract base classes
- **Deliverables:**
  - [ ] `ProvenanceStore` abstract base class
  - [ ] `store(provenance)` method signature
  - [ ] `retrieve(digest)` method signature  
  - [ ] `verify_integrity(provenance)` method signature
  - [ ] Interface documentation
- **Success Criteria:**
  - Clean, minimal interface design
  - Well-documented method contracts
  - Ready for two implementations
- **Time Estimate:** 2-3 hours

---

## Stage A8: PostgreSQL Backend Implementation
- [ ] **Status:** Not Started
- **Objective:** Build centralized storage backend with SQL database
- **Key Concepts:**
  - PostgreSQL = mature, fast, ACID-compliant relational database
  - REST API exposes storage operations
  - Traditional/centralized architecture
  - Baseline for comparison
- **Tools Used:** PostgreSQL, FastAPI, SQLAlchemy, Docker Compose
- **Deliverables:**
  - [ ] PostgreSQL database schema
  - [ ] `PostgreSQLStore` implementation  
  - [ ] REST API with endpoints: POST/GET/verify/health
  - [ ] Docker Compose setup for local development
  - [ ] Database migrations
  - [ ] API documentation (auto-generated by FastAPI)
- **Success Criteria:**
  - All CRUD operations work
  - API responds correctly to test requests
  - Database persists data correctly
  - Implements full `ProvenanceStore` interface
- **Time Estimate:** 6-8 hours

---

## Stage A9: Verification Engine & API
- [ ] **Status:** Not Started
- **Objective:** Build the core verification logic (same for both backends)
- **Key Concepts:**
  - Takes artifact digest → returns VALID/INVALID/TAMPERED
  - Runs ALL security checks in sequence
  - Backend-agnostic (works with any storage implementation)
  - Single source of truth for verification logic
- **Tools Used:** FastAPI, Python cryptography libraries
- **Deliverables:**
  - [ ] `VerificationEngine` class with all check methods
  - [ ] FastAPI endpoint `/verify/{digest}`
  - [ ] Comprehensive verification pipeline:
    - [ ] Artifact digest validation
    - [ ] Cosign signature verification  
    - [ ] SLSA provenance validation
    - [ ] Source repository verification
    - [ ] Builder identity verification
    - [ ] Timestamp validation
  - [ ] Structured result format (VALID/INVALID + details)
  - [ ] Error handling and logging
- **Success Criteria:**
  - All verification checks implemented
  - Returns correct results for valid/invalid artifacts
  - Detailed error messages for failures
  - Works with PostgreSQL backend
- **Time Estimate:** 8-10 hours

---

## Stage A10: React Dashboard
- [ ] **Status:** Not Started
- **Objective:** Build web UI for artifact verification
- **Key Concepts:**
  - User-friendly interface for testing
  - Demonstrates system capabilities
  - Same UI works with both backends
  - Research demo/presentation tool
- **Tools Used:** React, TypeScript, Tailwind CSS
- **Deliverables:**
  - [ ] React app with verification form
  - [ ] Artifact digest input field
  - [ ] Backend selection (PostgreSQL/Blockchain+IPFS)
  - [ ] Real-time verification results display
  - [ ] Verification details breakdown
  - [ ] Performance metrics display (latency)
  - [ ] Error handling and user feedback
- **Success Criteria:**
  - Can verify artifacts through web interface
  - Shows clear VALID/INVALID results
  - Displays verification details
  - Works with PostgreSQL backend
- **Time Estimate:** 6-8 hours

---

## Stage A11: Functional Testing Suite
- [ ] **Status:** Not Started
- **Objective:** Verify system correctly detects valid/invalid artifacts
- **Key Concepts:**
  - Must prove correctness before measuring performance
  - Test both positive cases (valid) and negative cases (tampered)
  - Automated test suite for continuous validation
  - Foundation for research credibility
- **Tools Used:** pytest, Docker Compose for test environment
- **Deliverables:**
  - [ ] Test fixtures with known-good and tampered artifacts
  - [ ] Positive test cases:
    - [ ] Valid artifact → VALID result
    - [ ] Valid signature → verification passes
    - [ ] Correct provenance → validation passes
  - [ ] Negative test cases:
    - [ ] Modified artifact → INVALID result
    - [ ] Invalid signature → verification fails
    - [ ] Missing provenance → INVALID result
    - [ ] Wrong digest → INVALID result
    - [ ] Wrong builder → INVALID result
    - [ ] Modified provenance → INVALID result
  - [ ] Automated test runner
  - [ ] Test coverage report
- **Success Criteria:**
  - All positive tests pass
  - All negative tests correctly detect tampering
  - 100% tamper detection rate
  - Zero false positives
- **Time Estimate:** 6-8 hours

**🎉 Phase A Completion Milestone:** Full working centralized provenance verification system

---

# 🟠 PHASE B — DECENTRALIZED SYSTEM (Blockchain + IPFS Backend)

> **Phase Objective:** Replace PostgreSQL backend with Blockchain+IPFS while keeping everything else identical.

## Stage B1: IPFS Backend Implementation
- [ ] **Status:** Not Started
- **Objective:** Store full provenance data on IPFS (InterPlanetary File System)
- **Key Concepts:**
  - IPFS = peer-to-peer, content-addressed storage
  - Content addressing = files identified by content hash (CID)
  - Inherent tamper detection (content change = address change)
  - Distributed storage (no single point of failure)
- **Tools Used:** Kubo (IPFS node), Python ipfshttpclient
- **Deliverables:**
  - [ ] Local IPFS node setup
  - [ ] Python IPFS client integration
  - [ ] Upload provenance JSON to IPFS
  - [ ] Retrieve provenance by CID
  - [ ] CID validation and integrity checks
  - [ ] Error handling for network failures
- **Success Criteria:**
  - Can store/retrieve provenance data
  - CID correctly identifies content
  - Tamper detection works (modified content = different CID)
- **Time Estimate:** 4-6 hours

---

## Stage B2: Blockchain Smart Contract
- [ ] **Status:** Not Started
- **Objective:** Create tamper-evident ledger for provenance metadata
- **Key Concepts:**
  - Smart contract = immutable program on blockchain
  - Stores small, critical metadata (digest, CID, timestamps)
  - Once written, data cannot be changed
  - Provides cryptographic proof of existence/integrity
- **Tools Used:** Solidity, Hardhat (local blockchain), Web3.py
- **Deliverables:**
  - [ ] Solidity smart contract with functions:
    - [ ] `registerProvenance()` - store new provenance record
    - [ ] `getProvenance()` - retrieve by artifact digest
    - [ ] `verifyProvenance()` - validate integrity
  - [ ] Contract stores:
    - [ ] `artifactDigest` (unique identifier)
    - [ ] `provenanceHash` (tamper detection)
    - [ ] `ipfsCID` (pointer to full data)
    - [ ] `builderIdentity` (who built it)
    - [ ] `timestamp` (when registered)
  - [ ] Local blockchain setup with Hardhat
  - [ ] Contract deployment scripts
  - [ ] Python integration (Web3.py)
- **Success Criteria:**
  - Contract deploys successfully
  - Can store/retrieve records
  - Gas costs reasonable for testing
  - Tamper detection works
- **Time Estimate:** 6-8 hours

---

## Stage B3: Blockchain + IPFS Integration
- [ ] **Status:** Not Started
- **Objective:** Connect IPFS storage with blockchain metadata layer
- **Key Concepts:**
  - IPFS holds large data (full provenance JSON)
  - Blockchain holds small metadata + IPFS pointer (CID)
  - Single `store()` call does both operations
  - Verification checks both layers for consistency
- **Tools Used:** Python integration layer
- **Deliverables:**
  - [ ] `BlockchainIPFSStore` class implementing `ProvenanceStore`
  - [ ] Two-phase storage: IPFS upload → blockchain registration
  - [ ] Two-phase retrieval: blockchain lookup → IPFS download
  - [ ] Cross-layer integrity verification:
    - [ ] IPFS content hash matches blockchain record
    - [ ] Artifact digest matches blockchain record
    - [ ] Timestamps consistent
  - [ ] Error handling for partial failures
  - [ ] Transaction confirmation waiting
- **Success Criteria:**
  - Implements full `ProvenanceStore` interface
  - Data integrity maintained across both layers
  - Handles network/blockchain delays gracefully
- **Time Estimate:** 5-6 hours

---

## Stage B4: Integration with Existing System  
- [ ] **Status:** Not Started
- **Objective:** Plug blockchain+IPFS backend into existing verification API
- **Key Concepts:**
  - **Zero changes** to verification logic
  - Same API endpoints work with new backend
  - Same React dashboard works with new backend
  - Proves the interface abstraction works
- **Tools Used:** Configuration management, dependency injection
- **Deliverables:**
  - [ ] Backend switching mechanism (config file/env var)
  - [ ] Updated Docker Compose with IPFS + blockchain nodes
  - [ ] Same FastAPI endpoints working with new backend
  - [ ] Same React dashboard working with new backend
  - [ ] Backend health checks and status monitoring
- **Success Criteria:**
  - All existing tests pass with new backend
  - API responses identical to PostgreSQL version
  - Dashboard shows same results
  - Can switch backends without code changes
- **Time Estimate:** 3-4 hours

**🎉 Phase B Completion Milestone:** Two identical systems with different storage backends

---

# 🟢 PHASE C — BENCHMARKING & RESEARCH COMPARISON

> **Phase Objective:** Systematically measure and compare both systems across multiple dimensions.

## Stage C1: Benchmark Dataset Creation
- [ ] **Status:** Not Started
- **Objective:** Create standardized test dataset for fair comparison
- **Key Concepts:**
  - Fixed dataset eliminates variability
  - Multiple artifact sizes test scalability
  - Reproducible test conditions
  - Statistical validity requires sufficient sample size
- **Tools Used:** Python scripts, Docker builds
- **Deliverables:**
  - [ ] 100 unique artifacts with known properties:
    - [ ] Various sizes (1KB - 5MB provenance)
    - [ ] Different SBOM complexities
    - [ ] Various builder identities
    - [ ] Spread across time periods
  - [ ] Corresponding provenance packages
  - [ ] Dataset metadata and documentation
  - [ ] Validation scripts (all artifacts verify correctly)
- **Success Criteria:**
  - All artifacts verify as VALID on both backends
  - Dataset covers expected size/complexity ranges
  - Reproducible generation process
- **Time Estimate:** 4-5 hours

---

## Stage C2: Automated Benchmark Suite
- [ ] **Status:** Not Started  
- **Objective:** Build automated testing infrastructure for performance measurement
- **Key Concepts:**
  - Automated = repeatable, unbiased results
  - Multiple concurrency levels test scalability
  - Comprehensive metrics capture system behavior
  - Statistical analysis requires multiple runs
- **Tools Used:** Locust or k6 (load testing), Python statistics
- **Deliverables:**
  - [ ] Load testing scripts with configurable parameters:
    - [ ] Concurrency levels: 1, 10, 50, 100 users
    - [ ] Duration: 5-minute test runs
    - [ ] Backend selection: PostgreSQL vs Blockchain+IPFS
  - [ ] Metrics collection:
    - [ ] Response latency (min, mean, median, max, p95, p99)
    - [ ] Throughput (requests/second)
    - [ ] Error rate
    - [ ] Resource utilization (CPU, memory, disk, network)
  - [ ] Automated test runner
  - [ ] Raw data export (CSV format)
  - [ ] Statistical analysis scripts
- **Success Criteria:**
  - Tests run unattended and produce consistent results
  - Captures all required metrics
  - Works with both backends
- **Time Estimate:** 8-10 hours

---

## Stage C3: Performance Experiments Execution
- [ ] **Status:** Not Started
- **Objective:** Run comprehensive performance comparison experiments
- **Key Concepts:**
  - Multiple experiment types reveal different aspects
  - Component-level analysis explains overall performance
  - Failure testing shows robustness differences
  - Storage analysis reveals scalability implications
- **Tools Used:** Benchmark suite, monitoring tools
- **Deliverables:**
  - [ ] **Experiment 1:** Verification Latency
    - [ ] Test both backends at 1, 10, 50, 100 concurrent users
    - [ ] Measure end-to-end verification time
    - [ ] Record full latency distribution (not just averages)
  - [ ] **Experiment 2:** Throughput Measurement  
    - [ ] Maximum requests/second for each backend
    - [ ] Saturation point identification
    - [ ] Error rate under load
  - [ ] **Experiment 3:** Component-Level Timing
    - [ ] Break down verification into steps:
      - Storage retrieval time
      - Signature verification time  
      - SLSA validation time
      - Network/blockchain confirmation time
    - [ ] Identify performance bottlenecks
  - [ ] **Experiment 4:** Storage Overhead Analysis
    - [ ] PostgreSQL: database size, index overhead
    - [ ] IPFS: stored data size, retrieval efficiency
    - [ ] Blockchain: gas costs, transaction overhead
  - [ ] **Experiment 5:** Failure Recovery Testing
    - [ ] Simulate backend failures
    - [ ] Measure recovery time and data consistency
- **Success Criteria:**
  - All experiments complete without data corruption
  - Results statistically significant (multiple runs)
  - Raw data available for analysis
- **Time Estimate:** 12-15 hours

---

## Stage C4: Statistical Analysis & Visualization
- [ ] **Status:** Not Started
- **Objective:** Analyze experimental results and create research-quality outputs
- **Key Concepts:**
  - Statistics provide objective comparison
  - Visualizations communicate findings clearly  
  - Research requires rigorous methodology
  - Results must support/refute hypotheses
- **Tools Used:** Python (pandas, matplotlib, seaborn), Jupyter notebooks
- **Deliverables:**
  - [ ] **Statistical Analysis:**
    - [ ] Latency comparison tables with confidence intervals
    - [ ] Throughput comparison with significance tests
    - [ ] Storage efficiency analysis
    - [ ] Cost/benefit analysis (performance vs overhead)
  - [ ] **Research Visualizations:**
    - [ ] Latency vs Concurrency graphs
    - [ ] Throughput vs Load curves  
    - [ ] Component timing breakdown charts
    - [ ] Storage growth projections
    - [ ] Cost analysis charts
  - [ ] **Comparison Tables:**
    - [ ] Performance summary table
    - [ ] Security capabilities comparison
    - [ ] Operational characteristics comparison
    - [ ] Trade-offs analysis matrix
- **Success Criteria:**
  - Clear performance winner identified (or "depends on use case")
  - Statistical significance established
  - Limitations and biases acknowledged
  - Professional-quality visualizations
- **Time Estimate:** 6-8 hours

---

## Stage C5: Research Paper & Documentation
- [ ] **Status:** Not Started
- **Objective:** Document findings in IEEE-format research paper
- **Key Concepts:**
  - Research paper validates academic rigor
  - Reproducible methodology enables peer review
  - Clear conclusions guide practical decisions
  - Complete documentation enables replication
- **Tools Used:** LaTeX, academic writing tools
- **Deliverables:**
  - [ ] **IEEE Conference Paper** (6-8 pages):
    - [ ] Abstract summarizing key findings
    - [ ] Introduction and motivation
    - [ ] Related work comparison
    - [ ] Methodology and experimental design
    - [ ] Results and analysis
    - [ ] Discussion of implications
    - [ ] Conclusions and future work
  - [ ] **Technical Documentation:**
    - [ ] Complete setup/deployment guide
    - [ ] API documentation
    - [ ] Database schemas
    - [ ] Smart contract specifications
    - [ ] Benchmark reproduction guide
  - [ ] **Open Source Release:**
    - [ ] All code published on GitHub
    - [ ] Docker Compose for easy setup
    - [ ] Example dataset
    - [ ] CI/CD pipeline templates
- **Success Criteria:**
  - Paper follows IEEE format standards
  - Methodology enables replication
  - Conclusions supported by data
  - Code publicly available and documented
- **Time Estimate:** 10-12 hours

**🎉 Phase C Completion Milestone:** Complete research comparison with publishable results

---

# 📊 Project Summary Statistics

## Time Estimates
- **Phase A:** 43-58 hours (Centralized system)
- **Phase B:** 18-24 hours (Decentralized system)  
- **Phase C:** 40-50 hours (Benchmarking & analysis)
- **Total:** 101-132 hours (~3-4 months part-time)

## Key Technologies Mastered
- Docker & containerization
- GitHub Actions CI/CD
- SLSA provenance & Sigstore/Cosign
- PostgreSQL & FastAPI
- IPFS & blockchain/Solidity
- Load testing & performance analysis
- Research methodology & academic writing

## Research Contributions
- First direct comparison of centralized vs decentralized provenance storage
- Benchmarking methodology for supply chain security systems
- Open-source reference implementation of SLSA verification
- Performance/security trade-off analysis for practitioners

---

## 🎯 Success Criteria for Overall Project

### Technical Success
- [ ] Both systems detect tampering with 100% accuracy
- [ ] Performance differences quantified with statistical significance
- [ ] Storage trade-offs clearly documented
- [ ] Systems handle realistic concurrent load

### Research Success  
- [ ] Clear answer to "which architecture is better for what use cases?"
- [ ] Methodology enables replication by other researchers
- [ ] Results publishable in academic venue
- [ ] Practical guidance for industry adoption

### Educational Success
- [ ] Deep understanding of software supply chain security
- [ ] Hands-on experience with modern DevOps/security tools
- [ ] Research methodology and scientific analysis skills
- [ ] Portfolio project demonstrating full-stack capabilities

---

*Last Updated: [Date will be updated as we progress]*
*Current Phase: Phase A - Stage A1 (Sample Application)*