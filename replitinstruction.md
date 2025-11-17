# Replit Setup Instructions for Image Knowledge Graph System

## Overview
This Image Knowledge Graph System processes images through OCR, generates embeddings, and visualizes relationships in an interactive 3D graph. This guide will help you set up and run the project on Replit.

## Automatic Setup

When you open this Repl, it will automatically:
1. Install all Python dependencies
2. Install all Node.js dependencies
3. Download required AI models (SentenceTransformer, CLIP, spaCy)
4. Start MongoDB database
5. Start the FastAPI backend server
6. Start the React frontend server

**Note**: Initial setup may take 5-10 minutes to download AI models (~1-2GB).

## System Architecture

### Backend (FastAPI - Port 8001)
- Image processing pipeline with OCR and embeddings
- FAISS vector search indexes
- MongoDB for metadata storage
- REST API endpoints

### Frontend (React - Port 3000)
- Interactive 3D force graph visualization
- Image upload interface
- Node details with thumbnails
- Search functionality

## Features

### 1. Image Upload
- Click "Upload Image" button in the web interface
- Select an image file (JPG, PNG, etc.)
- The system will:
  - Extract text using Tesseract OCR
  - Generate text embeddings using SentenceTransformer
  - Generate image embeddings using CLIP
  - Extract named entities using spaCy
  - Create thumbnail
  - Add node to the graph

### 2. Batch Processing with Folder Upload

You can process multiple images at once using the batch script:

```bash
# From the project root
python backend/batch_ingest.py /path/to/your/image/folder

# Example: Process images in the data/images directory
python backend/batch_ingest.py data/images
```

The script will:
- Find all image files (jpg, jpeg, png, gif, bmp, webp)
- Process each image through the pipeline
- Show a progress bar
- Display success/error status for each image
- Automatically skip duplicates

**Note**: You can drag and drop a folder into the Replit file explorer, then run the script on that folder.

### 3. Interactive 3D Graph

**Controls:**
- **Rotate**: Left mouse drag
- **Zoom**: Mouse wheel
- **Pan**: Right mouse drag
- **Click node**: View detailed information with thumbnail

**Visual Features:**
- Nodes display actual image thumbnails
- Node size indicates importance
- Links show relationships between images
- Color coding by image groups

### 4. Search Functionality

Use the search bar to find images by:
- Filename
- OCR text content
- Extracted entities

The graph will highlight matching nodes in real-time.

### 5. Build FAISS Index

After uploading multiple images, click "Build Index" to create vector search indexes for similarity search. This enables finding similar images based on content.

## API Endpoints

The backend exposes these endpoints:

- `POST /api/ingest` - Upload and process a single image
- `GET /api/node/{id}` - Get metadata for a specific image
- `GET /api/thumbnail/{id}` - Get thumbnail for an image
- `GET /api/graph` - Get full graph structure (nodes + links)
- `POST /api/build-index` - Build FAISS vector indexes
- `GET /api/search?query=text` - Search nodes by text
- `GET /api/` - Health check

## Data Storage

All data is stored in the `/data` directory:

```
/data/
├── images/          # Original uploaded images
├── thumbnails/      # Generated thumbnails (200x200)
├── metadata/        # JSON metadata files per image
├── indexes/         # FAISS vector indexes
└── metadata.db      # SQLite database with all metadata
```

## Troubleshooting

### Issue: "Models are downloading"
**Solution**: Wait for initial model download (one-time, ~1-2GB). Check the console for progress.

### Issue: "Port already in use"
**Solution**: Stop the Repl and restart it. Replit will automatically assign available ports.

### Issue: "Out of memory"
**Solution**: The free tier has RAM limitations. Try:
- Processing smaller images
- Processing fewer images at once
- Upgrading to Replit's paid tier for more RAM

### Issue: "MongoDB connection failed"
**Solution**: 
- Restart the Repl
- MongoDB should start automatically
- Check console logs for errors

### Issue: "Graph not loading"
**Solution**:
- Ensure backend is running (check port 8001)
- Check browser console for errors
- Try refreshing the page

## Performance Tips

1. **Free Tier Limitations**:
   - RAM: ~1GB (be mindful of image sizes)
   - Storage: Limited (clean up unused images)
   - Processing: Slower on CPU-only

2. **Optimize Performance**:
   - Use smaller images (resize before upload)
   - Build indexes only when needed
   - Process images in smaller batches

3. **Best Practices**:
   - Upload images one at a time initially
   - Build index after uploading 10+ images
   - Use batch script for large collections
   - Keep total image count under 100 for free tier

## File Structure

```
.
├── backend/
│   ├── api.py              # API endpoints
│   ├── pipeline.py         # Image processing pipeline
│   ├── server.py           # FastAPI app
│   ├── batch_ingest.py     # Batch processing script (NEW)
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React component (Enhanced)
│   │   └── App.css        # Styles
│   ├── package.json       # Node dependencies
│   └── .env              # Frontend environment
├── scripts/
│   └── start_replit.sh   # Startup script for Replit
├── .replit               # Replit configuration
├── replit.nix            # Nix dependencies
└── replitinstruction.md  # This file
```

## Technology Stack

- **Backend**: FastAPI, Python 3.11
- **Frontend**: React 19, Three.js
- **Database**: MongoDB, SQLite
- **AI Models**: 
  - SentenceTransformer (all-MiniLM-L6-v2) - Text embeddings
  - CLIP (openai/clip-vit-base-patch32) - Image embeddings
  - spaCy (en_core_web_sm) - Named entity recognition
  - Tesseract - OCR
- **Vector Search**: FAISS (CPU)
- **Visualization**: react-force-graph-3d, Three.js

## Support

For issues or questions:
1. Check the console logs (backend and frontend)
2. Review this documentation
3. Check the main README.md for detailed API documentation
4. Ensure all dependencies are installed

## Next Steps

1. **Upload your first image** using the web interface
2. **Try batch processing** with the batch_ingest.py script
3. **Explore the 3D graph** by clicking on nodes
4. **Search for images** using the search bar
5. **Build indexes** for similarity search

Enjoy exploring your image knowledge graph! 🎨📊🔍
