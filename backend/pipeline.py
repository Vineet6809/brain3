import os
import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from PIL import Image
import imagehash
import pytesseract
from sentence_transformers import SentenceTransformer
from transformers import CLIPProcessor, CLIPModel
import torch
import faiss
import spacy
from tqdm import tqdm

# Initialize models (lazy loading)
_text_model = None
_clip_model = None
_clip_processor = None
_nlp = None

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

class ImagePipeline:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.images_dir = self.data_dir / "images"
        self.thumbnails_dir = self.data_dir / "thumbnails"
        self.metadata_dir = self.data_dir / "metadata"
        self.indexes_dir = self.data_dir / "indexes"
        self.db_path = self.data_dir / "metadata.db"
        
        # Create directories
        for d in [self.images_dir, self.thumbnails_dir, self.metadata_dir, self.indexes_dir]:
            d.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite
        self._init_db()
        
        # Initialize FAISS indexes
        self.text_index = None
        self.image_index = None
        self.text_ids = []
        self.image_ids = []
        
    def _init_db(self):
        """Initialize SQLite database"""
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
    
    def extract_text_ocr(self, image: Image.Image) -> str:
        """Extract text using Tesseract OCR"""
        try:
            text = pytesseract.image_to_string(image)
            return text.strip()
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""
    
    def extract_entities(self, text: str) -> List[str]:
        """Extract named entities from text"""
        if not text:
            return []
        nlp = get_nlp()
        doc = nlp(text)
        return [ent.text for ent in doc.ents]
    
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
    
    def create_thumbnail(self, image: Image.Image, image_id: str, size=(256, 256)) -> Path:
        """Create and save thumbnail"""
        thumbnail = image.copy()
        thumbnail.thumbnail(size, Image.Resampling.LANCZOS)
        thumbnail_path = self.thumbnails_dir / f"{image_id}.jpg"
        thumbnail.save(thumbnail_path, "JPEG")
        return thumbnail_path
    
    def check_duplicate(self, sha256: str) -> Optional[str]:
        """Check if image already exists by SHA256"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM images WHERE sha256 = ?", (sha256,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def ingest_image(self, image_path: Path, image_id: Optional[str] = None) -> Dict:
        """Ingest a single image through the pipeline"""
        if image_id is None:
            image_id = hashlib.sha5(str(image_path).encode()).hexdigest()[:16]
        
        # Compute SHA256
        sha256 = self.compute_sha256(image_path)
        
        # Check for duplicates
        existing_id = self.check_duplicate(sha256)
        if existing_id:
            print(f"Duplicate found: {image_path} -> {existing_id}")
            return {"status": "duplicate", "id": existing_id}
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Compute perceptual hash
        phash = self.compute_phash(image)
        
        # Extract text via OCR
        ocr_text = self.extract_text_ocr(image)
        
        # Extract entities
        entities = self.extract_entities(ocr_text)
        
        # Get embeddings
        text_embedding = self.get_text_embedding(ocr_text)
        image_embedding = self.get_image_embedding(image)
        
        # Create thumbnail
        thumbnail_path = self.create_thumbnail(image, image_id)
        
        # Save metadata JSON
        metadata = {
            "id": image_id,
            "sha256": sha256,
            "phash": phash,
            "filename": image_path.name,
            "ocr_text": ocr_text,
            "entities": entities,
            "thumbnail_path": str(thumbnail_path)
        }
        metadata_path = self.metadata_dir / f"{image_id}.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Save to SQLite
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO images (id, sha256, phash, filename, ocr_text, entities, 
                              text_embedding, image_embedding, thumbnail_path, metadata_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            image_id, sha256, phash, image_path.name, ocr_text, json.dumps(entities),
            text_embedding.tobytes(), image_embedding.tobytes(),
            str(thumbnail_path), str(metadata_path)
        ))
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "id": image_id,
            "metadata": metadata
        }
    
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
        
        # Build text index
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
    
    def load_faiss_indexes(self):
        """Load FAISS indexes from disk"""
        text_index_path = self.indexes_dir / "text_index.faiss"
        image_index_path = self.indexes_dir / "image_index.faiss"
        
        if text_index_path.exists():
            self.text_index = faiss.read_index(str(text_index_path))
            with open(self.indexes_dir / "text_ids.json", 'r') as f:
                self.text_ids = json.load(f)
        
        if image_index_path.exists():
            self.image_index = faiss.read_index(str(image_index_path))
            with open(self.indexes_dir / "image_ids.json", 'r') as f:
                self.image_ids = json.load(f)
    
    def search_similar(self, query: str = None, image: Image.Image = None, k: int = 5) -> List[str]:
        """Search for similar images using text or image query"""
        if query:
            if self.text_index is None:
                self.load_faiss_indexes()
            embedding = self.get_text_embedding(query)
            distances, indices = self.text_index.search(np.array([embedding]), k)
            return [self.text_ids[i] for i in indices[0]]
        
        if image:
            if self.image_index is None:
                self.load_faiss_indexes()
            embedding = self.get_image_embedding(image)
            distances, indices = self.image_index.search(np.array([embedding]), k)
            return [self.image_ids[i] for i in indices[0]]
        
        return []
    
    def get_metadata(self, image_id: str) -> Optional[Dict]:
        """Get metadata for a specific image"""
        metadata_path = self.metadata_dir / f"{image_id}.json"
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return None
    
    def build_graph(self, similarity_threshold: float = 0.8) -> Dict:
        """Build graph based on similarity and shared entities"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, entities, image_embedding FROM images")
        rows = cursor.fetchall()
        conn.close()
        
        nodes = []
        links = []
        
        # Create nodes
        for row in rows:
            image_id, entities_json, _ = row
            nodes.append({
                "id": image_id,
                "group": 1,
                "entities": json.loads(entities_json)
            })
        
        # Create edges based on shared entities or embedding similarity
        for i, row1 in enumerate(rows):
            id1, entities1_json, emb1_bytes = row1
            entities1 = set(json.loads(entities1_json))
            emb1 = np.frombuffer(emb1_bytes, dtype=np.float32)
            
            for j, row2 in enumerate(rows[i+1:], start=i+1):
                id2, entities2_json, emb2_bytes = row2
                entities2 = set(json.loads(entities2_json))
                emb2 = np.frombuffer(emb2_bytes, dtype=np.float32)
                
                # Check shared entities
                shared = entities1.intersection(entities2)
                if shared:
                    links.append({
                        "source": id1,
                        "target": id2,
                        "value": len(shared)
                    })
                else:
                    # Check embedding similarity
                    similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
                    if similarity > similarity_threshold:
                        links.append({
                            "source": id1,
                            "target": id2,
                            "value": float(similarity)
                        })
        
        return {"nodes": nodes, "links": links}
