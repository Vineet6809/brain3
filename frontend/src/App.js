import React, { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [uploadStatus, setUploadStatus] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  
  const graphRef = useRef();
  const textureCache = useRef({});

  // Fetch graph data
  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/graph`);
      
      if (!response.ok) {
        console.error('Error fetching graph:', response.status, response.statusText);
        return;
      }
      
      const data = await response.json();
      setGraph(data);
    } catch (error) {
      console.error('Error fetching graph:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  // Handle file upload
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Reset the input value to allow uploading the same file again
    event.target.value = '';

    const formData = new FormData();
    formData.append('file', file);

    const progressInterval = setInterval(() => {
      setUploadProgress(prev => Math.min(prev + 10, 90));
    }, 200);

    try {
      setIsUploading(true);
      setUploadProgress(0);
      setUploadStatus('Uploading...');

      const response = await fetch(`${BACKEND_URL}/api/ingest`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      // Check if response is ok before parsing
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Upload failed: ${errorText}`);
      }

      const result = await response.json();
      setUploadProgress(100);
      
      if (result.status === 'success') {
        setUploadStatus(`Success! Image ID: ${result.id}`);
        // Refresh graph
        setTimeout(() => {
          fetchGraph();
          setIsUploading(false);
          setUploadProgress(0);
          setUploadStatus('');
        }, 2000);
      } else if (result.status === 'duplicate') {
        setUploadStatus(`Duplicate image detected. ID: ${result.id}`);
        setTimeout(() => {
          setIsUploading(false);
          setUploadProgress(0);
          setUploadStatus('');
        }, 2000);
      } else {
        setUploadStatus(result.message || 'Upload completed');
        setTimeout(() => {
          setIsUploading(false);
          setUploadProgress(0);
          setUploadStatus('');
        }, 2000);
      }
    } catch (error) {
      clearInterval(progressInterval);
      console.error('Upload error:', error);
      setUploadStatus(`Error: ${error.message}`);
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  // Handle search
  const handleSearch = useCallback(async (query) => {
    setSearchQuery(query);
    
    if (!query || query.trim().length === 0) {
      setSearchResults([]);
      setHighlightNodes(new Set());
      return;
    }

    try {
      const response = await fetch(`${BACKEND_URL}/api/search?query=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        console.error('Search failed:', response.status, response.statusText);
        return;
      }
      
      const data = await response.json();
      
      setSearchResults(data.nodes || []);
      
      // Highlight matching nodes
      const nodeIds = new Set(data.nodes.map(node => node.id));
      setHighlightNodes(nodeIds);
      
      // Focus on first result if available
      if (data.nodes && data.nodes.length > 0 && graphRef.current) {
        const firstNode = graph.nodes.find(n => n.id === data.nodes[0].id);
        if (firstNode) {
          graphRef.current.centerAt(firstNode.x, firstNode.y, 1000);
          graphRef.current.zoom(8, 1000);
        }
      }
    } catch (error) {
      console.error('Error searching:', error);
    }
  }, [graph.nodes]);

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchQuery) {
        handleSearch(searchQuery);
      }
    }, 300);

    return () => clearTimeout(timer);
  }, [searchQuery, handleSearch]);

  // Handle node click
  const handleNodeClick = useCallback(async (node) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/node/${node.id}`);
      const metadata = await response.json();
      setSelectedNode({
        ...metadata,
        thumbnailUrl: `${BACKEND_URL}/api/thumbnail/${node.id}`
      });
    } catch (error) {
      console.error('Error fetching node details:', error);
    }
  }, []);

  // Build FAISS index
  const buildIndex = async () => {
    try {
      setUploadStatus('Building index...');
      const response = await fetch(`${BACKEND_URL}/api/build-index`, {
        method: 'POST',
      });
      const result = await response.json();
      setUploadStatus(result.message);
    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    }
  };

  // Create sprite texture for node with image
  const createNodeTexture = useCallback((node) => {
    const thumbnailUrl = `${BACKEND_URL}/api/thumbnail/${node.id}`;
    
    // Return cached texture if available
    if (textureCache.current[node.id]) {
      return textureCache.current[node.id];
    }

    // Create a canvas for the node
    const canvas = document.createElement('canvas');
    const size = 128;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Draw background
    ctx.fillStyle = highlightNodes.has(node.id) ? '#FFD700' : '#667eea';
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2, 0, 2 * Math.PI);
    ctx.fill();

    // Load and draw image
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      ctx.save();
      ctx.beginPath();
      ctx.arc(size / 2, size / 2, size / 2 - 4, 0, 2 * Math.PI);
      ctx.clip();
      ctx.drawImage(img, 4, 4, size - 8, size - 8);
      ctx.restore();
      
      // Update texture
      texture.needsUpdate = true;
    };
    img.src = thumbnailUrl;

    const texture = new THREE.CanvasTexture(canvas);
    textureCache.current[node.id] = texture;
    
    return texture;
  }, [highlightNodes]);

  // Custom node rendering with image sprites
  const nodeThreeObject = useCallback((node) => {
    const texture = createNodeTexture(node);
    const material = new THREE.SpriteMaterial({ 
      map: texture,
      transparent: true,
      opacity: highlightNodes.size > 0 ? (highlightNodes.has(node.id) ? 1 : 0.3) : 1
    });
    const sprite = new THREE.Sprite(material);
    sprite.scale.set(12, 12, 1);
    
    return sprite;
  }, [createNodeTexture, highlightNodes]);

  // Clear search
  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setHighlightNodes(new Set());
  };

  return (
    <div className="app">
      {/* Control Panel */}
      <div className="control-panel">
        <h1>Image Knowledge Graph</h1>
        
        {/* Search Bar */}
        <div className="search-section">
          <input
            type="text"
            placeholder="Search images..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          {searchQuery && (
            <button onClick={clearSearch} className="clear-search-button">
              ×
            </button>
          )}
          {searchResults.length > 0 && (
            <div className="search-results-count">
              Found {searchResults.length} result(s)
            </div>
          )}
        </div>
        
        {/* Upload Section */}
        <div className="upload-section">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            id="file-upload"
            disabled={isUploading}
          />
          <label 
            htmlFor="file-upload" 
            className={`upload-button ${isUploading ? 'disabled' : ''}`}
          >
            {isUploading ? 'Uploading...' : 'Upload Image'}
          </label>
          <button 
            onClick={buildIndex} 
            className="build-index-button"
            disabled={isUploading}
          >
            Build Index
          </button>
        </div>
        
        {/* Progress Bar */}
        {isUploading && (
          <div className="progress-container">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            <div className="progress-text">{uploadProgress}%</div>
          </div>
        )}
        
        {uploadStatus && !isUploading && (
          <div className="status-message">{uploadStatus}</div>
        )}
        
        <div className="stats">
          <p>Nodes: {graph.nodes.length}</p>
          <p>Links: {graph.links.length}</p>
          {searchResults.length > 0 && (
            <p>Matches: {searchResults.length}</p>
          )}
        </div>

        {/* Instructions */}
        <div className="instructions">
          <p><strong>Controls:</strong></p>
          <p>• Rotate: Left drag</p>
          <p>• Zoom: Mouse wheel</p>
          <p>• Pan: Right drag</p>
          <p>• Click node: View details</p>
        </div>
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <div className="node-details">
          <button 
            className="close-button"
            onClick={() => setSelectedNode(null)}
          >
            ×
          </button>
          <h3>Node Details</h3>
          <img 
            src={selectedNode.thumbnailUrl} 
            alt="Thumbnail" 
            className="thumbnail"
          />
          <p><strong>ID:</strong> {selectedNode.id}</p>
          <p><strong>Filename:</strong> {selectedNode.filename}</p>
          {selectedNode.ocr_text && (
            <div>
              <strong>OCR Text:</strong>
              <p className="ocr-text">{selectedNode.ocr_text}</p>
            </div>
          )}
          {selectedNode.entities && selectedNode.entities.length > 0 && (
            <div>
              <strong>Entities:</strong>
              <div className="entities">
                {selectedNode.entities.map((entity, i) => (
                  <span key={i} className="entity-tag">{entity}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* 3D Graph */}
      <div className="graph-container">
        {loading ? (
          <div className="loading">Loading graph...</div>
        ) : (
          <ForceGraph3D
            ref={graphRef}
            graphData={graph}
            nodeThreeObject={nodeThreeObject}
            nodeLabel={node => node.id}
            onNodeClick={handleNodeClick}
            linkWidth={link => link.value || 1}
            linkOpacity={0.5}
            backgroundColor="#000011"
            enableNodeDrag={true}
            enableNavigationControls={true}
          />
        )}
      </div>
    </div>
  );
}

export default App;
