from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import uuid
from .pipeline import ImagePipeline

# Initialize pipeline
pipeline = ImagePipeline(data_dir="data")

# Create API router
api_router = APIRouter(prefix="/api")

@api_router.post("/ingest")
async def ingest_image(file: UploadFile = File(...)):
    """
    Ingest an image file through the pipeline
    """
    try:
        # Generate unique ID
        image_id = str(uuid.uuid4())[:16]
        
        # Save uploaded file
        file_path = Path("data/images") / f"{image_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process through pipeline
        result = pipeline.ingest_image(file_path, image_id)
        
        return JSONResponse(content=result, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/node/{image_id}")
async def get_node(image_id: str):
    """
    Get metadata for a specific image node
    """
    metadata = pipeline.get_metadata(image_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return metadata

@api_router.get("/thumbnail/{image_id}")
async def get_thumbnail(image_id: str):
    """
    Get thumbnail for a specific image
    """
    thumbnail_path = Path("data/thumbnails") / f"{image_id}.jpg"
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumbnail_path)

@api_router.get("/graph")
async def get_graph():
    """
    Get the full graph structure
    """
    try:
        graph = pipeline.build_graph()
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/build-index")
async def build_index():
    """
    Build FAISS indexes for all ingested images
    """
    try:
        pipeline.build_faiss_indexes()
        return {"status": "success", "message": "Indexes built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
