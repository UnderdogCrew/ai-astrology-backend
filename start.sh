#!/bin/bash

# Astrology Platform Startup Script
# This script starts both the FastAPI backend and the web interface

echo "🌟 Starting Astrology Platform..."
echo "=================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before starting the application."
    echo "   You can start the application again after configuring .env"
    exit 1
fi

# Start FastAPI backend in background
echo "🚀 Starting FastAPI backend..."
python run.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running at http://localhost:8000"
    echo "📖 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend failed to start. Please check the logs above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start web interface
echo "🌐 Starting web interface..."
python serve_web.py &
WEB_PID=$!

echo ""
echo "🎉 Astrology Platform is now running!"
echo "======================================"
echo "🌐 Web Interface: http://localhost:3000"
echo "🔗 API Backend: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $WEB_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for background processes
wait
