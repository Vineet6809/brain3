#!/bin/bash

echo "============================================"
echo "  Codespaces Debug Information"
echo "============================================"
echo ""

# Check environment
echo "📍 Current Directory:"
pwd
echo ""

echo "🌐 Codespace Information:"
echo "   CODESPACE_NAME: ${CODESPACE_NAME:-'Not set'}"
echo "   GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN: ${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-'Not set'}"
echo ""

# Check frontend .env
echo "📝 Frontend Configuration:"
if [ -f "frontend/.env" ]; then
    cat frontend/.env
else
    echo "   ❌ frontend/.env not found!"
fi
echo ""

# Check backend .env
echo "📝 Backend Configuration:"
if [ -f "backend/.env" ]; then
    cat backend/.env
else
    echo "   ❌ backend/.env not found!"
fi
echo ""

# Check if MongoDB is running
echo "🍃 MongoDB Status:"
if pgrep -x "mongod" > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ NOT running"
    echo "   Starting MongoDB..."
    sudo mkdir -p /data/db
    sudo chmod -R 777 /data/db
    sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
fi
echo ""

# Check what's running on ports
echo "🔌 Port Status:"
echo "   Port 8001 (Backend):"
if sudo lsof -i :8001 > /dev/null 2>&1; then
    sudo lsof -i :8001 | grep LISTEN
else
    echo "      Nothing running"
fi
echo ""
echo "   Port 3000 (Frontend):"
if sudo lsof -i :3000 > /dev/null 2>&1; then
    sudo lsof -i :3000 | grep LISTEN
else
    echo "      Nothing running"
fi
echo ""

# Test backend if it's running
echo "🧪 Testing Backend:"
if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
    RESPONSE=$(curl -s http://localhost:8001/api/)
    echo "   ✅ Backend responding: $RESPONSE"
else
    echo "   ❌ Backend not responding"
fi
echo ""

# Check if backend venv exists
echo "🐍 Python Environment:"
if [ -d "backend/.venv" ]; then
    echo "   ✅ Virtual environment exists"
    if [ -f "backend/.venv/bin/python" ]; then
        PYTHON_VERSION=$(backend/.venv/bin/python --version 2>&1)
        echo "   Python: $PYTHON_VERSION"
    fi
else
    echo "   ❌ Virtual environment not found at backend/.venv"
fi
echo ""

# Check node_modules
echo "📦 Node Modules:"
if [ -d "frontend/node_modules" ]; then
    echo "   ✅ node_modules exists"
else
    echo "   ❌ node_modules not found - run 'cd frontend && yarn install'"
fi
echo ""

echo "============================================"
echo "  Recommended Actions:"
echo "============================================"
echo ""

# Generate corrected .env if we have CODESPACE_NAME
if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    echo "✅ Detected Codespace environment"
    echo ""
    echo "Run these commands:"
    echo ""
    echo "# Update frontend .env:"
    echo "cat > frontend/.env << 'EOF'"
    echo "REACT_APP_BACKEND_URL=https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    echo "WDS_SOCKET_PORT=443"
    echo "REACT_APP_ENABLE_VISUAL_EDITS=false"
    echo "ENABLE_HEALTH_CHECK=false"
    echo "EOF"
    echo ""
    echo "# Start backend:"
    echo "cd backend"
    echo "source .venv/bin/activate"
    echo "uvicorn server:app --host 0.0.0.0 --port 8001 --reload &"
    echo "cd .."
    echo ""
    echo "# Start frontend:"
    echo "cd frontend"
    echo "PORT=3000 yarn start &"
    echo ""
else
    echo "⚠️  CODESPACE_NAME not detected"
    echo ""
    echo "This might not be a Codespaces environment, or variables aren't set."
    echo "Check your Codespace settings."
fi

echo ""
echo "============================================"
