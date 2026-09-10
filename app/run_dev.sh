#!/bin/bash
# Development script to run the SLSA demo app locally

set -e  # Exit on any error

echo "🚀 Starting SLSA Demo App in Development Mode"
echo "============================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Set development environment
export FLASK_ENV=development
export FLASK_DEBUG=true
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export ENVIRONMENT=development

echo "🌐 Starting Flask application..."
echo "   - App will be available at: http://localhost:5000"
echo "   - Health check at: http://localhost:5000/health"
echo "   - API info at: http://localhost:5000/api/artifact-info"
echo ""
echo "💡 Press Ctrl+C to stop the server"
echo ""

# Run the application
python src/app.py