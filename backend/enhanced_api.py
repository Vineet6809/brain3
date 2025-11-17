from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import List, Optional
import shutil
import uuid
from enhanced_pipeline import EnhancedImagePipeline
from datetime import datetime
from pydantic import BaseModel

# Initialize enhanced pipeline
pipeline = EnhancedImagePipeline(data_dir="data")

# Create API router
enhanced_api_router = APIRouter(prefix="/api")


class GraphFilters(BaseModel):
    categories: Optional[List[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    connection_types: Optional[List[str]] = None


@enhanced_api_router.post("/ingest")
async def ingest_image(file: UploadFile = File(...)):
    """
    Ingest an image file through the enhanced pipeline
    """
    try:
        # Generate unique ID
        image_id = str(uuid.uuid4())[:16]
        
        # Save uploaded file
        file_path = Path("data/images") / f"{image_id}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process through enhanced pipeline
        result = await pipeline.ingest_image(file_path, image_id)
        
        return JSONResponse(content=result, status_code=200)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_api_router.get("/node/{image_id}")
async def get_node(image_id: str):
    """
    Get metadata for a specific image node
    """
    metadata = await pipeline.get_metadata(image_id)
    if metadata is None:
        raise HTTPException(status_code=404, detail="Node not found")
    return metadata


@enhanced_api_router.get("/thumbnail/{image_id}")
async def get_thumbnail(image_id: str, size: str = Query("small", regex="^(small|large)$")):
    """
    Get thumbnail for a specific image
    size: 'small' (512x512) or 'large' (1024x1024)
    """
    if size == "large":
        thumbnail_path = Path("data/thumbnails_large") / f"{image_id}.jpg"
    else:
        thumbnail_path = Path("data/thumbnails") / f"{image_id}.jpg"
    
    if not thumbnail_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(thumbnail_path)


@enhanced_api_router.post("/graph")
async def get_graph(filters: Optional[GraphFilters] = None):
    """
    Get the full graph structure with optional filters
    """
    try:
        filter_dict = None
        if filters:
            filter_dict = {}
            if filters.categories:
                filter_dict['categories'] = filters.categories
            if filters.date_from:
                filter_dict['date_from'] = datetime.fromisoformat(filters.date_from)
            if filters.date_to:
                filter_dict['date_to'] = datetime.fromisoformat(filters.date_to)
            if filters.connection_types:
                filter_dict['connection_types'] = filters.connection_types
        
        graph = await pipeline.build_graph_enhanced(filter_dict)
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_api_router.get("/graph")
async def get_graph_simple():
    """
    Get the full graph structure without filters (for backward compatibility)
    """
    try:
        graph = await pipeline.build_graph_enhanced()
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_api_router.post("/build-index")
async def build_index():
    """
    Build FAISS indexes for all ingested images
    """
    try:
        pipeline.build_faiss_indexes()
        return {"status": "success", "message": "Indexes built successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_api_router.get("/search")
async def search_nodes(query: str):
    """
    Search nodes by filename, OCR text, entities, and categories
    """
    try:
        if not query or len(query.strip()) == 0:
            return {"nodes": [], "count": 0}
        
        matching_nodes = await pipeline.search_images(query)
        
        return {"nodes": matching_nodes, "count": len(matching_nodes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@enhanced_api_router.get("/categories")
async def get_categories():
    """
    Get all available content categories
    """
    return {
        "categories": [
            {"id": "anime/manga", "label": "Anime/Manga"},
            {"id": "movie/tv show poster", "label": "Movies/TV Shows"},
            {"id": "educational/academic content", "label": "Education"},
            {"id": "programming/coding screenshot", "label": "Coding"},
            {"id": "document/text", "label": "Documents"},
            {"id": "social media post", "label": "Social Media"},
            {"id": "meme/comic", "label": "Memes/Comics"},
            {"id": "photo/picture", "label": "Photos"},
            {"id": "diagram/chart", "label": "Diagrams/Charts"},
            {"id": "other", "label": "Other"}
        ]
    }


@enhanced_api_router.get("/connection-types")
async def get_connection_types():
    """
    Get all available connection types
    """
    return {
        "connection_types": [
            {"id": "all", "label": "All Connections"},
            {"id": "date", "label": "Date-Based"},
            {"id": "category", "label": "Content Type"},
            {"id": "entity", "label": "Shared Entities"},
            {"id": "similarity", "label": "Visual Similarity"}
        ]
    }


@enhanced_api_router.get("/stats")
async def get_stats():
    """
    Get statistics about the image collection
    """
    try:
        total_images = await pipeline.db.images.count_documents({})
        
        # Get category distribution
        category_pipeline = [
            {"$group": {"_id": "$primary_category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}}
        ]
        category_stats = await pipeline.db.images.aggregate(category_pipeline).to_list(length=None)
        
        # Get date range
        date_pipeline = [
            {"$group": {
                "_id": None,
                "earliest": {"$min": "$creation_date"},
                "latest": {"$max": "$creation_date"}
            }}
        ]
        date_stats = await pipeline.db.images.aggregate(date_pipeline).to_list(length=1)
        
        return {
            "total_images": total_images,
            "categories": [
                {"category": stat["_id"], "count": stat["count"]} 
                for stat in category_stats
            ],
            "date_range": {
                "earliest": date_stats[0]["earliest"].isoformat() if date_stats and date_stats[0].get("earliest") else None,
                "latest": date_stats[0]["latest"].isoformat() if date_stats and date_stats[0].get("latest") else None
            } if date_stats else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
