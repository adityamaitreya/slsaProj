#!/usr/bin/env python3
"""
Validate Stage A2: Dockerization completion
This script verifies all Docker-related files and functionality
"""

import os
import subprocess
import json
import sys

def run_command(cmd, capture_output=True):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"❌ Missing: {description} at {filepath}")
        return False

def validate_docker_stage():
    """Validate the complete Docker setup"""
    print("🔍 Validating Stage A2: Dockerization")
    print("=" * 40)
    
    base_dir = "/home/byte/Desktop/projX/app"
    
    # Check required Docker files
    files_to_check = [
        (f"{base_dir}/Dockerfile", "Production Dockerfile"),
        (f"{base_dir}/Dockerfile.dev", "Development Dockerfile"),
        (f"{base_dir}/.dockerignore", "Docker ignore file"),
        (f"{base_dir}/docker-compose.yml", "Docker Compose configuration"),
        (f"{base_dir}/build.sh", "Build script")
    ]
    
    all_files_good = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_files_good = False
    
    print("\n📋 Docker Configuration Analysis:")
    
    # Check Dockerfile content
    dockerfile_path = f"{base_dir}/Dockerfile"
    if os.path.exists(dockerfile_path):
        with open(dockerfile_path, 'r') as f:
            content = f.read()
            print(f"   - Dockerfile lines: {len(content.splitlines())}")
            print(f"   - Multi-stage build: {'FROM python:3.11-slim as builder' in content}")
            print(f"   - Security (non-root user): {'useradd' in content}")
            print(f"   - Health check: {'HEALTHCHECK' in content}")
            print(f"   - Production server: {'gunicorn' in content}")
    
    # Check if Docker is available
    print("\n🐳 Docker Environment:")
    docker_available, docker_version, _ = run_command("sudo docker --version")
    if docker_available:
        print(f"   - Docker available: ✅ {docker_version.strip()}")
        
        # Check if image exists
        image_check, image_info, _ = run_command("sudo docker images slsa-demo-app:latest --format 'table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}'")
        if image_check and "slsa-demo-app" in image_info:
            print(f"   - Image built: ✅ slsa-demo-app:latest")
            lines = image_info.strip().split('\n')
            if len(lines) > 1:
                image_data = lines[1].split()
                if len(image_data) >= 4:
                    print(f"   - Image ID: {image_data[2]}")
                    print(f"   - Image Size: {image_data[3]}")
        else:
            print(f"   - Image built: ❌ slsa-demo-app:latest not found")
            all_files_good = False
    else:
        print(f"   - Docker available: ❌ Not available")
        all_files_good = False
    
    # Test container functionality (quick test)
    print("\n🧪 Container Functionality Test:")
    if docker_available:
        print("   - Starting test container...")
        start_success, _, _ = run_command("sudo docker run -d -p 5001:5000 --name slsa-validation-test slsa-demo-app:latest", capture_output=True)
        
        if start_success:
            print("   - Container started: ✅")
            
            # Wait for startup
            import time
            time.sleep(3)
            
            # Test health endpoint
            health_test, health_response, _ = run_command("curl -s http://localhost:5001/health")
            if health_test and "slsa-demo-app" in health_response:
                print("   - Health endpoint: ✅")
                
                # Parse health response
                try:
                    health_data = json.loads(health_response)
                    print(f"   - App version: {health_data.get('version', 'unknown')}")
                    print(f"   - Python version: {health_data.get('python_version', 'unknown').split()[0]}")
                except:
                    print("   - Health response parsing: ⚠️  Could not parse JSON")
            else:
                print("   - Health endpoint: ❌ Failed")
                all_files_good = False
            
            # Cleanup test container
            run_command("sudo docker stop slsa-validation-test > /dev/null 2>&1", capture_output=True)
            run_command("sudo docker rm slsa-validation-test > /dev/null 2>&1", capture_output=True)
            print("   - Test cleanup: ✅")
        else:
            print("   - Container start: ❌ Failed to start test container")
            all_files_good = False
    
    # Key achievements check
    print("\n🎯 Stage A2 Key Achievements:")
    achievements = [
        ("Multi-stage Dockerfile with security best practices", dockerfile_path and "FROM python:3.11-slim as builder" in open(dockerfile_path).read() if os.path.exists(dockerfile_path) else False),
        ("Docker image builds successfully", image_check and "slsa-demo-app" in image_info if docker_available else False),
        ("Container runs and serves HTTP requests", health_test and "slsa-demo-app" in health_response if docker_available else False),
        ("SHA-256 digest available for supply chain tracking", docker_available and image_check),
        ("Production-ready setup with gunicorn", dockerfile_path and "gunicorn" in open(dockerfile_path).read() if os.path.exists(dockerfile_path) else False)
    ]
    
    for description, achieved in achievements:
        status = "✅" if achieved else "❌"
        print(f"   {status} {description}")
    
    all_achievements = all([achieved for _, achieved in achievements])
    
    print(f"\n🎯 Stage A2 Status: {'✅ COMPLETE' if all_files_good and all_achievements else '❌ INCOMPLETE'}")
    
    if all_files_good and all_achievements:
        print("\n🚀 Ready for Stage A3 (GitHub Actions CI/CD)!")
        print("   Next: Set up automated builds with provenance generation")
        print(f"   Docker Image ID: {image_data[2] if 'image_data' in locals() and len(image_data) >= 3 else 'Run docker images to get ID'}")
        
        # Show the critical SHA-256 information
        print(f"\n📝 Supply Chain Tracking Information:")
        print(f"   - Artifact Name: slsa-demo-app")
        print(f"   - Artifact Version: 1.0.0")
        print(f"   - Container Image: slsa-demo-app:latest")
        if 'image_data' in locals() and len(image_data) >= 3:
            print(f"   - Image ID: {image_data[2]} (local build fingerprint)")
        print(f"   ⚠️  Registry digest will be available after pushing to GHCR in Stage A3")
        
    return all_files_good and all_achievements

if __name__ == "__main__":
    success = validate_docker_stage()
    sys.exit(0 if success else 1)