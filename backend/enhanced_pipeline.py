import os
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import numpy as np
from PIL import Image
import imagehash
import pytesseract
import easyocr
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
import torch
import faiss
import spacy
from tqdm import tqdm
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
import asyncio

# Initialize models (lazy loading)
_text_model = None
_clip_model = None
_clip_processor = None
_nlp = None
_easyocr_reader = None

def get_text_model():
    global _text_model
    if _text_model is None:
        print("Loading SentenceTransformer model...")
        _text_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    return _text_model

def get_clip_model():
    global _clip_model, _clip_processor
    if _clip_model is None:
        print("Loading CLIP model...")
        _clip_model = CLIPModel.from_pretrained('openai/clip-vit-base-patch32')
        _clip_processor = CLIPProcessor.from_pretrained('openai/clip-vit-base-patch32')
    return _clip_model, _clip_processor

def get_nlp():
    global _nlp
    if _nlp is None:
        print("Loading spaCy model...")
        _nlp = spacy.load('en_core_web_sm')
    return _nlp

def get_easyocr_reader():
    global _easyocr_reader
    if _easyocr_reader is None:
        print("Loading EasyOCR reader...")
        try:
            _easyocr_reader = easyocr.Reader(['en'], gpu=False, verbose=False)
        except Exception as e:
            print(f"Failed to load EasyOCR: {e}")
            _easyocr_reader = None
    return _easyocr_reader


