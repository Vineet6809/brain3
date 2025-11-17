#!/bin/bash

set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev

echo "Creating Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "Downloading spaCy model..."
python -m spacy download en_core_web_sm

echo "Creating data directories..."
mkdir -p data/images data/thumbnails data/metadata data/indexes

echo "Installation complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate"
echo "To start the backend, run: uvicorn backend.server:app --reload"
