#!/bin/bash

echo "============================================"
echo "  Starting Backend in Codespaces"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Run this from the repository root (/workspaces/brain3)"
    exit 1
fi

# Start MongoDB if not running
echo "🍃 Checking MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo "   Starting MongoDB..."
    sudo mkdir -p /data/db
    sudo chmod -R 777 /data/db
    sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
    sleep 2
    echo "   ✅ MongoDB started"
else
    echo "   ✅ MongoDB already running"
fi
echo ""

# Create backend .env if it doesn't exist
echo "🔧 Setting up backend .env..."
cat > backend/.env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF
echo "   ✅ Backend .env created"
echo ""

# Check if virtual environment exists
echo "🐍 Checking Python environment..."
cd backend

if [ ! -d ".venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv .venv
    echo "   ✅ Virtual environment created"
fi

# Activate and check dependencies
echo "   Activating virtual environment..."
source .venv/bin/activate

echo "   Checking dependencies..."
if ! pip show fastapi > /dev/null 2>&1; then
    echo "   Installing Python dependencies (this may take a few minutes)..."
    pip install --upgrade pip -q
    pip install -r requirements.txt
    echo "   ✅ Dependencies installed"
else
    echo "   ✅ Dependencies already installed"
fi

# Check if spacy model is installed
if ! python -c "import spacy; spacy.load('en_core_web_sm')" > /dev/null 2>&1; then
    echo "   Downloading spaCy model..."
    python -m spacy download en_core_web_sm
    echo "   ✅ spaCy model installed"
fi

echo ""
echo "🚀 Starting backend server..."
echo "   Backend will run on: http://localhost:8001"
echo "   Public URL: https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo ""

# Kill any existing process on port 8001
sudo fuser -k 8001/tcp 2>/dev/null || true
sleep 1

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!

echo "   Backend PID: $BACKEND_PID"
echo ""
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "   ✅ Backend is running and responding!"
    RESPONSE=$(curl -s http://localhost:8001/api/)
    echo "   Response: $RESPONSE"
else
    echo "   ⚠️  Backend may be starting... Check logs:"
    echo "   tail -f ../backend.log"
fi

cd ..

echo ""
echo "============================================"
echo "✅ Backend Setup Complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Frontend should already be running on port 3000"
echo "2. If not, run in another terminal: cd frontend && PORT=3000 yarn start"
echo "3. Access your app at:"
echo "   https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo ""
echo "To check logs:"
echo "   tail -f backend.log"
echo ""
echo "============================================"
