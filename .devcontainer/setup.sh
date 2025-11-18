#!/bin/bash

echo "============================================"
echo "GitHub Codespaces Setup - Image Knowledge Graph"
echo "============================================"

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
    libgomp1

# Start MongoDB
echo "🍃 Starting MongoDB..."
sudo mkdir -p /data/db
sudo chmod -R 777 /data/db
sudo mongod --fork --logpath /var/log/mongodb.log --bind_ip 127.0.0.1

# Create data directories
echo "📁 Creating data directories..."
mkdir -p data/images data/thumbnails data/metadata data/indexes

# Setup Python backend
echo "🐍 Setting up Python backend..."
cd /workspaces/workspace/backend || cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies (this may take 5-10 minutes)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# Download spaCy model
echo "📥 Downloading spaCy language model..."
python -m spacy download en_core_web_sm

# Setup Node.js frontend
echo "⚛️  Setting up React frontend..."
cd /workspaces/workspace/frontend || cd ../frontend

# Install Node dependencies
echo "📦 Installing Node.js dependencies..."
yarn install

# Update frontend .env with Codespace URL
echo "🔧 Configuring frontend environment..."
cat > .env << 'EOF'
REACT_APP_BACKEND_URL=https://${CODESPACE_NAME}-8001.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}
WDS_SOCKET_PORT=443
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
EOF

# Return to workspace root
cd /workspaces/workspace || cd ..

echo ""
echo "============================================"
echo "✅ Setup complete!"
echo "============================================"
echo ""
echo "To start the application:"
echo "  1. Backend:  cd backend && source .venv/bin/activate && uvicorn server:app --host 0.0.0.0 --port 8001"
echo "  2. Frontend: cd frontend && PORT=3000 yarn start"
echo ""
echo "Or use the start script:"
echo "  bash scripts/start_codespaces.sh"
echo ""
echo "============================================"
