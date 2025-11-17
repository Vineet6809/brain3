import pytest
import requests
from pathlib import Path
from PIL import Image
import io

BASE_URL = "http://localhost:8000"

def test_ingest_image():
    """
    Test image ingestion endpoint
    """
    # Create a simple test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    # Send to ingest endpoint
    files = {'file': ('test_image.png', img_bytes, 'image/png')}
    response = requests.post(f"{BASE_URL}/api/ingest", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] in ['success', 'duplicate']
    assert 'id' in data
    
    image_id = data['id']
    
    # Test get node endpoint
    node_response = requests.get(f"{BASE_URL}/api/node/{image_id}")
    assert node_response.status_code == 200
    node_data = node_response.json()
    assert node_data['id'] == image_id
    
    # Test get thumbnail endpoint
    thumbnail_response = requests.get(f"{BASE_URL}/api/thumbnail/{image_id}")
    assert thumbnail_response.status_code == 200
    assert thumbnail_response.headers['content-type'] == 'image/jpeg'

def test_graph_endpoint():
    """
    Test graph endpoint
    """
    response = requests.get(f"{BASE_URL}/api/graph")
    assert response.status_code == 200
    data = response.json()
    assert 'nodes' in data
    assert 'links' in data
    assert isinstance(data['nodes'], list)
    assert isinstance(data['links'], list)

def test_health_check():
    """
    Test existing health check endpoint
    """
    response = requests.get(f"{BASE_URL}/api/")
    assert response.status_code == 200
    data = response.json()
    assert data['message'] == 'Hello World'
