import React, { useEffect, useState, useCallback, useRef, useMemo } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import * as THREE from 'three';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function EnhancedApp() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [uploadStatus, setUploadStatus] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [highlightNodes, setHighlightNodes] = useState(new Set());
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  
  // Filter states
  const [categories, setCategories] = useState([]);
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [connectionTypes, setConnectionTypes] = useState([]);
  const [selectedConnectionTypes, setSelectedConnectionTypes] = useState(['all']);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [stats, setStats] = useState(null);
  
  const graphRef = useRef();
  const textureCache = useRef({});

  // Fetch categories and connection types
  useEffect(() => {
    const fetchMetadata = async () => {
      try {
        const [categoriesRes, connectionTypesRes, statsRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/categories`),
          fetch(`${BACKEND_URL}/api/connection-types`),
          fetch(`${BACKEND_URL}/api/stats`)
        ]);
        
        const categoriesData = await categoriesRes.json();
        const connectionTypesData = await connectionTypesRes.json();
        const statsData = await statsRes.json();
        
        setCategories(categoriesData.categories || []);
        setConnectionTypes(connectionTypesData.connection_types || []);
        setStats(statsData);
      } catch (error) {
        console.error('Error fetching metadata:', error);
      }
    };
    
    fetchMetadata();
  }, []);

  // Fetch graph data with filters
  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true);
      
      // Build filter object
      const filters = {};
      if (selectedCategories.length > 0) {
        filters.categories = selectedCategories;
      }
      if (dateFrom) {
        filters.date_from = dateFrom;
      }
      if (dateTo) {
        filters.date_to = dateTo;
      }
      if (selectedConnectionTypes.length > 0) {
        filters.connection_types = selectedConnectionTypes;
      }
      
      // Fetch with filters
      const response = await fetch(`${BACKEND_URL}/api/graph`, {
        method: Object.keys(filters).length > 0 ? 'POST' : 'GET',
        headers: Object.keys(filters).length > 0 ? {
          'Content-Type': 'application/json',
        } : undefined,
        body: Object.keys(filters).length > 0 ? JSON.stringify(filters) : undefined,
      });
      
      const data = await response.json();
      setGraph(data);
    } catch (error) {
      console.error('Error fetching graph:', error);
    } finally {
      setLoading(false);
    }
  }, [selectedCategories, dateFrom, dateTo, selectedConnectionTypes]);

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
      const data = await response.json();
      
      setSearchResults(data.nodes || []);
      
      const nodeIds = new Set(data.nodes.map(node => node.id));
      setHighlightNodes(nodeIds);
      
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
        thumbnailUrl: `${BACKEND_URL}/api/thumbnail/${node.id}?size=large`
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

  // Get link color based on connection type
  const getLinkColor = (link) => {
    const type = link.type || 'similarity';
    const colors = {
      date: '#FFD700',      // Gold
      category: '#FF6B6B',  // Red
      entity: '#4ECDC4',    // Teal
      similarity: '#667eea' // Purple
    };
    return colors[type] || colors.similarity;
  };

  // Create sprite texture for node with image
  const createNodeTexture = useCallback((node) => {
    const thumbnailUrl = `${BACKEND_URL}/api/thumbnail/${node.id}?size=small`;
    
    if (textureCache.current[node.id]) {
      return textureCache.current[node.id];
    }

    const canvas = document.createElement('canvas');
    const size = 128;
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');

    // Get category color
    const categoryColors = {
      'anime/manga': '#FF1493',
      'movie/tv show poster': '#FFD700',
      'educational/academic content': '#4169E1',
      'programming/coding screenshot': '#32CD32',
      'document/text': '#808080',
      'social media post': '#1DA1F2',
      'meme/comic': '#FF4500',
      'photo/picture': '#9370DB',
      'diagram/chart': '#FF8C00',
      'other': '#667eea'
    };
    
    const bgColor = highlightNodes.has(node.id) 
      ? '#FFD700' 
      : (categoryColors[node.category] || '#667eea');

    // Draw background
    ctx.fillStyle = bgColor;
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
      
      texture.needsUpdate = true;
    };
    img.src = thumbnailUrl;

    const texture = new THREE.CanvasTexture(canvas);
    textureCache.current[node.id] = texture;
    
    return texture;
  }, [highlightNodes]);

  // Custom node rendering
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

  // Toggle category filter
  const toggleCategory = (categoryId) => {
    setSelectedCategories(prev => 
      prev.includes(categoryId)
        ? prev.filter(c => c !== categoryId)
        : [...prev, categoryId]
    );
  };

  // Toggle connection type filter
  const toggleConnectionType = (typeId) => {
    if (typeId === 'all') {
      setSelectedConnectionTypes(['all']);
    } else {
      setSelectedConnectionTypes(prev => {
        const filtered = prev.filter(t => t !== 'all');
        return filtered.includes(typeId)
          ? filtered.filter(t => t !== typeId)
          : [...filtered, typeId];
      });
    }
  };

  // Clear all filters
  const clearFilters = () => {
    setSelectedCategories([]);
    setSelectedConnectionTypes(['all']);
    setDateFrom('');
    setDateTo('');
  };

  return (
    <div className="app">
      {/* Control Panel */}
      <div className="control-panel">
        <h1>🖼️ Image Knowledge Graph</h1>
        
        {/* Search Bar */}
        <div className="search-section">
          <input
            type="text"
            placeholder="Search images by content, text, entities..."
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
            {isUploading ? 'Uploading...' : '📤 Upload Image'}
          </label>
          <button 
            onClick={buildIndex} 
            className="build-index-button"
            disabled={isUploading}
          >
            🔍 Build Index
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
        
        {/* Filters Toggle */}
        <button 
          onClick={() => setShowFilters(!showFilters)} 
          className="filters-toggle"
        >
          {showFilters ? '🔽 Hide Filters' : '🔼 Show Filters'}
        </button>
        
        {/* Filters Section */}
        {showFilters && (
          <div className="filters-section">
            <div className="filter-group">
              <h4>📁 Content Categories</h4>
              <div className="filter-options">
                {categories.map(cat => (
                  <label key={cat.id} className="filter-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedCategories.includes(cat.id)}
                      onChange={() => toggleCategory(cat.id)}
                    />
                    {cat.label}
                  </label>
                ))}
              </div>
            </div>
            
            <div className="filter-group">
              <h4>🔗 Connection Types</h4>
              <div className="filter-options">
                {connectionTypes.map(type => (
                  <label key={type.id} className="filter-checkbox">
                    <input
                      type="radio"
                      checked={selectedConnectionTypes.includes(type.id)}
                      onChange={() => toggleConnectionType(type.id)}
                      name="connection-type"
                    />
                    {type.label}
                  </label>
                ))}
              </div>
            </div>
            
            <div className="filter-group">
              <h4>📅 Date Range</h4>
              <div className="date-filters">
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="date-input"
                  placeholder="From"
                />
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="date-input"
                  placeholder="To"
                />
              </div>
            </div>
            
            <button onClick={clearFilters} className="clear-filters-button">
              Clear All Filters
            </button>
          </div>
        )}
        
        {/* Stats */}
        <div className="stats">
          <p>📊 Nodes: {graph.nodes.length}</p>
          <p>🔗 Links: {graph.links.length}</p>
          {stats && <p>💾 Total: {stats.total_images}</p>}
        </div>

        {/* Legend */}
        <div className="legend">
          <h4>Connection Types:</h4>
          <div className="legend-item">
            <span className="legend-color" style={{background: '#FFD700'}}></span>
            <span>Date-Based</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{background: '#FF6B6B'}}></span>
            <span>Category</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{background: '#4ECDC4'}}></span>
            <span>Entities</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{background: '#667eea'}}></span>
            <span>Similarity</span>
          </div>
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
          <h3>📷 Node Details</h3>
          <img 
            src={selectedNode.thumbnailUrl} 
            alt="Thumbnail" 
            className="thumbnail-large"
          />
          <p><strong>ID:</strong> {selectedNode.id}</p>
          <p><strong>Filename:</strong> {selectedNode.filename}</p>
          
          {selectedNode.primary_category && (
            <p><strong>Category:</strong> {selectedNode.primary_category}</p>
          )}
          
          {selectedNode.creation_date && (
            <p><strong>Created:</strong> {new Date(selectedNode.creation_date).toLocaleDateString()}</p>
          )}
          
          {selectedNode.ocr_text && (
            <div>
              <strong>📝 Extracted Text:</strong>
              <p className="ocr-text">{selectedNode.ocr_text}</p>
            </div>
          )}
          
          {selectedNode.text_lines && selectedNode.text_lines.length > 0 && (
            <div>
              <strong>📄 Text Lines ({selectedNode.text_lines.length}):</strong>
              <div className="text-lines">
                {selectedNode.text_lines.slice(0, 10).map((line, i) => (
                  <div key={i} className="text-line">{line}</div>
                ))}
                {selectedNode.text_lines.length > 10 && (
                  <div className="text-line">... and {selectedNode.text_lines.length - 10} more</div>
                )}
              </div>
            </div>
          )}
          
          {selectedNode.entities && (
            <div>
              {selectedNode.entities.persons && selectedNode.entities.persons.length > 0 && (
                <div>
                  <strong>👤 Persons:</strong>
                  <div className="entities">
                    {selectedNode.entities.persons.map((entity, i) => (
                      <span key={i} className="entity-tag">{entity}</span>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedNode.entities.organizations && selectedNode.entities.organizations.length > 0 && (
                <div>
                  <strong>🏢 Organizations/Titles:</strong>
                  <div className="entities">
                    {selectedNode.entities.organizations.map((entity, i) => (
                      <span key={i} className="entity-tag">{entity}</span>
                    ))}
                  </div>
                </div>
              )}
              
              {selectedNode.entities.potential_titles && selectedNode.entities.potential_titles.length > 0 && (
                <div>
                  <strong>🎬 Potential Titles:</strong>
                  <div className="entities">
                    {selectedNode.entities.potential_titles.map((entity, i) => (
                      <span key={i} className="entity-tag potential-title">{entity}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          
          {selectedNode.classification && (
            <div>
              <strong>🏷️ Classification Confidence:</strong>
              <div className="classification">
                {Object.entries(selectedNode.classification)
                  .sort((a, b) => b[1] - a[1])
                  .slice(0, 3)
                  .map(([category, confidence]) => (
                    <div key={category} className="classification-item">
                      <span>{category}</span>
                      <span>{(confidence * 100).toFixed(1)}%</span>
                    </div>
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
            nodeLabel={node => `${node.filename}\nCategory: ${node.category}`}
            onNodeClick={handleNodeClick}
            linkWidth={link => (link.value || 1) * 0.5}
            linkColor={getLinkColor}
            linkOpacity={0.6}
            backgroundColor="#000011"
            enableNodeDrag={true}
            enableNavigationControls={true}
          />
        )}
      </div>
    </div>
  );
}

export default EnhancedApp;
