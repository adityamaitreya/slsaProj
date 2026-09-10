# Software Supply-Chain Provenance Verification Using SLSA

## Complete Project Development & Research Performance Roadmap

> **Core concept:** Build one complete SLSA-based software supply-chain
> pipeline and connect it to two interchangeable provenance-storage
> endpoints: **Centralized PostgreSQL** and **Decentralized Blockchain +
> IPFS**. Keep the artifact-generation, signing, verification, and
> testing logic identical so that the storage architecture is the
> primary experimental variable.

------------------------------------------------------------------------

## 1. Project Objective

The project aims to provide a secure and tamper-evident method for
verifying software artifacts.

The system should answer:

> **Can we trust this software artifact, and can we prove where and how
> it was built?**

The pipeline generates:

-   Docker/software artifact
-   SHA-256 artifact digest
-   SBOM using Syft
-   SLSA provenance
-   Cosign/Sigstore signature

The resulting provenance package is stored through two alternative
backends:

1.  **Centralized:** PostgreSQL
2.  **Decentralized:** IPFS + Blockchain/Smart Contract

A common verification service retrieves the evidence and determines
whether the artifact is:

-   `VALID`
-   `TAMPERED`
-   `INVALID`

------------------------------------------------------------------------

# 2. Overall Architecture

``` text
                         ┌──────────────────┐
                         │  Developer Code  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ GitHub Repository│
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ GitHub Actions   │
                         │      CI/CD       │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             ┌──────────────┐            ┌──────────────┐
             │ Docker Build │            │ SBOM (Syft)  │
             └──────┬───────┘            └──────┬───────┘
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                         ┌──────────────────┐
                         │ SLSA Provenance  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Cosign Signing   │
                         └────────┬─────────┘
                                  │
                                  ▼
                       ┌───────────────────────┐
                       │ Provenance Package    │
                       │                       │
                       │ Artifact Digest       │
                       │ SLSA Provenance       │
                       │ SBOM                  │
                       │ Cosign Signature      │
                       └───────────┬───────────┘
                                   │
                       ┌───────────┴───────────┐
                       │   STORAGE INTERFACE   │
                       └───────────┬───────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    ▼                             ▼
          ┌──────────────────┐          ┌────────────────────┐
          │ CENTRALIZED      │          │ DECENTRALIZED      │
          │                  │          │                    │
          │ PostgreSQL       │          │ IPFS               │
          │ REST API         │          │       +            │
          │                  │          │ Blockchain         │
          └────────┬─────────┘          └──────────┬─────────┘
                   │                               │
                   └──────────────┬────────────────┘
                                  ▼
                       ┌──────────────────┐
                       │ Verification API │
                       │    FastAPI       │
                       └────────┬─────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │ Verification     │
                       │ Engine           │
                       └────────┬─────────┘
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                      VALID       TAMPERED /
                                  INVALID
```

------------------------------------------------------------------------

# 3. Research Design

## 3.1 Independent Variable

The main independent variable is the **provenance storage backend**.

  System     Backend             Architecture
  ---------- ------------------- ---------------
  System A   Blockchain + IPFS   Decentralized
  System B   PostgreSQL          Centralized

## 3.2 Keep Everything Else Identical

For a fair comparison, keep the following constant:

-   Same source code
-   Same Docker image
-   Same artifact digest
-   Same SBOM
-   Same SLSA provenance
-   Same Cosign signature
-   Same verification API
-   Same verification logic
-   Same test dataset
-   Same test machine/environment
-   Same concurrency levels
-   Same benchmark procedure

### Core research principle

> **Do not build two unrelated systems. Build one pipeline with a
> replaceable storage layer.**

This allows observed performance differences to be attributed primarily
to the storage architecture.

------------------------------------------------------------------------

# 4. Backend Architecture

## 4.1 Centralized Backend --- System B

``` text
                 Provenance
                      │
                      ▼
                 REST API
                      │
                      ▼
                PostgreSQL
                      │
                      ▼
              Provenance Record
                      │
                      ▼
              Verification API
```

PostgreSQL stores the provenance information and exposes it through the
backend API.

