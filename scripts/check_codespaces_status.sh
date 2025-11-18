#!/bin/bash

echo "=========================================="
echo "  Codespaces Health Check"
echo "=========================================="
echo ""

# Check if we're in Codespaces
if [ -n "$CODESPACE_NAME" ]; then
    echo "✅ Running in GitHub Codespaces: $CODESPACE_NAME"
    BACKEND_URL="https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
    FRONTEND_URL="https://${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
    echo "⚠️  Not in Codespaces (localhost mode)"
    BACKEND_URL="http://localhost:8001"
    FRONTEND_URL="http://localhost:3000"
fi

echo ""
echo "📍 URLs:"
echo "   Frontend: $FRONTEND_URL"
echo "   Backend:  $BACKEND_URL"
echo ""

# Check MongoDB
echo "🍃 MongoDB Status:"
if pgrep -x "mongod" > /dev/null; then
    echo "   ✅ Running"
else
    echo "   ❌ NOT running"
    echo "   Fix: sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1"
fi

echo ""

# Check Backend
echo "🔧 Backend Status:"
if curl -s http://localhost:8001/api/ > /dev/null 2>&1; then
    echo "   ✅ Running and responding"
    RESPONSE=$(curl -s http://localhost:8001/api/)
    echo "   Response: $RESPONSE"
else
    echo "   ❌ NOT responding"
    echo "   Check: tail -f /var/log/supervisor/backend.err.log"
fi

echo ""

# Check Frontend
echo "⚛️  Frontend Status:"
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Running"
else
    echo "   ❌ NOT responding"
    echo "   Check: tail -f /var/log/supervisor/frontend.err.log"
fi

echo ""

# Check Frontend .env
echo "📝 Frontend Configuration:"
if [ -f "frontend/.env" ]; then
    BACKEND_URL_CONFIG=$(grep REACT_APP_BACKEND_URL frontend/.env | cut -d'=' -f2)
    echo "   Backend URL: $BACKEND_URL_CONFIG"
    
    if [ -n "$CODESPACE_NAME" ]; then
        EXPECTED_URL="https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
        if [ "$BACKEND_URL_CONFIG" = "$EXPECTED_URL" ]; then
            echo "   ✅ Correct for this Codespace"
        else
            echo "   ⚠️  URL mismatch!"
            echo "   Expected: $EXPECTED_URL"
            echo "   Found:    $BACKEND_URL_CONFIG"
            echo "   Fix: bash scripts/start_codespaces.sh"
        fi
    fi
else
    echo "   ❌ frontend/.env not found"
fi

echo ""

# Check ports visibility (if in Codespaces)
if [ -n "$CODESPACE_NAME" ]; then
    echo "⚠️  IMPORTANT: Port Visibility"
    echo "   Make sure ports 3000 and 8001 are set to PUBLIC"
    echo "   in VS Code PORTS tab (bottom panel)"
    echo ""
    echo "   Steps:"
    echo "   1. Click PORTS tab"
    echo "   2. Right-click port 8001 → Port Visibility → Public"
    echo "   3. Right-click port 3000 → Port Visibility → Public"
fi

echo ""
echo "=========================================="

# Test backend endpoints
echo ""
echo "🧪 Testing Backend Endpoints:"
echo ""

echo "1. Health Check (/api/):"
curl -s http://localhost:8001/api/ | jq '.' 2>/dev/null || curl -s http://localhost:8001/api/

echo ""
echo "2. Stats (/api/stats):"
curl -s http://localhost:8001/api/stats | jq '.' 2>/dev/null || curl -s http://localhost:8001/api/stats

echo ""
echo "3. Categories (/api/categories):"
curl -s http://localhost:8001/api/categories | jq '.categories | length' 2>/dev/null || echo "Categories endpoint check"

echo ""
echo "=========================================="
echo ""

# Summary
echo "📊 Summary:"
if pgrep -x "mongod" > /dev/null && curl -s http://localhost:8001/api/ > /dev/null 2>&1 && curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ All services running correctly!"
    echo ""
    if [ -n "$CODESPACE_NAME" ]; then
        echo "   Next: Ensure ports are PUBLIC and test in browser:"
        echo "   $FRONTEND_URL"
    else
        echo "   Access at: http://localhost:3000"
    fi
else
    echo "   ⚠️  Some services need attention"
    echo "   Run: bash scripts/start_codespaces.sh"
fi

echo ""
echo "=========================================="
