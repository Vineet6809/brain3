#!/bin/bash

echo "============================================"
echo "Starting Image Knowledge Graph System"
echo "============================================"

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

# Get Codespace URL
if [ -n "$CODESPACE_NAME" ]; then
    BACKEND_URL="https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    FRONTEND_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
    BACKEND_URL="http://localhost:8001"
    FRONTEND_URL="http://localhost:3000"
fi

# Update frontend .env with correct URL
echo "🔧 Updating frontend configuration..."
cat > frontend/.env << EOF
REACT_APP_BACKEND_URL=${BACKEND_URL}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

# Update backend .env
echo "🔧 Updating backend configuration..."
cat > backend/.env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF

# Start backend
echo "🚀 Starting backend server on port 8001..."
cd backend
source .venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start frontend
echo "⚛️  Starting frontend server on port 3000..."
cd frontend
PORT=3000 yarn start &
FRONTEND_PID=$!
cd ..

echo ""
echo "============================================"
echo "✅ Application started successfully!"
echo "============================================"
echo ""
echo "Frontend: ${FRONTEND_URL}"
echo "Backend:  ${BACKEND_URL}"
echo "API Docs: ${BACKEND_URL}/docs"
echo ""
echo "Backend PID:  ${BACKEND_PID}"
echo "Frontend PID: ${FRONTEND_PID}"
echo ""
echo "Press Ctrl+C to stop all services"
echo "============================================"

# Keep script running and handle cleanup
trap "echo 'Stopping services...'; kill ${BACKEND_PID} ${FRONTEND_PID} 2>/dev/null; exit" INT TERM

wait