### Suggested record structure

``` text
provenance
--------------------------------
id
artifact_digest
provenance_hash
provenance_json
sbom_json
signature
builder_identity
source_repository
source_commit
timestamp
```

### Suggested endpoints

``` text
POST /provenance
GET  /provenance/{digest}
POST /verify
GET  /health
```

------------------------------------------------------------------------

## 4.2 Decentralized Backend --- System A

``` text
                 Provenance
                     │
            ┌────────┴────────┐
            ▼                 ▼
           IPFS           Blockchain
            │                 │
            │                 ├── Artifact Digest
            │                 ├── Provenance Hash
            │                 ├── IPFS CID
            │                 ├── Builder Identity
            │                 └── Timestamp
            │
            └── Complete provenance
                     │
                     ▼
              Verification API
```

### IPFS stores

-   Complete SLSA provenance
-   SBOM
-   Signature metadata
-   Other provenance information

### Blockchain stores

-   Artifact digest
-   Provenance hash
-   IPFS CID
-   Builder identity
-   Timestamp

The blockchain therefore acts as a tamper-evident commitment layer,
while IPFS stores the larger provenance object.

------------------------------------------------------------------------

# 5. Common Storage Interface

Create a storage abstraction between the verification service and the
two backends.

``` text
                 Verification API
                        │
                        ▼
                ProvenanceStore
                 /           \
                /             \
               ▼               ▼
      PostgreSQLStore      BlockchainIPFSStore
```

Conceptually:

``` python
class ProvenanceStore:

    def store(provenance):
        pass

    def retrieve(artifact_digest):
        pass

    def verify_commitment(provenance):
        pass
```

Implement:

``` text
PostgreSQLStore
BlockchainIPFSStore
```

The verification engine should not need to know whether the backend is
PostgreSQL or Blockchain + IPFS.

------------------------------------------------------------------------

# 6. Complete Development Roadmap

## Phase 0 --- Freeze Research Design

Before implementation:

1.  Define the research question.
2.  Define System A and System B.
3.  Define the metrics.
4.  Define the test dataset.
5.  Define the attack scenarios.
6.  Define the benchmark concurrency levels.
7.  Define the hardware/software environment.
8.  Decide what must remain identical between both systems.

### Research Question

> **What are the security, performance, storage, scalability, and
> availability trade-offs between centralized PostgreSQL and
> decentralized Blockchain + IPFS provenance storage when both are used
> by the same software supply-chain verification pipeline?**

------------------------------------------------------------------------

# Phase 1 --- Build the CI/CD Pipeline

## Goal

Automatically generate a trustworthy software artifact and its
verification evidence.

### Pipeline

``` text
Git Push
   ↓
GitHub Actions
   ↓
Docker Build
   ↓
Docker Image
   ↓
SHA-256 Digest
   ↓
SBOM Generation
   ↓
SLSA Provenance
   ↓
Cosign Signature
   ↓
Provenance Package
```

### Tasks

-   Create GitHub repository.
-   Create Dockerfile.
-   Configure GitHub Actions.
-   Build Docker image.
-   Push image to GHCR.
-   Obtain SHA-256 digest.
-   Generate SBOM using Syft.
-   Generate SLSA provenance.
-   Sign artifact/provenance using Cosign.
-   Verify generated signature and provenance.

### Deliverable

A reproducible pipeline:

``` text
Source Code
    ↓
Docker Image
    ↓
SBOM
    ↓
SLSA Provenance
    ↓
Cosign Signature
```

------------------------------------------------------------------------

# Phase 2 --- Build the Common Storage Interface

Create the abstraction first.

``` text
                 Provenance Package
                         │
                         ▼
                 Storage Interface
                    /          \
                   /            \
                  ▼              ▼
             PostgreSQL      Blockchain+IPFS
```

This is essential for the research comparison.

------------------------------------------------------------------------

# Phase 3 --- Implement Centralized PostgreSQL Backend

### Goal

Store and retrieve provenance through PostgreSQL.

### Tasks

