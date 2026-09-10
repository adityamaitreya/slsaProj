# SBOM (Software Bill of Materials) Guide

## 🎯 What is SBOM?

A **Software Bill of Materials (SBOM)** is a comprehensive list of all components, libraries, and dependencies in your software - like an ingredient label for software.

### Why SBOM Matters for Supply Chain Security

1. **Vulnerability Detection**
   - Quickly identify if your software contains vulnerable libraries
   - Example: Detect Log4Shell (CVE-2021-44228) instantly
   - Track security advisories for all dependencies

2. **License Compliance**
   - Know what open-source licenses you're using
   - Avoid license conflicts
   - Meet legal requirements

3. **Supply Chain Transparency**
   - Prove what's in your software
   - Verify integrity of dependencies
   - Track changes over time

4. **Incident Response**
   - When a vulnerability is announced, instantly know if you're affected
   - No manual dependency hunting
   - Faster patching decisions

---

## 📦 SBOM Formats

Our pipeline generates SBOMs in three industry-standard formats:

### 1. SPDX (Software Package Data Exchange)
- **Standard:** ISO/IEC 5962:2021
- **Created by:** Linux Foundation
- **Format:** JSON, XML, YAML, Tag-Value
- **Use case:** Most widely adopted, government requirements

### 2. CycloneDX
- **Standard:** OWASP/ECMA
- **Created by:** OWASP
- **Format:** JSON, XML
- **Use case:** Security-focused, vulnerability tracking

### 3. Syft JSON
- **Created by:** Anchore
- **Format:** JSON
- **Use case:** Detailed metadata, Grype vulnerability scanning

---

## 🔧 How SBOM Generation Works

### In GitHub Actions (Automatic)

```yaml
# From .github/workflows/build.yml

1. Build Docker image
2. Push to GHCR
3. Install Syft tool
4. Run: syft <image>@<digest> -o spdx-json
5. Upload SBOM as artifact
```

### Locally (Manual)

```bash
cd app
./generate_sbom.sh
```

This will:
1. Check if Syft is installed (install if not)
2. Scan the local Docker image
3. Generate SBOM in multiple formats
4. Display summary

---

## 📊 SBOM Contents

An SBOM typically includes:

### Package Information
```json
{
  "name": "flask",
  "version": "3.0.0",
  "type": "python",
  "foundBy": "python-package-cataloger",
  "licenses": ["BSD-3-Clause"],
  "language": "python",
  "cpes": ["cpe:2.3:a:flask:flask:3.0.0:*:*:*:*:*:*:*"],
  "purl": "pkg:pypi/flask@3.0.0"
}
```

### Relationship Data
- Which packages depend on what
- Transitive dependencies
- Dependency graph

### Provenance Data
- Where the package came from
- How it was discovered
- Package registry information

---

## 🔍 Reading SBOM Files

### View SPDX SBOM
```bash
cat sbom.spdx.json | jq '.packages[] | {name, version, licenseConcluded}'
```

### View CycloneDX SBOM
```bash
cat sbom.cyclonedx.json | jq '.components[] | {name, version, licenses}'
```

### View Syft SBOM
```bash
cat sbom.syft.json | jq '.artifacts[] | {name, version, type}'
```

### Count total packages
```bash
jq '.artifacts | length' sbom.syft.json
```

### Find specific package
```bash
jq '.artifacts[] | select(.name == "flask")' sbom.syft.json
```

---

## 🛡️ Using SBOM for Vulnerability Scanning

### With Grype (Anchore's vulnerability scanner)

```bash
# Install Grype
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin

# Scan using SBOM
grype sbom:sbom.syft.json

# Or scan image directly
grype slsa-demo-app:latest
```

### With Trivy (Already in our pipeline)

```bash
trivy sbom sbom.spdx.json
```

---

## 📝 SBOM in Our Supply Chain

### Current Pipeline Flow

