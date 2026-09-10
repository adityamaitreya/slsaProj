# GitHub Actions CI/CD Setup Guide

## 🎯 Purpose
This guide helps you set up GitHub Actions for automated Docker builds and supply chain tracking.

---

## 📋 Prerequisites

1. **GitHub Account** - You need a GitHub account
2. **Git Installed** - Check with `git --version`
3. **GitHub CLI (optional)** - Makes setup easier: `gh --version`

---

## 🚀 Quick Setup Steps

### Step 1: Initialize Git Repository

```bash
cd /home/byte/Desktop/projX
git init
git add .
git commit -m "Initial commit: SLSA demo app with Docker setup"
```

### Step 2: Create GitHub Repository

#### Option A: Using GitHub CLI (Recommended)
```bash
# Login to GitHub
gh auth login

# Create repository
gh repo create slsa-demo --public --source=. --remote=origin --push

# Set default branch to main
git branch -M main
```

#### Option B: Using GitHub Web Interface
1. Go to https://github.com/new
2. Repository name: `slsa-demo`
3. Description: "SLSA software supply chain provenance verification project"
4. Make it **Public** (required for free GitHub Actions and GHCR)
5. **Do NOT** initialize with README (we already have files)
6. Click "Create repository"
7. Follow the commands shown to push existing repository:

```bash
git remote add origin https://github.com/YOUR_USERNAME/slsa-demo.git
git branch -M main
git push -u origin main
```

### Step 3: Enable GitHub Container Registry (GHCR)

GHCR is automatically available for your repository. No additional setup needed!

Your Docker images will be pushed to:
```
ghcr.io/YOUR_USERNAME/slsa-demo
```

### Step 4: Verify GitHub Actions

1. Go to your repository on GitHub
2. Click the **"Actions"** tab
3. You should see two workflows:
   - ✅ Build and Push Docker Image
   - ✅ Run Tests

4. The build workflow should trigger automatically on your first push

### Step 5: Check Your First Build

After pushing code, GitHub Actions will:
1. ✅ Run tests
2. ✅ Build Docker image
3. ✅ Push to GHCR at `ghcr.io/YOUR_USERNAME/slsa-demo`
4. ✅ Generate image digest (SHA-256)
5. ✅ Run security scan

---

## 🔐 GitHub Container Registry Permissions

### Making Your Images Public

By default, GHCR packages are private. To make them public:

1. Go to your GitHub profile → Packages
2. Find `slsa-demo` package
3. Click on it → Package settings
4. Scroll down to "Danger Zone"
5. Click "Change visibility" → Make public

---

## 📦 Pulling Your Image

After successful build:

```bash
# Pull by tag
docker pull ghcr.io/YOUR_USERNAME/slsa-demo:latest

# Pull by digest (for supply chain verification)
docker pull ghcr.io/YOUR_USERNAME/slsa-demo@sha256:abc123...

# Run the container
docker run -p 5000:5000 ghcr.io/YOUR_USERNAME/slsa-demo:latest
```

---

## 🎯 What This Achieves for Supply Chain Security

### Before (Local Build)
- ❌ "I built this on my laptop"
- ❌ No proof of build environment
- ❌ Can't verify when/where/how it was built
- ❌ Digest changes if anyone rebuilds

### After (GitHub Actions Build)
- ✅ "GitHub Actions built this"
- ✅ Exact commit SHA recorded
- ✅ Build timestamp recorded
- ✅ Reproducible build environment
- ✅ Immutable digest: `sha256:abc123...`
- ✅ Traceable builder identity
- ✅ Ready for SLSA provenance (Stage A5)

---

## 🔍 Understanding the Digest

Every Docker build produces a **digest** (SHA-256 hash):

```
sha256:45fae577dc363271229ad6e8309a5b2e971f8b3e0c4d1a8f6c7b9d0e1f2a3b4c
```

This digest:
- 🔒 **Uniquely identifies** this exact image
- 🔒 **Changes if anything changes** (even 1 byte)
- 🔒 **Can't be faked** or manipulated
- 🔒 **Becomes our artifact fingerprint** for supply chain tracking

In later stages, we'll:
- Generate SLSA provenance that references this digest
- Store the digest + provenance in PostgreSQL / Blockchain
- Verify that the running container matches the signed digest

---

## 🧪 Testing the CI/CD Pipeline

### Test 1: Make a small change
```bash
cd /home/byte/Desktop/projX/app/src
echo "# Test change" >> app.py
git add app.py
git commit -m "test: trigger CI/CD pipeline"
git push
```

Watch the Actions tab - you should see a new workflow run!

### Test 2: Check the build output
```bash
# List workflow runs
gh run list

# View specific run
gh run view

# View logs
gh run view --log
```

### Test 3: Pull and test the image
```bash
docker pull ghcr.io/YOUR_USERNAME/slsa-demo:latest
docker run -p 5000:5000 ghcr.io/YOUR_USERNAME/slsa-demo:latest

# Test in another terminal
curl http://localhost:5000/health
```

---

## 📊 GitHub Actions Workflow Files

Two workflow files created:

### 1. `.github/workflows/build.yml`
- Builds Docker image
- Pushes to GHCR
- Extracts digest
- Runs security scan
- **This is the foundation for SLSA provenance**

### 2. `.github/workflows/test.yml`
- Runs Python tests
- Checks code quality
- Runs before Docker build

---

## 🐛 Troubleshooting

### Error: "Permission denied while pushing to GHCR"
- Check that your repo is public (GHCR free tier requires public repos)
- Verify the `packages: write` permission is set in workflow file

### Error: "Failed to build Docker image"
- Check the build logs in Actions tab
- Verify Dockerfile syntax locally: `docker build -t test ./app`

### Error: "Tests failed"
- Run tests locally first: `cd app && python -m pytest tests/ -v`
- Check Python version matches (3.11)

### Can't find the image on GHCR
- Wait for workflow to complete (check Actions tab)
- Verify you're looking at the right username
- Check if image is set to private (change to public)

---

## ✅ Stage A3 Completion Checklist

- [ ] Git repository initialized
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] GitHub Actions workflows triggered
- [ ] Docker image built successfully
- [ ] Image pushed to GHCR
- [ ] Image digest captured
- [ ] Security scan completed
- [ ] Can pull and run image from GHCR

---

## 🚀 Next Steps

Once Stage A3 is complete:
- **Stage A4:** Generate SBOM with Syft
- **Stage A5:** Generate SLSA provenance
- **Stage A6:** Sign with Cosign

Your CI/CD pipeline is now the **trusted builder** for your supply chain!

---

## 📝 Important Notes

### Repository Visibility
- **Public repos:** Free GitHub Actions (2000 minutes/month) + free GHCR
- **Private repos:** Limited free minutes, GHCR charges may apply

### Secrets and Tokens
- `GITHUB_TOKEN` is automatically provided by GitHub Actions
- No additional secrets needed for basic GHCR push
- Later stages may need additional secrets for signing

### Image Storage
- GHCR free tier: 500MB storage for public packages
- Old images can be deleted manually if needed
- Use retention policies in production

---

## 🎓 Key Concepts Learned

1. **Trusted Builder**: GitHub Actions = reproducible, auditable build environment
2. **Immutable Artifacts**: Docker digest = unique fingerprint
3. **Traceability**: Every build tied to exact commit SHA
4. **Automation**: Push code → auto-build → auto-publish
5. **Supply Chain Foundation**: Ready for provenance generation

This CI/CD setup is the cornerstone of our SLSA supply chain verification system!