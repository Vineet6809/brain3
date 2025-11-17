import React, { useEffect, useState, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000';

function App() {
  const [graph, setGraph] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [uploadStatus, setUploadStatus] = useState('');
  const [selectedNode, setSelectedNode] = useState(null);

  // Fetch graph data
  const fetchGraph = useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetch(`${BACKEND_URL}/api/graph`);
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

    const formData = new FormData();
    formData.append('file', file);

    try {
      setUploadStatus('Uploading...');
      const response = await fetch(`${BACKEND_URL}/api/ingest`, {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      
      if (result.status === 'success') {
        setUploadStatus(`Success! Image ID: ${result.id}`);
        // Refresh graph
        setTimeout(fetchGraph, 1000);
      } else if (result.status === 'duplicate') {
        setUploadStatus(`Duplicate image detected. ID: ${result.id}`);
      }
    } catch (error) {
      setUploadStatus(`Error: ${error.message}`);
    }
  };

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

  return (
    <div className="app">
      {/* Control Panel */}
      <div className="control-panel">
        <h1>Image Knowledge Graph</h1>
        
        <div className="upload-section">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileUpload}
            id="file-upload"
          />
          <label htmlFor="file-upload" className="upload-button">
            Upload Image
          </label>
          <button onClick={buildIndex} className="build-index-button">
            Build Index
          </button>
        </div>
        
        {uploadStatus && (
          <div className="status-message">{uploadStatus}</div>
        )}
        
        <div className="stats">
          <p>Nodes: {graph.nodes.length}</p>
          <p>Links: {graph.links.length}</p>
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
            graphData={graph}
            nodeAutoColorBy="group"
            nodeLabel={node => node.id}
            onNodeClick={handleNodeClick}
            nodeRelSize={6}
            linkWidth={link => link.value || 1}
            linkOpacity={0.5}
            backgroundColor="#000011"
          />
        )}
      </div>
    </div>
  );
}

export default App;
