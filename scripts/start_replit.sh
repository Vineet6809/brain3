#!/bin/bash

echo "========================================"
echo "Image Knowledge Graph System - Starting"
echo "========================================"

# Create data directories
echo "Creating data directories..."
mkdir -p data/images data/thumbnails data/metadata data/indexes

# Start MongoDB
echo "Starting MongoDB..."
mkdir -p /tmp/mongodb
mongod --dbpath /tmp/mongodb --bind_ip 127.0.0.1 --port 27017 --quiet &
sleep 3

# Install Python dependencies
echo "Installing Python dependencies..."
cd /app/backend
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt

# Download spaCy model if not already downloaded
echo "Checking spaCy model..."
python -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null || python -m spacy download en_core_web_sm

echo "Starting backend server on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd /app/frontend
if [ ! -d "node_modules" ]; then
  yarn install --silent
fi

echo "Starting frontend server on port 3000..."
PORT=3000 yarn start &
FRONTEND_PID=$!

echo ""
echo "========================================"
echo "System started successfully!"
echo "========================================"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8001"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Press Ctrl+C to stop all services"
echo "========================================"

# Keep script running
wait
