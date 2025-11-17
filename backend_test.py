#!/usr/bin/env python3
"""
Backend API Testing for Image Knowledge Graph Application
Tests all endpoints with focus on the /api/ingest endpoint that's causing issues
"""

import requests
import json
import os
from pathlib import Path
import time

# Get backend URL from frontend .env file
def get_backend_url():
    frontend_env_path = Path("/app/frontend/.env")
    if frontend_env_path.exists():
        with open(frontend_env_path, 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    return "http://localhost:8001"

BASE_URL = get_backend_url()
API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

def test_endpoint(method, endpoint, **kwargs):
    """Helper function to test an endpoint and return detailed results"""
    url = f"{API_BASE}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing {method.upper()} {endpoint}")
    print(f"Full URL: {url}")
    
    try:
        if method.lower() == 'get':
            response = requests.get(url, timeout=30, **kwargs)
        elif method.lower() == 'post':
            response = requests.post(url, timeout=30, **kwargs)
        else:
            print(f"Unsupported method: {method}")
            return False
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # Check Content-Type
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        
        # Try to get response body
        try:
            if 'application/json' in content_type:
                response_data = response.json()
                print(f"Response Body (JSON): {json.dumps(response_data, indent=2)}")
            else:
                response_text = response.text[:500]  # First 500 chars
                print(f"Response Body (Text): {response_text}")
        except Exception as e:
            print(f"Error parsing response body: {e}")
            print(f"Raw response: {response.content[:200]}")
        
        return response.status_code < 400
        
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

def test_image_upload():
    """Test the critical /api/ingest endpoint with actual image upload"""
    print(f"\n{'='*60}")
    print("CRITICAL TEST: Image Upload (/api/ingest)")
    print(f"{'='*60}")
    
    # Check if test image exists
    test_image_path = Path("/app/test_invoice.png")
    if not test_image_path.exists():
        print("ERROR: Test image not found at /app/test_invoice.png")
        return False
    
    url = f"{API_BASE}/ingest"
    print(f"Upload URL: {url}")
    
    try:
        # Prepare file for upload
        with open(test_image_path, 'rb') as f:
            files = {'file': ('test_invoice.png', f, 'image/png')}
            
            print("Uploading image...")
            response = requests.post(url, files=files, timeout=60)
            
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # Check Content-Type specifically
        content_type = response.headers.get('content-type', '')
        print(f"Content-Type: {content_type}")
        
        if 'application/json' not in content_type:
            print(f"WARNING: Expected application/json but got {content_type}")
        
        # Try to parse response
        try:
            response_data = response.json()
            print(f"Response Body (JSON): {json.dumps(response_data, indent=2)}")
            
            # Check if response has expected structure
            if isinstance(response_data, dict):
                if 'image_id' in response_data:
                    print("✅ Response contains image_id")
                    return response_data.get('image_id')
                else:
                    print("⚠️  Response missing image_id field")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            print(f"Raw response: {response.text[:500]}")
            return False
        
        return response.status_code < 400
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Upload request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during upload: {e}")
        return False

def run_all_tests():
    """Run comprehensive backend API tests"""
    print("Starting comprehensive backend API testing...")
    print(f"Backend URL: {BASE_URL}")
    
    results = {}
    
    # Test 1: Critical - Image Upload
    print(f"\n{'#'*80}")
    print("PRIORITY 1: CRITICAL IMAGE UPLOAD TEST")
    print(f"{'#'*80}")
    
    upload_result = test_image_upload()
    results['image_upload'] = upload_result
    image_id = None
    if isinstance(upload_result, str):
        image_id = upload_result
        results['image_upload'] = True
    
    # Test 2: Basic endpoints
    print(f"\n{'#'*80}")
    print("PRIORITY 2: BASIC ENDPOINT TESTS")
    print(f"{'#'*80}")
    
    # Test GET /api/graph
    results['get_graph'] = test_endpoint('GET', '/graph')
    
    # Test GET /api/categories
    results['get_categories'] = test_endpoint('GET', '/categories')
    
    # Test GET /api/connection-types
    results['get_connection_types'] = test_endpoint('GET', '/connection-types')
    
    # Test GET /api/stats
    results['get_stats'] = test_endpoint('GET', '/stats')
    
    # Test POST /api/build-index
    results['build_index'] = test_endpoint('POST', '/build-index')
    
    # Test GET /api/search
    results['search'] = test_endpoint('GET', '/search?query=test')
    
    # Test image-specific endpoints if we have an image_id
    if image_id:
        print(f"\n{'#'*80}")
        print(f"PRIORITY 3: IMAGE-SPECIFIC TESTS (using image_id: {image_id})")
        print(f"{'#'*80}")
        
        # Test GET /api/node/{image_id}
        results['get_node'] = test_endpoint('GET', f'/node/{image_id}')
        
        # Test GET /api/thumbnail/{image_id}
        results['get_thumbnail'] = test_endpoint('GET', f'/thumbnail/{image_id}')
    else:
        print("\n⚠️  Skipping image-specific tests - no valid image_id from upload")
        results['get_node'] = 'SKIPPED'
        results['get_thumbnail'] = 'SKIPPED'
    
    # Summary
    print(f"\n{'='*80}")
    print("TEST RESULTS SUMMARY")
    print(f"{'='*80}")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for test_name, result in results.items():
        if result == 'SKIPPED':
            print(f"⏭️  {test_name}: SKIPPED")
            skipped += 1
        elif result:
            print(f"✅ {test_name}: PASSED")
            passed += 1
        else:
            print(f"❌ {test_name}: FAILED")
            failed += 1
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        print(f"\n🚨 CRITICAL ISSUES FOUND: {failed} tests failed")
        if not results.get('image_upload', False):
            print("🚨 IMAGE UPLOAD FAILED - This is the main issue reported by user")
    else:
        print(f"\n✅ All tests passed successfully!")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()