1.  Create PostgreSQL database.
2.  Create provenance table.
3.  Build REST API.
4.  Implement registration.
5.  Implement retrieval by artifact digest.
6.  Implement hash verification.
7.  Implement health check.
8.  Connect it to the common storage interface.

### Deliverable

``` text
Artifact
   ↓
PostgreSQL Backend
   ↓
Provenance
   ↓
Verification API
   ↓
VALID
```

------------------------------------------------------------------------

# Phase 4 --- Implement Blockchain + IPFS Backend

## Step 4.1 --- IPFS

Implement:

``` text
Provenance JSON
      ↓
     IPFS
      ↓
     CID
```

Measure and log:

-   Upload time
-   Retrieval time
-   Object size
-   CID

## Step 4.2 --- Blockchain

Create Solidity smart contract.

Required operations:

``` text
registerProvenance()
verifyProvenance()
getProvenance()
```

Store:

``` text
artifactDigest
provenanceHash
ipfsCID
builderIdentity
timestamp
```

## Step 4.3 --- Connect IPFS and Blockchain

``` text
Complete Provenance
       │
       ├──────────────► IPFS
       │                   │
       │                   ▼
       │                  CID
       │
       └── Hash ───────► Blockchain
                            │
                            ├── Digest
                            ├── Hash
                            ├── CID
                            ├── Builder
                            └── Timestamp
```

### Deliverable

A fully functioning decentralized backend.

------------------------------------------------------------------------

# Phase 5 --- Build the Verification API

Use FastAPI as the common verification service.

### Verification sequence

``` text
Artifact Digest
      ↓
Provenance Retrieval
      ↓
Signature Verification
      ↓
SLSA Verification
      ↓
Source Verification
      ↓
Builder Verification
      ↓
Blockchain Hash Verification
      ↓
Final Result
```

### Result

``` text
All checks pass
      ↓
    VALID
```

or

``` text
Any required check fails
      ↓
TAMPERED / INVALID
```

------------------------------------------------------------------------

# Phase 6 --- Build the React Dashboard

Create a simple web dashboard showing:

``` text
Software Provenance Verifier

Artifact Digest: sha256:...

Backend:
[ PostgreSQL ]
or
[ Blockchain + IPFS ]

✓ Artifact Digest
✓ Cosign Signature
✓ SLSA Provenance
✓ Source Commit
✓ Builder Identity
✓ Provenance Hash

Result:
       VALID

Verification Time:
       XX ms
```

The same interface should work with both backends.

------------------------------------------------------------------------

# Phase 7 --- Functional Testing

Before benchmarking, verify that both systems are functionally correct.

  Test Case                        PostgreSQL   Blockchain + IPFS
  -------------------------------- ------------ -------------------
  Valid artifact                   VALID        VALID
  Modified artifact                INVALID      INVALID
  Invalid signature                INVALID      INVALID
  Missing provenance               INVALID      INVALID
  Wrong digest                     INVALID      INVALID
  Modified provenance              INVALID      INVALID
  Wrong builder                    INVALID      INVALID
  Wrong source commit              INVALID      INVALID
  Modified blockchain commitment   N/A          INVALID

Do not start performance testing until the functional tests pass.

------------------------------------------------------------------------

# Phase 8 --- Create a Fixed Benchmark Dataset

Prepare a controlled set of artifacts.

Example:

``` text
Artifact 001
Artifact 002
Artifact 003
...
Artifact 100
```

For every artifact record:

``` text
Artifact ID
Image Digest
Provenance Size
SBOM Size
Signature Size
Builder
Source Repository
Source Commit
```

Where possible, include different provenance sizes to study storage and
retrieval behavior.

------------------------------------------------------------------------

# Phase 9 --- Standardize the Experimental Environment

Use one controlled environment for both systems.

Example:

``` text
Linux
 │
 ├── Docker
 ├── PostgreSQL
 ├── IPFS/Kubo
 ├── Hardhat Blockchain
 ├── FastAPI
 ├── React
 └── Benchmark Tools
```

Keep:

-   CPU
-   RAM
-   disk
-   operating system
-   Docker configuration
-   network conditions
-   dataset
-   API implementation

as consistent as practical.

------------------------------------------------------------------------

# Phase 10 --- Performance Experiments

