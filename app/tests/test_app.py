#!/usr/bin/env python3
"""
Basic tests for the SLSA Demo Flask application

These tests verify that our sample application works correctly.
Later, we'll add tests that verify SLSA provenance and SBOM contents.
"""

import json
import pytest
import sys
import os

# Add src directory to path so we can import our app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app, APP_NAME, APP_VERSION


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    """Test the home endpoint returns expected data"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['app'] == APP_NAME
    assert data['version'] == APP_VERSION
    assert data['status'] == 'healthy'
    assert 'timestamp' in data


def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['app'] == APP_NAME
    assert data['version'] == APP_VERSION
    assert 'uptime_seconds' in data
    assert 'python_version' in data


def test_artifact_info_endpoint(client):
    """Test the artifact info endpoint"""
    response = client.get('/api/artifact-info')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'artifact' in data
    assert data['artifact']['name'] == APP_NAME
    assert data['artifact']['version'] == APP_VERSION
    assert 'endpoints' in data
    assert len(data['endpoints']) >= 4


def test_echo_endpoint_valid_json(client):
    """Test the echo endpoint with valid JSON"""
    test_data = {"message": "Hello SLSA!", "test": True}
    response = client.post('/api/echo',
                          data=json.dumps(test_data),
                          content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['echo'] == test_data
    assert data['processed_by'] == APP_NAME
    assert 'received_at' in data


def test_echo_endpoint_no_json(client):
    """Test the echo endpoint with no JSON data"""
    response = client.post('/api/echo')
    assert response.status_code == 400
    
    data = json.loads(response.data)
    assert 'error' in data


def test_echo_endpoint_invalid_json(client):
    """Test the echo endpoint with invalid JSON"""
    response = client.post('/api/echo',
                          data="invalid json",
                          content_type='application/json')
    assert response.status_code == 400


def test_404_handler(client):
    """Test custom 404 handler"""
    response = client.get('/nonexistent-endpoint')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data
    assert data['app'] == APP_NAME
    assert 'available_endpoints' in data


if __name__ == '__main__':
    # Run tests when executed directly
    pytest.main([__file__, '-v'])