# Image Knowledge Graph System

A free-tier, CPU-only image ingestion and graph visualization system that processes images through OCR, generates embeddings, and displays relationships in an interactive 3D graph with **image thumbnails visible directly on nodes**.

## ✨ Features

- 🎨 **Enhanced 3D Visualization**: Image thumbnails displayed directly on graph nodes for better visual context
- 🔍 **Real-time Search**: Search across filenames, OCR text, and entities with live highlighting
- 📦 **Batch Processing**: Command-line script to process entire folders of images
- 📊 **Progress Tracking**: Visual progress bars for upload operations
- ☁️ **GitHub Codespaces Ready**: Full devcontainer configuration for instant cloud development

## Features

### Backend (FastAPI)
- **Image Ingestion Pipeline**
  - SHA256 + perceptual hash (pHash) deduplication
  - Tesseract OCR for text extraction
  - SentenceTransformer text embeddings (`all-MiniLM-L6-v2`)
  - CLIP image embeddings (`openai/clip-vit-base-patch32`)
  - Metadata storage in JSON + SQLite
  - Thumbnail generation

- **Vector Search**
  - FAISS indexes for text and image embeddings
  - Fast similarity search

- **Graph Building**
  - Automatic edge creation based on:
    - Shared named entities
    - Embedding similarity

- **API Endpoints**
  - `POST /api/ingest` - Upload and process images
  - `GET /api/node/{id}` - Get metadata for a specific image
  - `GET /api/thumbnail/{id}` - Get thumbnail for an image
  - `GET /api/graph` - Get full graph structure (nodes + links)
  - `POST /api/build-index` - Build FAISS indexes
  - `GET /api/search?query=text` - Search nodes by text (NEW)
  - `GET /api/` - Health check endpoint
  - `POST /api/status` - Create status check
  - `GET /api/status` - Get status checks

- **Batch Processing**
  - Command-line script for folder ingestion
  - Progress tracking with tqdm
  - Automatic duplicate detection
  - Error handling and reporting

### Frontend (React)
- **Enhanced 3D Visualization**: Image thumbnails displayed on nodes using Three.js sprites
- **Search Functionality**: Real-time search with result highlighting
- **Progress Indicators**: Visual feedback during uploads
- Interactive 3D force graph visualization using `react-force-graph-3d`
- Upload images directly from the UI
- Click nodes to view detailed metadata
- View thumbnails and OCR text
- See extracted named entities
- Real-time graph updates

## Technology Stack

### Backend
- FastAPI
- Pillow, imagehash
- Tesseract OCR
- SentenceTransformers
- CLIP (Transformers)
- FAISS (CPU)
- spaCy (`en_core_web_sm`)
- SQLite
- MongoDB (for other app data)

### Frontend
- React 19
- react-force-graph-3d
- Three.js

## Installation & Setup

### Option 1: Replit (Easiest - One-Click Deploy)

