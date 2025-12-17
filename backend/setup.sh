#!/bin/bash

# NexusHR AI Backend Setup Script
# This script sets up the backend environment and starts the server

echo "=============================================="
echo "  NexusHR AI Backend Setup"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if we're in the backend directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the backend directory."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ .env file created. Please update it with your configuration."
else
    echo "✅ .env file exists"
fi
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p chroma_db
echo "✅ Directories created"
echo ""

echo "=============================================="
echo "  Setup Complete!"
echo "=============================================="
echo ""
echo "🚀 To start the server, run:"
echo "   source venv/bin/activate  # If not already activated"
echo "   python run.py"
echo ""
echo "📖 API Documentation will be available at:"
echo "   http://localhost:8000/api/docs"
echo ""
echo "👤 Default login credentials:"
echo "   Admin:      hr_admin / admin123"
echo "   HR Manager: hr_manager / manager123"
echo "   Employee:   employee / employee123"
echo ""
echo "=============================================="
