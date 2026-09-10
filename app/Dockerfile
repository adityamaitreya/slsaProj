# Multi-stage Dockerfile for SLSA Demo Application
# This creates a secure, minimal production image for our Flask app

#==============================================================================
# STAGE 1: Build Dependencies
# Use a full Python image to install dependencies and prepare the app
#==============================================================================
FROM python:3.11-slim as builder

# Set build arguments for reproducible builds
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first (for better layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --user --no-warn-script-location -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY tests/ ./tests/

# Verify the application can import (basic smoke test)
RUN python -c "import sys; sys.path.insert(0, 'src'); from app import app; print('✅ App imports successfully')"

#==============================================================================
# STAGE 2: Production Runtime
# Use a minimal image with only what's needed to run the app
#==============================================================================
FROM python:3.11-slim as runtime

# Set build metadata (will appear in image labels)
ARG BUILD_DATE
ARG VCS_REF  
ARG VERSION=1.0.0

# Add metadata labels (following OCI standards)
LABEL org.opencontainers.image.title="SLSA Demo Application" \
      org.opencontainers.image.description="Flask app for SLSA provenance verification research" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.created="${BUILD_DATE}" \
      org.opencontainers.image.revision="${VCS_REF}" \
      org.opencontainers.image.vendor="SLSA Research Project" \
      org.opencontainers.image.source="https://github.com/YOUR_USERNAME/slsa-demo"

# Set production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    FLASK_ENV=production \
    FLASK_HOST=0.0.0.0 \
    FLASK_PORT=5000 \
    PATH="/home/appuser/.local/bin:$PATH"

# Create non-root user for security
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Create directory for logs (if needed)
RUN mkdir -p /app/logs && chown appuser:appuser /app/logs

# Switch to non-root user
USER appuser

# Verify the application works
RUN python -c "from src.app import app; print('✅ Production image ready')"

# Expose the application port
EXPOSE 5000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Use gunicorn for production serving
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "--error-logfile", "-", "src.app:app"]