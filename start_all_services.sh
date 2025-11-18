#!/bin/bash

echo "============================================"
echo "  Starting All Services in Codespaces"
echo "============================================"
echo ""

# Verify we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Run this from /workspaces/brain3"
    exit 1
fi

# 1. Start MongoDB
echo "Step 1: Starting MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    sudo mkdir -p /data/db
    sudo chmod -R 777 /data/db
    sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
    echo "✅ MongoDB started"
else
    echo "✅ MongoDB already running"
fi
echo ""

# 2. Setup Backend
echo "Step 2: Setting up Backend..."
cd backend

# Create .env
cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF

# Setup venv if needed
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# Check if packages are installed
if ! pip show fastapi > /dev/null 2>&1; then
    echo "Installing Python dependencies..."
    pip install --upgrade pip -q
    pip install -r requirements.txt
fi

# Kill existing backend
sudo fuser -k 8001/tcp 2>/dev/null || true
sleep 1

# Start backend
echo "Starting backend on port 8001..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

cd ..
sleep 5

# Test backend
if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend starting... check 'tail -f backend.log'"
fi
echo ""

# 3. Setup Frontend
echo "Step 3: Checking Frontend..."

# Update .env
if [ -n "$CODESPACE_NAME" ]; then
    cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=https://\${CODESPACE_NAME}-8001.\${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF
fi

cd frontend

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    yarn install
fi

# Kill existing frontend
sudo fuser -k 3000/tcp 2>/dev/null || true
sleep 1

# Start frontend
echo "Starting frontend on port 3000..."
PORT=3000 yarn start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

cd ..

echo ""
echo "============================================"
echo "✅ All Services Started!"
echo "============================================"
echo ""
echo "Process IDs:"
echo "  Backend:  $BACKEND_PID"
echo "  Frontend: $FRONTEND_PID"
echo ""
echo "URLs:"
echo "  Frontend: https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo "  Backend:  https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
echo "  API Docs: https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}/docs"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "============================================"
