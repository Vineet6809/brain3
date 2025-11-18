#!/bin/bash

echo "============================================"
echo "GitHub Codespaces Setup - Image Knowledge Graph"
echo "============================================"

# Detect workspace directory
WORKSPACE_DIR="/workspaces/brain3"
if [ ! -d "$WORKSPACE_DIR" ]; then
    WORKSPACE_DIR=$(pwd)
fi

echo "📂 Workspace: $WORKSPACE_DIR"
cd "$WORKSPACE_DIR" || exit 1

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update -qq

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y -qq \
    tesseract-ocr \
    libtesseract-dev \
    mongodb \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    curl

# Start MongoDB
echo "🍃 Starting MongoDB..."
sudo mkdir -p /data/db
sudo chmod -R 777 /data/db
if ! pgrep -x "mongod" > /dev/null; then
    sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1 || true
fi

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/images data/thumbnails data/metadata data/indexes

# Setup Python backend
echo "🐍 Setting up Python backend..."
cd "$WORKSPACE_DIR/backend" || exit 1

# Create virtual environment
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies (this may take 5-10 minutes)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q || pip install -r requirements.txt

# Download spaCy model
echo "📥 Downloading spaCy language model..."
python -m spacy download en_core_web_sm || true

# Create backend .env
echo "🔧 Creating backend .env..."
cat > .env << 'EOF'
MONGO_URL=mongodb://localhost:27017
DB_NAME=image_graph_db
CORS_ORIGINS=*
EOF

# Setup Node.js frontend
echo "⚛️  Setting up React frontend..."
cd "$WORKSPACE_DIR/frontend" || exit 1

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
yarn install || npm install

# Create frontend .env with Codespace URL
echo "🔧 Creating frontend .env..."
if [ -n "$CODESPACE_NAME" ] && [ -n "$GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN" ]; then
    BACKEND_URL="https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
else
    BACKEND_URL="http://localhost:8001"
fi

cat > .env << EOF
REACT_APP_BACKEND_URL=${BACKEND_URL}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

echo "Backend URL: ${BACKEND_URL}"

# Return to workspace root
cd "$WORKSPACE_DIR" || exit 1

echo ""
echo "============================================"
echo "✅ Setup complete!"
echo "============================================"
echo ""
echo "To start the application, run:"
echo "  bash scripts/start_codespaces.sh"
echo ""
echo "Or start services manually:"
echo "  1. Backend:  cd backend && source .venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8001 --reload"
echo "  2. Frontend: cd frontend && PORT=3000 yarn start"
echo ""
echo "============================================"
