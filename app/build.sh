#!/bin/bash
# Build script for SLSA Demo App Docker image
# This script builds the image and captures the SHA-256 digest

set -e  # Exit on any error

echo "🔨 Building SLSA Demo App Docker Image"
echo "======================================"

# Set build metadata
BUILD_DATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
VERSION="${VERSION:-1.0.0}"

echo "📋 Build Info:"
echo "   - Build Date: ${BUILD_DATE}"
echo "   - VCS Reference: ${VCS_REF}"
echo "   - Version: ${VERSION}"
echo ""

# Build the Docker image
echo "🔨 Building Docker image..."
docker build \
    --build-arg BUILD_DATE="${BUILD_DATE}" \
    --build-arg VCS_REF="${VCS_REF}" \
    --build-arg VERSION="${VERSION}" \
    -t slsa-demo-app:latest \
    -t slsa-demo-app:${VERSION} \
    .

echo ""
echo "✅ Docker build completed successfully!"

# Get the image digest
echo "🔍 Extracting image digest..."
DIGEST=$(docker images --digests slsa-demo-app:latest --format "table {{.Digest}}" | tail -n 1)
IMAGE_ID=$(docker images slsa-demo-app:latest --format "table {{.ID}}" | tail -n 1)

if [ "$DIGEST" = "<none>" ] || [ -z "$DIGEST" ]; then
    echo "⚠️  Local build - no registry digest available"
    echo "   Image ID: ${IMAGE_ID}"
    echo "   💡 Push to registry to get SHA-256 digest for provenance"
else
    echo "   SHA-256 Digest: ${DIGEST}"
fi

echo ""
echo "📊 Image Information:"
docker images slsa-demo-app:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedSince}}\t{{.Size}}"

echo ""
echo "🧪 Testing the built image..."
echo "Starting container for health check..."

# Start container in background
CONTAINER_ID=$(docker run -d -p 5000:5000 slsa-demo-app:latest)

# Wait for container to start
sleep 5

# Test health endpoint
if curl -f -s http://localhost:5000/health > /dev/null; then
    echo "✅ Health check passed!"
    
    # Test artifact info endpoint
    echo "🔍 Testing artifact info endpoint..."
    curl -s http://localhost:5000/api/artifact-info | python3 -m json.tool | head -10
else
    echo "❌ Health check failed!"
    docker logs $CONTAINER_ID
fi

# Cleanup
echo ""
echo "🧹 Cleaning up test container..."
docker stop $CONTAINER_ID > /dev/null
docker rm $CONTAINER_ID > /dev/null

echo ""
echo "🎯 Build Summary:"
echo "   - Image: slsa-demo-app:latest"
echo "   - Image: slsa-demo-app:${VERSION}"
echo "   - Image ID: ${IMAGE_ID}"
echo "   - Build Date: ${BUILD_DATE}"
echo "   - VCS Ref: ${VCS_REF}"
echo ""
echo "🚀 Ready for Stage A3 (GitHub Actions CI/CD)!"
echo "   Next: Set up automated builds with provenance generation"