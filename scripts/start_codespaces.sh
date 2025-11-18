#!/bin/bash

echo "============================================"
echo "Starting Image Knowledge Graph System"
echo "============================================"

# Detect workspace directory
if [ -d "/workspaces/brain3" ]; then
    WORKSPACE_DIR="/workspaces/brain3"
    echo "📂 Detected GitHub Codespaces environment"
elif [ -d "/app" ]; then
    WORKSPACE_DIR="/app"
    echo "📂 Detected local/container environment"
else
    WORKSPACE_DIR=$(pwd)
    echo "📂 Using current directory: $WORKSPACE_DIR"
fi

cd "$WORKSPACE_DIR" || exit 1

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "🍃 Starting MongoDB..."
    sudo mkdir -p /data/db
    sudo chmod -R 777 /data/db
    sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1
    sleep 2
else
    echo "✅ MongoDB already running"
fi

# Detect if we're in Codespaces
if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    BACKEND_URL="https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    FRONTEND_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    echo "🌐 Detected Codespace: $CODESPACE_NAME"
else
    BACKEND_URL="http://localhost:8001"
    FRONTEND_URL="http://localhost:3000"
    echo "🌐 Using localhost URLs"
fi

# Update frontend .env
echo "🔧 Updating frontend configuration..."
cat > "$WORKSPACE_DIR/frontend/.env" << EOF
REACT_APP_BACKEND_URL=${BACKEND_URL}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

echo "   Backend URL: ${BACKEND_URL}"

# Update backend .env
echo "🔧 Updating backend configuration..."
cat > "$WORKSPACE_DIR/backend/.env" << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF

# Kill any existing processes on ports 8001 and 3000
echo "🔄 Checking for existing processes..."
sudo fuser -k 8001/tcp 2>/dev/null || true
sudo fuser -k 3000/tcp 2>/dev/null || true
sleep 2

# Start backend
echo "🚀 Starting backend server on port 8001..."
cd "$WORKSPACE_DIR/backend" || exit 1

if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

uvicorn server:app --host 0.0.0.0 --port 8001 --reload > "$WORKSPACE_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: ${BACKEND_PID}"

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
if curl -s http://localhost:8001/api/ > /dev/null; then
    echo "✅ Backend is responding"
else
    echo "⚠️  Backend may not be ready yet"
fi

# Start frontend
echo "⚛️  Starting frontend server on port 3000..."
cd "$WORKSPACE_DIR/frontend" || exit 1

PORT=3000 yarn start > "$WORKSPACE_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: ${FRONTEND_PID}"

sleep 3

echo ""
echo "============================================"
echo "✅ Application started successfully!"
echo "============================================"
echo ""
echo "📱 Frontend: ${FRONTEND_URL}"
echo "🔌 Backend:  ${BACKEND_URL}"
echo "📚 API Docs: ${BACKEND_URL}/docs"
echo ""
echo "📊 Process IDs:"
echo "   Backend:  ${BACKEND_PID}"
echo "   Frontend: ${FRONTEND_PID}"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f $WORKSPACE_DIR/backend.log"
echo "   Frontend: tail -f $WORKSPACE_DIR/frontend.log"
echo ""
echo "⚠️  IMPORTANT: Make sure ports 3000 and 8001 are set to PUBLIC"
echo "   in the VS Code PORTS tab (bottom panel)"
echo ""
echo "🛑 To stop: kill ${BACKEND_PID} ${FRONTEND_PID}"
echo "============================================"

# Keep script running
echo ""
echo "Press Ctrl+C to stop all services..."
trap "echo '\n🛑 Stopping services...'; kill ${BACKEND_PID} ${FRONTEND_PID} 2>/dev/null; exit" INT TERM

wait