## Experiment 1 --- Verification Latency

Measure:

``` text
Request
   ↓
Final VALID/INVALID
```

Test:

``` text
1 concurrent request
10 concurrent requests
50 concurrent requests
100 concurrent requests
```

Record:

-   Minimum
-   Mean
-   Median
-   Maximum
-   p95
-   p99
-   Standard deviation

### Table

  --------------------------------------------------------------------------------
     Concurrency     PostgreSQL   Blockchain/IPFS PostgreSQL p95   Blockchain/IPFS
                           Mean              Mean                              p95
  -------------- -------------- ----------------- -------------- -----------------
               1                                                 

              10                                                 

              50                                                 

             100                                                 
  --------------------------------------------------------------------------------

------------------------------------------------------------------------

# Experiment 2 --- Throughput

Measure:

> **How many verification requests can each backend process per
> second?**

    Concurrency   PostgreSQL req/s   Blockchain + IPFS req/s
  ------------- ------------------ -------------------------
              1                    
             10                    
             50                    
            100                    

------------------------------------------------------------------------

# Experiment 3 --- Component-Level Latency

Break total verification time into:

``` text
Total Verification
       │
       ├── Backend retrieval
       ├── Blockchain lookup
       ├── IPFS retrieval
       ├── Hash computation
       ├── Signature verification
       └── SLSA verification
```

This helps explain **why** one backend is faster or slower.

------------------------------------------------------------------------

# Experiment 4 --- Storage Overhead

## PostgreSQL

Measure:

``` text
Database size
Record size
Index overhead
```

## Blockchain + IPFS

Measure separately:

``` text
IPFS storage
Blockchain storage
Transaction data
```

### Table

  Metric             PostgreSQL   IPFS   Blockchain
  ---------------- ------------ ------ ------------
  Per provenance                       
  100 artifacts                        
  1000 artifacts                       

------------------------------------------------------------------------

# Experiment 5 --- Blockchain Transaction Overhead

For every provenance registration measure:

``` text
Gas used
Transaction execution time
Block confirmation time
On-chain storage
```

This quantifies the additional cost of decentralization.

------------------------------------------------------------------------

# Experiment 6 --- IPFS Performance

Measure:

``` text
Upload time
CID generation time
Retrieval time
Failure rate
```

Test multiple provenance sizes, for example:

``` text
10 KB
100 KB
500 KB
1 MB
5 MB
```

This can show how provenance size affects decentralized retrieval.

------------------------------------------------------------------------

# Experiment 7 --- Tamper Detection

Create controlled attacks.

``` text
Original Artifact
       │
       ├── Modify artifact
       ├── Modify provenance
       ├── Modify digest
       ├── Change builder
       ├── Change source commit
       ├── Forge signature
       └── Modify stored commitment
```

Record:

  Attack                    Expected   Actual   Detected?   Detection Time
  ------------------------- ---------- -------- ----------- ----------------
  Artifact modification     INVALID                         
  Provenance modification   INVALID                         
  Wrong digest              INVALID                         
  Wrong builder             INVALID                         
  Wrong commit              INVALID                         
  Invalid signature         INVALID                         
  Wrong blockchain hash     INVALID                         

Calculate:

``` text
Tamper Detection Rate =
Detected Attacks / Total Attacks × 100
```

------------------------------------------------------------------------

# Experiment 8 --- Backend Failure / Availability

## PostgreSQL Failure

``` text
Verification Request
       ↓
PostgreSQL OFFLINE
       ↓
Observe system behavior
```

## IPFS Failure

``` text
Verification Request
       ↓
IPFS OFFLINE
       ↓
Observe system behavior
```

## Blockchain Failure

``` text
Verification Request
       ↓
Blockchain OFFLINE
       ↓
Observe system behavior
```

Record:

``` text
Failure type
Requests during failure
VALID results
DENIED results
Errors
Recovery time
```

------------------------------------------------------------------------

# Phase 11 --- Automate the Experiments

Do not manually run benchmarks.

Suggested project structure:

