#!/bin/bash

echo "============================================"
echo "🔧 Fixing URLs for GitHub Codespaces"
echo "============================================"
echo ""

# Detect if running in Codespaces
if [ -z "$CODESPACE_NAME" ]; then
    echo "⚠️  WARNING: Not running in GitHub Codespaces"
    echo "   Using localhost URLs instead"
    BACKEND_URL="http://localhost:8001"
    FRONTEND_URL="http://localhost:3000"
else
    echo "✅ Detected GitHub Codespace: $CODESPACE_NAME"
    BACKEND_URL="https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    FRONTEND_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
fi

echo ""
echo "📝 URLs Configured:"
echo "   Backend:  $BACKEND_URL"
echo "   Frontend: $FRONTEND_URL"
echo ""

# Update frontend .env
echo "🔧 Updating frontend/.env..."
cat > /app/frontend/.env << EOF
REACT_APP_BACKEND_URL=${BACKEND_URL}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

# Update backend .env
echo "🔧 Updating backend/.env..."
cat > /app/backend/.env << EOF
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF

echo ""
echo "✅ Configuration updated successfully!"
echo ""
echo "📋 Next Steps:"
echo "   1. Restart your services:"
echo "      bash scripts/start_codespaces.sh"
echo ""
echo "   2. Or restart manually:"
echo "      - Backend: cd backend && uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo "      - Frontend: cd frontend && PORT=3000 yarn start"
echo ""
echo "   3. Access your app from the PORTS tab in VS Code"
echo "      - Port 3000 (Frontend) - Click the globe icon"
echo "      - Port 8001 (Backend API) - For API access"
echo ""
echo "============================================"