```
Code → Build → Docker Image → SBOM Generation
                    ↓              ↓
               SHA-256 Digest   SBOM Files
                    ↓              ↓
              SLSA Provenance ← References SBOM
                    ↓
             Cosign Signature
                    ↓
          Storage (PostgreSQL / Blockchain)
```

### SBOM Integration Points

1. **Generation** (Stage A4 - Current)
   - Syft scans Docker image
   - Generates SPDX, CycloneDX, Syft formats
   - Uploaded as build artifacts

2. **Storage** (Stage A8-A9)
   - SBOM stored with provenance
   - Linked to artifact digest
   - Queryable via API

3. **Verification** (Stage A11)
   - Verify SBOM hasn't been tampered
   - Check SBOM matches actual dependencies
   - Validate SBOM signature

4. **Analysis** (Phase C)
   - Track SBOM size over time
   - Compare dependency counts
   - Measure SBOM generation performance

---

## 🎯 SBOM Best Practices

### 1. Generate at Build Time
- ✅ Automated in CI/CD
- ✅ Always up-to-date
- ❌ Don't generate manually

### 2. Reference by Digest
```bash
# Good: Tied to specific image
syft image@sha256:abc123... -o spdx-json

# Bad: Tag can change
syft image:latest -o spdx-json
```

### 3. Store with Provenance
- SBOM is part of the artifact's metadata
- Store together with SLSA provenance
- Sign both together

### 4. Use Standard Formats
- SPDX for government/compliance
- CycloneDX for security teams
- Both are widely supported

### 5. Automate Vulnerability Checks
- Scan SBOM regularly
- Alert on new vulnerabilities
- Track remediation status

---

## 📊 Example SBOM Summary

For our `slsa-demo-app`, the SBOM typically contains:

```
Total Packages: ~150-200

Main Components:
- Python 3.11 runtime
- Flask 3.0.0 (web framework)
- Gunicorn 21.2.0 (WSGI server)
- Werkzeug 3.0.1 (WSGI utilities)
- All transitive dependencies

System Libraries:
- glibc, openssl, zlib, etc.
- from base Python image
```

---

## 🔗 SBOM Standards & Resources

### Official Standards
- **SPDX:** https://spdx.dev/
- **CycloneDX:** https://cyclonedx.org/
- **NTIA SBOM Guidelines:** https://www.ntia.gov/sbom

### Tools
- **Syft:** https://github.com/anchore/syft
- **Grype:** https://github.com/anchore/grype (vulnerability scanning)
- **SBOM Tool:** https://github.com/microsoft/sbom-tool (Microsoft)

### Why Multiple Formats?
- **SPDX:** Required by US government, most mature standard
- **CycloneDX:** Better for security use cases, vulnerability data
- **Both:** Interoperable, use what your tools support

---

## ✅ Stage A4 Success Criteria

Our SBOM implementation is complete when:

- [x] Syft integrated into GitHub Actions
- [x] SBOM generated in SPDX format
- [x] SBOM generated in CycloneDX format
- [x] SBOM uploaded as build artifact
- [ ] SBOM accessible in workflow artifacts (after next push)
- [ ] SBOM references correct image digest (after next push)

---

## 🚀 What's Next?

### Stage A5: SLSA Provenance
- SLSA provenance will **reference** the SBOM
- Proves: "This artifact has digest X, with SBOM Y"
- Links everything together cryptographically

### Stage A6: Cosign Signing
- Sign both provenance AND SBOM
- Proves: "Nobody tampered with the SBOM"
- Enables verification

---

## 💡 Key Takeaways

1. **SBOM = Ingredient Label** for software
2. **Generated automatically** in our CI/CD pipeline
3. **Three formats** for maximum compatibility
4. **Enables vulnerability tracking** without manual work
5. **Part of SLSA provenance** - not separate
6. **Signed with Cosign** - tamper-evident

SBOMs are now a **requirement** for:
- US Federal government software
- Critical infrastructure
- Many enterprise customers
- Supply chain security best practices

---

*Generated as part of Stage A4: SBOM Generation*