``` text
benchmark/
│
├── generate_dataset.py
├── benchmark_postgres.py
├── benchmark_blockchain.py
├── tamper_tests.py
├── failure_tests.py
├── collect_metrics.py
└── analyze_results.py

results/
│
├── latency.csv
├── throughput.csv
├── storage.csv
├── ipfs_latency.csv
├── blockchain.csv
├── tamper_detection.csv
└── availability.csv
```

The benchmark scripts should automatically:

1.  Select backend.
2.  Send requests.
3.  Record timestamps.
4.  Calculate metrics.
5.  Save raw data.
6.  Generate summary statistics.

------------------------------------------------------------------------

# Phase 12 --- Statistical Analysis

Do not compare systems using only one measured value.

For latency calculate:

-   Mean
-   Median
-   Standard deviation
-   p95
-   p99
-   Min
-   Max

For throughput calculate:

-   Requests/second
-   Successful requests
-   Failed requests

For security calculate:

-   Detection rate
-   False acceptance rate
-   False rejection rate

For availability calculate:

-   Failure rate
-   Recovery time
-   Successful recovery percentage

------------------------------------------------------------------------

# Phase 13 --- Generate Research Graphs

Recommended graphs:

### Graph 1 --- Latency vs Concurrency

``` text
X-axis: Concurrent Requests
Y-axis: Verification Latency (ms)

Lines:
PostgreSQL
Blockchain + IPFS
```

### Graph 2 --- Throughput vs Concurrency

``` text
X-axis: Concurrent Requests
Y-axis: Requests/second
```

### Graph 3 --- p95 Latency

``` text
X-axis: Concurrency
Y-axis: p95 latency
```

### Graph 4 --- Storage Growth

``` text
X-axis: Number of artifacts
Y-axis: Storage used
```

### Graph 5 --- IPFS Retrieval Time vs Provenance Size

``` text
X-axis: Provenance size
Y-axis: Retrieval latency
```

### Graph 6 --- Blockchain Registration Cost

``` text
X-axis: Number of registrations
Y-axis: Gas / transaction overhead
```

------------------------------------------------------------------------

# Phase 14 --- Research Results Tables

## Latency

  --------------------------------------------------------------------------------
     Concurrency     PostgreSQL   Blockchain/IPFS PostgreSQL p95   Blockchain/IPFS
                           Mean              Mean                              p95
  -------------- -------------- ----------------- -------------- -----------------
               1            TBD               TBD            TBD               TBD

              10            TBD               TBD            TBD               TBD

              50            TBD               TBD            TBD               TBD

             100            TBD               TBD            TBD               TBD
  --------------------------------------------------------------------------------

## Throughput

    Concurrency   PostgreSQL   Blockchain + IPFS
  ------------- ------------ -------------------
              1          TBD                 TBD
             10          TBD                 TBD
             50          TBD                 TBD
            100          TBD                 TBD

## Storage

  Metric              PostgreSQL   IPFS   Blockchain
  ----------------- ------------ ------ ------------
  Per attestation            TBD    TBD          TBD
  100 artifacts              TBD    TBD          TBD
  1000 artifacts             TBD    TBD          TBD

## Security

  Attack                           PostgreSQL   Blockchain + IPFS
  -------------------------------- ------------ -------------------
  Artifact modification            TBD          TBD
  Provenance modification          TBD          TBD
  Invalid signature                TBD          TBD
  Wrong digest                     TBD          TBD
  Wrong builder                    TBD          TBD
  Wrong source commit              TBD          TBD
  Modified blockchain commitment   N/A          TBD

------------------------------------------------------------------------

# Phase 15 --- Research Analysis

The final research question is:

> **Which architecture provides the better overall trade-off between
> security and performance?**

Compare:

``` text
                 RESEARCH COMPARISON
                         │
             ┌───────────┴───────────┐
             ▼                       ▼
       CENTRALIZED              DECENTRALIZED
       PostgreSQL               Blockchain + IPFS
             │                       │
             ├── Latency             ├── Latency
             ├── Throughput          ├── Throughput
             ├── Storage             ├── Storage
             ├── Security            ├── Security
             └── Availability        └── Availability
```

Do not assume that decentralization is automatically better.

