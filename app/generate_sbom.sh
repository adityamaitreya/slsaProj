#!/bin/bash
# Generate SBOM (Software Bill of Materials) locally using Syft

set -e

echo "📦 Generating SBOM for SLSA Demo App"
echo "===================================="

IMAGE_NAME="slsa-demo-app:latest"

# Check if Syft is installed
if ! command -v syft &> /dev/null; then
    echo "⚠️  Syft not found. Installing..."
    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
    echo "✅ Syft installed"
fi

echo ""
echo "🔍 Syft version:"
syft version

echo ""
echo "📊 Scanning Docker image: $IMAGE_NAME"
echo ""

# Generate SBOM in multiple formats
echo "Generating SPDX format..."
sudo syft $IMAGE_NAME -o spdx-json=sbom.spdx.json

echo "Generating CycloneDX format..."
sudo syft $IMAGE_NAME -o cyclonedx-json=sbom.cyclonedx.json

echo "Generating Syft JSON format..."
sudo syft $IMAGE_NAME -o json=sbom.syft.json

echo "Generating human-readable table..."
sudo syft $IMAGE_NAME -o table=sbom.txt

echo ""
echo "✅ SBOM Generation Complete!"
echo ""
echo "📁 Files created:"
ls -lh sbom.* 2>/dev/null || echo "No SBOM files found"

echo ""
echo "📊 SBOM Summary:"
if [ -f "sbom.syft.json" ]; then
    package_count=$(jq '.artifacts | length' sbom.syft.json 2>/dev/null || echo "0")
    echo "   Total packages detected: $package_count"
    
    echo ""
    echo "📦 Top 10 packages:"
    jq -r '.artifacts[:10] | .[] | "   - \(.name) (\(.version // "unknown"))"' sbom.syft.json 2>/dev/null || echo "   Could not parse packages"
fi

echo ""
echo "🔍 View full SBOM:"
echo "   Human-readable: cat sbom.txt"
echo "   SPDX JSON:      cat sbom.spdx.json | jq"
echo "   CycloneDX JSON: cat sbom.cyclonedx.json | jq"
echo "   Syft JSON:      cat sbom.syft.json | jq"

echo ""
echo "💡 What is SBOM?"
echo "   Software Bill of Materials (SBOM) lists all components, libraries,"
echo "   and dependencies in your software. It's like an ingredient label"
echo "   for software, helping with:"
echo "   - Vulnerability tracking (e.g., Log4Shell detection)"
echo "   - License compliance"
echo "   - Supply chain security"
echo "   - Audit and transparency"