class EnhancedImagePipeline:
    def __init__(self, data_dir: str = "data", mongo_url: str = None, db_name: str = None):
        self.data_dir = Path(data_dir)
        self.images_dir = self.data_dir / "images"
        self.thumbnails_dir = self.data_dir / "thumbnails"
        self.thumbnails_large_dir = self.data_dir / "thumbnails_large"
        self.metadata_dir = self.data_dir / "metadata"
        self.indexes_dir = self.data_dir / "indexes"
        self.db_path = self.data_dir / "metadata.db"
        
        # Create directories
        for d in [self.images_dir, self.thumbnails_dir, self.thumbnails_large_dir, 
                  self.metadata_dir, self.indexes_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # MongoDB connection
        self.mongo_url = mongo_url or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = db_name or os.environ.get('DB_NAME', 'test_database')
        self.mongo_client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.mongo_client[self.db_name]
        
        # Initialize SQLite (for backward compatibility and FAISS)
        self._init_db()
        
        # Initialize FAISS indexes
        self.text_index = None
        self.image_index = None
        self.text_ids = []
        self.image_ids = []
        
        # Content categories for classification
        self.content_categories = [
            "anime or manga",
            "movie or tv show poster",
            "educational or academic content",
            "programming or coding screenshot",
            "document or text",
            "social media post",
            "meme or comic",
            "photo or picture",
            "diagram or chart",
            "other"
        ]
        
    def _init_db(self):
        """Initialize SQLite database for backward compatibility"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id TEXT PRIMARY KEY,
                sha256 TEXT UNIQUE,
                phash TEXT,
                filename TEXT,
                ocr_text TEXT,
                entities TEXT,
                text_embedding BLOB,
                image_embedding BLOB,
                thumbnail_path TEXT,
                metadata_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def compute_sha256(self, image_path: Path) -> str:
        """Compute SHA256 hash of image"""
        sha256_hash = hashlib.sha256()
        with open(image_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def compute_phash(self, image: Image.Image) -> str:
        """Compute perceptual hash"""
        return str(imagehash.phash(image))
    
    def extract_text_enhanced(self, image: Image.Image) -> Tuple[str, List[str]]:
        """Extract text using both Tesseract and EasyOCR for better results"""
        all_text_lines = []
        
        # Use Tesseract first (lighter on memory)
        try:
            tesseract_text = pytesseract.image_to_string(image)
            tesseract_lines = [line.strip() for line in tesseract_text.split('\n') if line.strip()]
            all_text_lines.extend(tesseract_lines)
        except Exception as e:
            print(f"Tesseract OCR failed: {e}")
        
        # Use EasyOCR for better text detection (only if needed)
        try:
            reader = get_easyocr_reader()
            if reader is not None:
                # Convert PIL Image to numpy array
                img_array = np.array(image)
                results = reader.readtext(img_array, detail=1)
                
                # Extract all text detected by EasyOCR
                for (bbox, text, prob) in results:
                    if prob > 0.3:  # Only include text with confidence > 30%
                        all_text_lines.append(text.strip())
        except Exception as e:
            print(f"EasyOCR failed: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_lines = []
        for line in all_text_lines:
            line_lower = line.lower()
            if line_lower not in seen and len(line) > 1:
                seen.add(line_lower)
                unique_lines.append(line)
        
        # Combine all text
        combined_text = '\n'.join(unique_lines)
        
        return combined_text, unique_lines
    
    def classify_content(self, image: Image.Image, text: str) -> Dict[str, float]:
        """Classify image content using CLIP zero-shot classification"""
        try:
            model, processor = get_clip_model()
            
            # Prepare text prompts
            prompts = [f"a photo of {category}" for category in self.content_categories]
            
            # Process image and text
            inputs = processor(
                text=prompts,
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            with torch.no_grad():
                outputs = model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1).numpy()[0]
            
            # Create classification results
            classification = {}
            for category, prob in zip(self.content_categories, probs):
                # Simplify category names
                simple_category = category.replace("a photo of ", "").replace(" or ", "/")
                classification[simple_category] = float(prob)
            
            return classification
        except Exception as e:
            print(f"Content classification failed: {e}")
            return {}
    
    def extract_entities_enhanced(self, text: str, text_lines: List[str]) -> Dict[str, List[str]]:
        """Extract named entities with better categorization"""
        if not text:
            return {"persons": [], "organizations": [], "locations": [], "dates": [], "other": []}
        
        nlp = get_nlp()
        doc = nlp(text)
        
        entities = {
            "persons": [],
            "organizations": [],
            "locations": [],
            "dates": [],
            "other": []
        }
        
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                entities["persons"].append(ent.text)
            elif ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"]:
                entities["organizations"].append(ent.text)
            elif ent.label_ in ["GPE", "LOC", "FAC"]:
                entities["locations"].append(ent.text)
            elif ent.label_ in ["DATE", "TIME"]:
                entities["dates"].append(ent.text)
            else:
                entities["other"].append(ent.text)
        
        # Also extract potential titles (capitalized phrases)
        potential_titles = []
        for line in text_lines:
            # Check if line is mostly capitalized or title case
            if len(line) > 3 and (line.isupper() or line.istitle()):
                potential_titles.append(line)
        
        entities["potential_titles"] = potential_titles[:20]  # Limit to 20
        
        return entities
    
    def get_text_embedding(self, text: str) -> np.ndarray:
        """Get text embedding using SentenceTransformer"""
        if not text:
            return np.zeros(384)  # MiniLM dimension
        model = get_text_model()
        embedding = model.encode([text])[0]
        return embedding
    
    def get_image_embedding(self, image: Image.Image) -> np.ndarray:
        """Get image embedding using CLIP"""
        model, processor = get_clip_model()
        inputs = processor(images=image, return_tensors="pt")
        with torch.no_grad():
            image_features = model.get_image_features(**inputs)
        return image_features.numpy().flatten()
    
    def create_thumbnails(self, image: Image.Image, image_id: str) -> Tuple[Path, Path]:
        """Create thumbnails in two sizes: 512x512 for graph, 1024x1024 for details"""
        # Small thumbnail for graph (512x512)
        thumbnail_small = image.copy()
        thumbnail_small.thumbnail((512, 512), Image.Resampling.LANCZOS)
        thumbnail_small_path = self.thumbnails_dir / f"{image_id}.jpg"
        thumbnail_small.save(thumbnail_small_path, "JPEG", quality=95)
        
        # Large thumbnail for detail view (1024x1024)
        thumbnail_large = image.copy()
        thumbnail_large.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
        thumbnail_large_path = self.thumbnails_large_dir / f"{image_id}.jpg"
        thumbnail_large.save(thumbnail_large_path, "JPEG", quality=95)
        
        return thumbnail_small_path, thumbnail_large_path
    
    async def check_duplicate(self, sha256: str) -> Optional[str]:
        """Check if image already exists by SHA256 in MongoDB"""
        result = await self.db.images.find_one({"sha256": sha256})
        return result["id"] if result else None
    
    def get_image_creation_date(self, image_path: Path) -> datetime:
        """Get image creation date from file or EXIF data"""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()
            if exif_data and 36867 in exif_data:  # DateTimeOriginal
                date_str = exif_data[36867]
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except:
            pass
        
        # Fallback to file creation time
        stat = image_path.stat()
        return datetime.fromtimestamp(stat.st_ctime)
    
    async def ingest_image(self, image_path: Path, image_id: Optional[str] = None) -> Dict:
        """Ingest a single image through the enhanced pipeline"""
        if image_id is None:
            image_id = hashlib.sha5(str(image_path).encode()).hexdigest()[:16]
        
        # Compute SHA256
        sha256 = self.compute_sha256(image_path)
        
        # Check for duplicates
        existing_id = await self.check_duplicate(sha256)
        if existing_id:
            print(f"Duplicate found: {image_path} -> {existing_id}")
            return {"status": "duplicate", "id": existing_id}
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Compute perceptual hash
        phash = self.compute_phash(image)
        
        # Extract text (enhanced with EasyOCR)
        ocr_text, text_lines = self.extract_text_enhanced(image)
        
        # Classify content
        classification = self.classify_content(image, ocr_text)
        
        # Get primary category (highest confidence)
        primary_category = max(classification, key=classification.get) if classification else "other"
        
        # Extract entities (enhanced)
        entities = self.extract_entities_enhanced(ocr_text, text_lines)
        
        # Get embeddings
        text_embedding = self.get_text_embedding(ocr_text)
        image_embedding = self.get_image_embedding(image)
        
        # Create thumbnails (both sizes)
        thumbnail_small_path, thumbnail_large_path = self.create_thumbnails(image, image_id)
        
        # Get image creation date
        creation_date = self.get_image_creation_date(image_path)
        
        # Prepare metadata for MongoDB
        metadata = {
            "id": image_id,
            "sha256": sha256,
            "phash": phash,
            "filename": image_path.name,
            "ocr_text": ocr_text,
            "text_lines": text_lines,
            "entities": entities,
            "classification": classification,
            "primary_category": primary_category,
            "thumbnail_path": str(thumbnail_small_path),
            "thumbnail_large_path": str(thumbnail_large_path),
            "creation_date": creation_date,
            "ingestion_date": datetime.now(),
            "image_size": {
                "width": image.width,
                "height": image.height
            },
            "file_size": image_path.stat().st_size
        }
        
        # Save to MongoDB
        await self.db.images.insert_one(metadata)
        
        # Save metadata JSON (for backup)
        metadata_copy = metadata.copy()
        metadata_copy['creation_date'] = metadata_copy['creation_date'].isoformat()
        metadata_copy['ingestion_date'] = metadata_copy['ingestion_date'].isoformat()
        
        metadata_path = self.metadata_dir / f"{image_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata_copy, f, indent=2)
        
        # Save to SQLite (for FAISS compatibility)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Flatten entities for SQLite
        all_entities = []
        for entity_type, entity_list in entities.items():
            all_entities.extend(entity_list)
        
        cursor.execute('''
            INSERT INTO images (id, sha256, phash, filename, ocr_text, entities, 
                              text_embedding, image_embedding, thumbnail_path, metadata_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_id, sha256, phash, image_path.name, ocr_text, json.dumps(all_entities),
            text_embedding.tobytes(), image_embedding.tobytes(),
            str(thumbnail_small_path), str(metadata_path)
        ))
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "id": image_id,
            "metadata": metadata_copy
        }
    
    async def build_graph_enhanced(self, filters: Dict = None) -> Dict:
        """Build graph with enhanced connections and filtering"""
        # Get all images from MongoDB
        query = {}
        if filters:
            if filters.get('categories'):
                query['primary_category'] = {'$in': filters['categories']}
            if filters.get('date_from') or filters.get('date_to'):
                date_query = {}
                if filters.get('date_from'):
                    date_query['$gte'] = filters['date_from']
                if filters.get('date_to'):
                    date_query['$lte'] = filters['date_to']
                query['creation_date'] = date_query
        
        cursor = self.db.images.find(query)
        images = await cursor.to_list(length=None)
        
        nodes = []
        links = []
        
        # Create nodes
        for img in images:
            nodes.append({
                "id": img["id"],
                "group": 1,
                "category": img.get("primary_category", "other"),
                "filename": img.get("filename", ""),
                "creation_date": img.get("creation_date").isoformat() if img.get("creation_date") else None
            })
        
        # Create connections
        connection_filter = filters.get('connection_types', ['all']) if filters else ['all']
        show_all = 'all' in connection_filter
        
        for i, img1 in enumerate(images):
            for img2 in images[i+1:]:
                connections = []
                
                # Date-based connection
                if show_all or 'date' in connection_filter:
                    date1 = img1.get("creation_date")
                    date2 = img2.get("creation_date")
                    if date1 and date2:
                        # Same day
                        if date1.date() == date2.date():
                            connections.append({
                                "type": "date",
                                "strength": 3,
                                "reason": "Same creation date"
                            })
                
                # Category-based connection
                if show_all or 'category' in connection_filter:
                    cat1 = img1.get("primary_category")
                    cat2 = img2.get("primary_category")
                    if cat1 and cat2 and cat1 == cat2 and cat1 != "other":
                        connections.append({
                            "type": "category",
                            "strength": 2,
                            "reason": f"Same category: {cat1}"
                        })
                
                # Entity-based connection
                if show_all or 'entity' in connection_filter:
                    entities1 = img1.get("entities", {})
                    entities2 = img2.get("entities", {})
                    
                    # Flatten entities
                    all_entities1 = set()
                    all_entities2 = set()
                    for entity_list in entities1.values():
                        if isinstance(entity_list, list):
                            all_entities1.update(entity_list)
                    for entity_list in entities2.values():
                        if isinstance(entity_list, list):
                            all_entities2.update(entity_list)
                    
                    shared = all_entities1.intersection(all_entities2)
                    if shared:
                        connections.append({
                            "type": "entity",
                            "strength": len(shared),
                            "reason": f"Shared entities: {', '.join(list(shared)[:3])}"
                        })
                
                # Similarity-based connection (from embeddings in SQLite)
                if show_all or 'similarity' in connection_filter:
                    # Get embeddings from SQLite
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT image_embedding FROM images WHERE id = ?", (img1["id"],))
                    emb1_result = cursor.fetchone()
                    cursor.execute("SELECT image_embedding FROM images WHERE id = ?", (img2["id"],))
                    emb2_result = cursor.fetchone()
                    conn.close()
                    
                    if emb1_result and emb2_result:
                        emb1 = np.frombuffer(emb1_result[0], dtype=np.float32)
                        emb2 = np.frombuffer(emb2_result[0], dtype=np.float32)
                        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                        
                        if similarity > 0.8:
                            connections.append({
                                "type": "similarity",
                                "strength": float(similarity),
                                "reason": f"Visual similarity: {similarity:.2f}"
                            })
                
                # Add link if any connections found
                if connections:
                    # Use the strongest connection
                    primary_conn = max(connections, key=lambda x: x['strength'])
                    links.append({
                        "source": img1["id"],
                        "target": img2["id"],
                        "value": primary_conn['strength'],
                        "type": primary_conn['type'],
                        "reason": primary_conn['reason'],
                        "all_connections": connections
                    })
        
        return {"nodes": nodes, "links": links}
    
    async def get_metadata(self, image_id: str) -> Optional[Dict]:
        """Get metadata for a specific image from MongoDB"""
        result = await self.db.images.find_one({"id": image_id})
        if result:
            # Convert datetime to ISO format
            if result.get('creation_date'):
                result['creation_date'] = result['creation_date'].isoformat()
            if result.get('ingestion_date'):
                result['ingestion_date'] = result['ingestion_date'].isoformat()
            # Remove MongoDB _id
            result.pop('_id', None)
        return result
    
    async def search_images(self, query: str) -> List[Dict]:
        """Search images with enhanced search capabilities"""
        if not query or not query.strip():
            return []
        
        query_lower = query.lower().strip()
        
        # Search in MongoDB
        search_query = {
            '$or': [
                {'filename': {'$regex': query_lower, '$options': 'i'}},
                {'ocr_text': {'$regex': query_lower, '$options': 'i'}},
                {'text_lines': {'$regex': query_lower, '$options': 'i'}},
                {'primary_category': {'$regex': query_lower, '$options': 'i'}},
                {'entities.persons': {'$regex': query_lower, '$options': 'i'}},
                {'entities.organizations': {'$regex': query_lower, '$options': 'i'}},
                {'entities.potential_titles': {'$regex': query_lower, '$options': 'i'}}
            ]
        }
        
        cursor = self.db.images.find(search_query)
        results = await cursor.to_list(length=100)
        
        # Convert dates to ISO format
        for result in results:
            if result.get('creation_date'):
                result['creation_date'] = result['creation_date'].isoformat()
            if result.get('ingestion_date'):
                result['ingestion_date'] = result['ingestion_date'].isoformat()
            result.pop('_id', None)
        
        return results
    
    def build_faiss_indexes(self):
        """Build FAISS indexes for text and image embeddings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, text_embedding, image_embedding FROM images")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            print("No images to index")
            return
        
        text_embeddings = []
        image_embeddings = []
        ids = []
        
        for row in rows:
            image_id, text_emb_bytes, image_emb_bytes = row
            ids.append(image_id)
            text_embeddings.append(np.frombuffer(text_emb_bytes, dtype=np.float32))
            image_embeddings.append(np.frombuffer(image_emb_bytes, dtype=np.float32))
        
        # Text FAISS index
        text_dim = len(text_embeddings[0])
        self.text_index = faiss.IndexFlatL2(text_dim)
        self.text_index.add(np.array(text_embeddings))
        self.text_ids = ids
        
        # Image FAISS index
        image_dim = len(image_embeddings[0])
        self.image_index = faiss.IndexFlatL2(image_dim)
        self.image_index.add(np.array(image_embeddings))
        self.image_ids = ids
        
        # Save indexes
        faiss.write_index(self.text_index, str(self.indexes_dir / "text_index.faiss"))
        faiss.write_index(self.image_index, str(self.indexes_dir / "image_index.faiss"))
        
        with open(self.indexes_dir / "text_ids.json", 'w') as f:
            json.dump(self.text_ids, f)
        with open(self.indexes_dir / "image_ids.json", 'w') as f:
            json.dump(self.image_ids, f)
        
        print(f"Built FAISS indexes: {len(ids)} images")
