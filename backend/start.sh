#!/bin/bash

# Farm Monitor - Quick Start Script
# This script sets up and runs the backend server

echo "🌾 Farm Monitor - Backend Setup"
echo "================================"

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.9+ required. You have Python $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt --quiet

# Check for GEE credentials
if [ ! -f "gee-credentials.json" ]; then
    echo "⚠️  Warning: gee-credentials.json not found"
    echo "   Satellite features will use mock data"
    echo "   See docs/SETUP.md for GEE setup instructions"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created - please edit with your settings"
fi

# Run the server
echo ""
echo "🚀 Starting Farm Monitor API..."
echo "================================"
echo "Server will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

python main.py
