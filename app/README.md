# SLSA Demo Application

A simple Flask web API that serves as the **sample application** for our SLSA software supply-chain provenance verification research project.

## 📋 What This App Does

This Flask application provides a minimal web API with four endpoints:

- **`GET /`** - Home page with basic app info
- **`GET /health`** - Health check for container orchestration  
- **`GET /api/artifact-info`** - Metadata about this software artifact
- **`POST /api/echo`** - Simple echo service for testing

## 🎯 Why This App Exists

This isn't meant to be a complex application. It's intentionally simple because **we're focusing on the supply chain, not the app logic.**

This app will be:
1. **Built** into a Docker image with a reproducible SHA-256 digest
2. **Tracked** through a CI/CD pipeline with SLSA provenance generation
3. **Signed** with Cosign/Sigstore signatures
4. **Verified** using two different storage backends (PostgreSQL vs Blockchain+IPFS)

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
```bash
cd app/
pip install -r requirements.txt
```

2. **Run the application:**
```bash
python src/app.py
```

3. **Test it works:**
```bash
curl http://localhost:5000/
curl http://localhost:5000/health
```

### Run Tests

```bash
cd app/
pip install pytest
python -m pytest tests/ -v
```

## 📊 Endpoints Reference

### `GET /` - Home
```json
{
  "message": "SLSA Provenance Demo Application",
  "app": "slsa-demo-app", 
  "version": "1.0.0",
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### `GET /health` - Health Check
```json
{
  "status": "healthy",
  "app": "slsa-demo-app",
  "version": "1.0.0", 
  "build_timestamp": "2024-01-01T10:00:00Z",
  "uptime_seconds": 3600,
  "python_version": "3.11.0",
  "environment": "development"
}
```

### `GET /api/artifact-info` - Artifact Metadata
```json
{
  "artifact": {
    "name": "slsa-demo-app",
    "version": "1.0.0",
    "build_timestamp": "2024-01-01T10:00:00Z",
    "source_repo": "https://github.com/YOUR_USERNAME/slsa-demo",
    "builder": "github-actions", 
    "build_environment": "ubuntu-latest"
  },
  "endpoints": [...]
}
```

### `POST /api/echo` - Echo Service
**Request:**
```json
{
  "message": "Hello SLSA!",
  "test": true
}
```

**Response:**
```json
{
  "echo": {
    "message": "Hello SLSA!",
    "test": true
  },
  "received_at": "2024-01-01T12:00:00Z",
  "processed_by": "slsa-demo-app",
  "version": "1.0.0"
}
```

## 🔧 Configuration

The app uses environment variables for configuration:

- **`FLASK_HOST`** - Host to bind to (default: 0.0.0.0)
- **`FLASK_PORT`** - Port to listen on (default: 5000)
- **`FLASK_ENV`** - Environment mode (development/production)
- **`ENVIRONMENT`** - App environment identifier
- **`LOG_LEVEL`** - Logging level (INFO, DEBUG, etc.)

Copy `.env.example` to `.env` and customize as needed.

## 🏗️ What's Next?

This app is **Stage A1** of our development roadmap. Next steps:

- **Stage A2:** Dockerize this application  
- **Stage A3:** Set up GitHub Actions CI/CD
- **Stage A4:** Generate SBOM (Software Bill of Materials)
- **Stage A5:** Generate SLSA provenance
- **Stage A6:** Sign with Cosign
- And so on...

See `../DEVELOPMENT_ROADMAP.md` for the complete plan.

## 🧪 Testing the Supply Chain

Once the full pipeline is built, you'll be able to:

1. Push code to GitHub → Automatic build with provenance
2. Verify any artifact: `curl -X POST /verify -d '{"digest": "sha256:abc123..."}'`
3. Compare PostgreSQL vs Blockchain+IPFS verification performance
4. Generate research data on centralized vs decentralized storage trade-offs

---

**Remember:** This simple app is just the beginning. The real project is building the secure, verifiable supply chain around it! 🔒