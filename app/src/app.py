#!/usr/bin/env python3
"""
Simple Flask API for SLSA Provenance Verification Demo

This is our "sample application" - the software artifact that will be:
1. Built into a Docker image
2. Tracked through the CI/CD pipeline
3. Verified using SLSA provenance
4. Stored in both PostgreSQL and Blockchain+IPFS backends

The app itself is intentionally simple - we're focusing on the supply chain, not the app logic.
"""

import os
import time
from datetime import datetime, timezone
from flask import Flask, jsonify, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# App metadata - this will be included in SBOM and provenance
APP_VERSION = "1.0.0"
APP_NAME = "slsa-demo-app"
BUILD_TIMESTAMP = datetime.now(timezone.utc).isoformat()


@app.route("/", methods=["GET"])
def home():
    """
    Home endpoint - proves the app is running
    """
    return jsonify({
        "message": "SLSA Provenance Demo Application",
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint for container orchestration
    Returns app status and basic system info
    """
    return jsonify({
        "status": "healthy",
        "app": APP_NAME,
        "version": APP_VERSION,
        "build_timestamp": BUILD_TIMESTAMP,
        "uptime_seconds": time.time() - start_time,
        "python_version": os.sys.version,
        "environment": os.getenv("ENVIRONMENT", "development")
    })


@app.route("/api/artifact-info", methods=["GET"])
def artifact_info():
    """
    Returns information about this software artifact
    This data will later be verified against SLSA provenance
    """
    return jsonify({
        "artifact": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "build_timestamp": BUILD_TIMESTAMP,
            "source_repo": "https://github.com/YOUR_USERNAME/slsa-demo",  # Will update in CI/CD
            "builder": "github-actions",
            "build_environment": "ubuntu-latest"
        },
        "endpoints": [
            {"path": "/", "method": "GET", "description": "Home page"},
            {"path": "/health", "method": "GET", "description": "Health check"},
            {"path": "/api/artifact-info", "method": "GET", "description": "Artifact metadata"},
            {"path": "/api/echo", "method": "POST", "description": "Echo service"}
        ]
    })


@app.route("/api/echo", methods=["POST"])
def echo():
    """
    Simple echo service for testing
    Accepts JSON and returns it with metadata
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        return jsonify({
            "echo": data,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "processed_by": APP_NAME,
            "version": APP_VERSION
        })
    except Exception as e:
        logger.error(f"Echo endpoint error: {str(e)}")
        return jsonify({"error": "Invalid JSON data"}), 400


@app.errorhandler(404)
def not_found(error):
    """Custom 404 handler"""
    return jsonify({
        "error": "Endpoint not found",
        "app": APP_NAME,
        "available_endpoints": ["/", "/health", "/api/artifact-info", "/api/echo"]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal server error",
        "app": APP_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }), 500


if __name__ == "__main__":
    # Record start time for uptime calculation
    start_time = time.time()
    
    # Get configuration from environment
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_ENV") == "development"
    
    logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
    logger.info(f"Build timestamp: {BUILD_TIMESTAMP}")
    logger.info(f"Listening on {host}:{port}")
    
    app.run(host=host, port=port, debug=debug)
else:
    # When running with gunicorn, initialize start_time at module level
    start_time = time.time()