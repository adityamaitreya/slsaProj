#!/usr/bin/env python3
"""
Validate the Flask application structure without running it
This helps verify we've created all the right files
"""

import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and report"""
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {description}: {filepath} ({size} bytes)")
        return True
    else:
        print(f"❌ Missing: {description} at {filepath}")
        return False

def validate_app_structure():
    """Validate the complete application structure"""
    print("🔍 Validating SLSA Demo App Structure")
    print("=" * 40)
    
    base_dir = "/home/byte/Desktop/projX/app"
    
    files_to_check = [
        (f"{base_dir}/src/app.py", "Main Flask application"),
        (f"{base_dir}/requirements.txt", "Python dependencies"),
        (f"{base_dir}/.env.example", "Environment config example"),
        (f"{base_dir}/tests/test_app.py", "Test suite"),
        (f"{base_dir}/README.md", "Application documentation"),
        (f"{base_dir}/run_dev.sh", "Development script")
    ]
    
    all_good = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    print("\n📋 Code Structure Analysis:")
    
    # Check main application file
    app_file = f"{base_dir}/src/app.py"
    if os.path.exists(app_file):
        with open(app_file, 'r') as f:
            content = f.read()
            print(f"   - Lines of code: {len(content.splitlines())}")
            print(f"   - Contains Flask import: {'from flask import' in content}")
            print(f"   - Has health endpoint: {'/health' in content}")
            print(f"   - Has artifact-info endpoint: {'/api/artifact-info' in content}")
            print(f"   - Has echo endpoint: {'/api/echo' in content}")
            print(f"   - Has error handlers: {'@app.errorhandler' in content}")
    
    # Check requirements
    req_file = f"{base_dir}/requirements.txt"
    if os.path.exists(req_file):
        with open(req_file, 'r') as f:
            deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            print(f"   - Dependencies defined: {len(deps)}")
            print(f"   - Main dependencies: {', '.join(deps[:3])}")
    
    # Check tests
    test_file = f"{base_dir}/tests/test_app.py"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
            test_functions = [line.strip() for line in content.splitlines() if line.strip().startswith('def test_')]
            print(f"   - Test functions: {len(test_functions)}")
    
    print(f"\n🎯 Stage A1 Status: {'✅ COMPLETE' if all_good else '❌ INCOMPLETE'}")
    
    if all_good:
        print("\n🚀 Ready for Stage A2 (Dockerization)!")
        print("   Next: Create Dockerfile to containerize this application")
    
    return all_good

if __name__ == "__main__":
    validate_app_structure()