[![Run on Replit](https://replit.com/badge/github/yourusername/image-knowledge-graph)](https://replit.com/@yourusername/image-knowledge-graph)

1. Click the "Run on Replit" button above
2. Wait for automatic setup (5-10 minutes for first run)
3. The app will start automatically
4. Access the web interface from the Replit webview

**See `replitinstruction.md` for detailed Replit setup guide.**

### Option 2: Local Installation (with virtual environment)

#### Prerequisites
- Python 3.11+
- Node.js 18+
- System dependencies: Tesseract OCR

#### Install System Dependencies
```bash
# Run the install script
chmod +x scripts/install_deps.sh
./scripts/install_deps.sh
```

Or manually:
```bash
# Install Tesseract
sudo apt-get update
sudo apt-get install -y tesseract-ocr libtesseract-dev

# Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install -r backend/requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Install frontend dependencies
cd frontend
yarn install
cd ..
```

#### Run the Application

**Backend:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Run backend server
uvicorn backend.server:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
# In a new terminal
cd frontend
yarn start
```

The frontend will be available at `http://localhost:3000` and backend at `http://localhost:8000`.

### Option 3: Docker (Recommended for Production)

#### Prerequisites
- Docker
- Docker Compose

#### Run with Docker
```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

The frontend will be available at `http://localhost:3000` and backend at `http://localhost:8000`.

## Usage

### 1. Upload Images

**Single Image Upload (Web Interface):**
- Open the web interface at `http://localhost:3000`
- Click "Upload Image" button
- Select an image file (JPG, PNG, etc.)
- Wait for processing (first time will download AI models ~1-2GB)

**Batch Upload (Command Line):**
```bash
# Process all images in a folder
python backend/batch_ingest.py /path/to/your/images

# Examples
python backend/batch_ingest.py data/images
python backend/batch_ingest.py ~/Pictures/vacation
```

The batch script will:
- Process all images with progress tracking
- Automatically detect and skip duplicates
- Show detailed status for each image
- Handle errors gracefully

### 2. Search Images
- Use the search bar at the top of the control panel
- Search by filename, OCR text, or extracted entities
- Matching nodes will be highlighted in the graph
- Click on a highlighted node to view details

### 3. Build FAISS Index
After uploading multiple images, click "Build Index" to create vector indexes for similarity search.

### 4. Explore the Graph
- **Rotate**: Left mouse drag
- **Zoom**: Mouse wheel
- **Pan**: Right mouse drag
- **Click nodes**: View detailed information with thumbnails
- **Image Thumbnails**: Visible directly on each node for instant visual identification

### 5. API Usage Examples

**Upload an image:**
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -F "file=@/path/to/image.jpg"
```

**Get node metadata:**
```bash
curl "http://localhost:8000/api/node/{image_id}"
```

**Get graph data:**
```bash
curl "http://localhost:8000/api/graph"
```

**Build FAISS index:**
```bash
curl -X POST "http://localhost:8000/api/build-index"
```

**Search images:**
```bash
curl "http://localhost:8000/api/search?query=invoice"
curl "http://localhost:8000/api/search?query=person"
```

## Testing

```bash
# Run pytest tests
pytest tests/ -v

# Or run specific test
pytest tests/test_ingest.py -v
```

## Project Structure

```
.
├── backend/
│   ├── pipeline.py          # Image processing pipeline
│   ├── api.py               # Image API endpoints (with search)
│   ├── server.py            # Main FastAPI application
│   ├── batch_ingest.py      # Batch processing script (NEW)
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile           # Backend Docker image
│   └── .env                 # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js           # Enhanced 3D graph with image nodes (NEW)
│   │   ├── App.css          # Enhanced styles (NEW)
│   │   └── index.js         # Entry point
│   ├── package.json         # Node.js dependencies
│   ├── Dockerfile           # Frontend Docker image
│   └── .env                 # Frontend environment variables
├── data/                    # Data directory (auto-created)
│   ├── images/              # Original images
│   ├── thumbnails/          # Generated thumbnails
│   ├── metadata/            # JSON metadata files
│   ├── indexes/             # FAISS indexes
│   └── metadata.db          # SQLite database
├── tests/
│   ├── test_ingest.py       # Integration tests
│   └── images/              # Test images
├── scripts/
│   ├── install_deps.sh      # Installation script
│   └── start_replit.sh      # Replit startup script (NEW)
├── .replit                  # Replit configuration (NEW)
├── replit.nix               # Replit dependencies (NEW)
├── replitinstruction.md     # Replit setup guide (NEW)
├── IMPROVEMENTS_AND_SUGGESTIONS.md  # Feature roadmap (NEW)
├── docker-compose.yml       # Docker Compose configuration
└── README.md                # This file
```

## Data Storage

- **SQLite**: Image metadata, embeddings, deduplication hashes
- **MongoDB**: Application data (status checks, etc.)
- **JSON Files**: Individual image metadata
- **File System**: Original images, thumbnails, FAISS indexes

## Notes

- **First Run**: The first image upload will download AI models (~1-2GB). This is a one-time download.
- **CPU Only**: All models run on CPU - no GPU required.
- **Free Tier**: Uses only open-source, free tools and models.
- **Deduplication**: SHA256 hash prevents exact duplicates. pHash can detect near-duplicates.
- **Scalability**: FAISS indexes scale to millions of images efficiently.

## Troubleshooting

### Tesseract not found
Make sure Tesseract is installed:
```bash
sudo apt-get install tesseract-ocr libtesseract-dev
```

### spaCy model not found
Download the spaCy model:
```bash
python -m spacy download en_core_web_sm
```

### Port already in use
Change ports in docker-compose.yml or when running locally.

### Out of memory
Reduce batch sizes or use smaller images. The system is designed for CPU-only operation.

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