The research should determine the trade-off from measured evidence.

------------------------------------------------------------------------

# 16. Recommended Development Order

Follow this exact order:

``` text
01. Define research question
        ↓
02. Freeze experimental variables
        ↓
03. Create sample software project
        ↓
04. Dockerize application
        ↓
05. Configure GitHub Actions
        ↓
06. Generate SBOM
        ↓
07. Generate SLSA provenance
        ↓
08. Configure Cosign signing
        ↓
09. Create common storage interface
        ↓
10. Build PostgreSQL backend
        ↓
11. Build IPFS backend
        ↓
12. Build blockchain smart contract
        ↓
13. Connect Blockchain + IPFS
        ↓
14. Build verification API
        ↓
15. Connect both backends
        ↓
16. Build React dashboard
        ↓
17. Functional testing
        ↓
18. Tamper/attack testing
        ↓
19. Create benchmark dataset
        ↓
20. Automate benchmarks
        ↓
21. Latency testing
        ↓
22. Throughput testing
        ↓
23. Storage testing
        ↓
24. IPFS/blockchain overhead testing
        ↓
25. Failure/availability testing
        ↓
26. Statistical analysis
        ↓
27. Generate graphs/tables
        ↓
28. Compare results
        ↓
29. Draw research conclusions
        ↓
30. Update IEEE research paper
```

------------------------------------------------------------------------

# 17. Suggested Milestones

  Milestone   Expected Result
  ----------- ------------------------------------------
  M1          Dockerized sample application
  M2          Working GitHub Actions CI/CD
  M3          SBOM + SLSA provenance generation
  M4          Cosign signing and verification
  M5          Common provenance storage interface
  M6          PostgreSQL backend working
  M7          IPFS backend working
  M8          Blockchain smart contract working
  M9          Blockchain + IPFS backend working
  M10         Common verification API working
  M11         React dashboard working
  M12         Functional security tests passing
  M13         Automated benchmark system
  M14         Performance experiments completed
  M15         Results analyzed
  M16         IEEE paper updated with measured results

------------------------------------------------------------------------

# 18. Final Deliverables

By the end of the project, you should have:

### Software

-   GitHub Actions CI/CD pipeline
-   Docker artifact
-   SBOM
-   SLSA provenance
-   Cosign signatures
-   PostgreSQL backend
-   IPFS backend
-   Blockchain smart contract
-   FastAPI verification service
-   React dashboard
-   Automated test suite
-   Automated benchmark suite

### Research Data

-   Latency dataset
-   Throughput dataset
-   Storage dataset
-   IPFS performance dataset
-   Blockchain transaction dataset
-   Tamper-detection dataset
-   Failure/recovery dataset

### Research Output

-   Comparison tables
-   Performance graphs
-   Security analysis
-   Statistical analysis
-   Discussion of trade-offs
-   Final conclusion
-   IEEE-format research paper

------------------------------------------------------------------------

# 19. Most Important Rule for the Project

The strongest part of your research design is:

``` text
             SAME PIPELINE
                   │
        ┌──────────┴──────────┐
        │                     │
        ▼                     ▼
   PostgreSQL          Blockchain + IPFS
   CENTRALIZED          DECENTRALIZED
        │                     │
        └──────────┬──────────┘
                   ▼
           SAME VERIFIER
                   │
                   ▼
          COMPARE RESULTS
```

**Only change the storage backend.**

Everything else should remain as identical as practical.

That gives you a clean experimental setup for answering:

> **How does decentralized provenance storage compare with centralized
> provenance storage in terms of tamper resistance, verification
> latency, throughput, storage overhead, and availability?**

------------------------------------------------------------------------

## Source Alignment

This roadmap is based on the project's synopsis and research-paper
design. The synopsis defines the SLSA + SBOM + Cosign + IPFS +
blockchain verification framework, while the research paper defines the
interchangeable decentralized and centralized storage architectures and
the experimental comparison methodology.

Key source sections:

-   Project introduction and architecture
-   Objectives and scope
-   End-to-end methodology
-   Security testing
-   Performance testing
-   Evaluation metrics
-   Research comparison methodology
