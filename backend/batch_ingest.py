#!/usr/bin/env python3
"""
Batch Image Ingestion Script

This script processes all images in a specified directory through the
image knowledge graph pipeline.

Usage:
    python batch_ingest.py <directory_path>
    
Example:
    python batch_ingest.py data/images
    python batch_ingest.py /path/to/your/photos
"""

import sys
import os
from pathlib import Path
from tqdm import tqdm
import uuid
import time

# Add parent directory to path to import pipeline
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pipeline import ImagePipeline
except ImportError:
    print("Error: Could not import pipeline module.")
    print("Make sure you're running this script from the backend directory.")
    sys.exit(1)

# Supported image formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

def find_images(directory: Path) -> list:
    """
    Find all image files in the specified directory (non-recursive)
    """
    if not directory.exists():
        print(f"Error: Directory '{directory}' does not exist.")
        return []
    
    if not directory.is_dir():
        print(f"Error: '{directory}' is not a directory.")
        return []
    
    images = []
    for file in directory.iterdir():
        if file.is_file() and file.suffix.lower() in IMAGE_EXTENSIONS:
            images.append(file)
    
    return sorted(images)

def process_images(directory_path: str):
    """
    Process all images in the specified directory
    """
    directory = Path(directory_path).resolve()
    
    print(f"\n{'='*60}")
    print(f"Batch Image Ingestion")
    print(f"{'='*60}")
    print(f"Directory: {directory}")
    print(f"Searching for images...\n")
    
    # Find all images
    images = find_images(directory)
    
    if not images:
        print("No image files found in the directory.")
        print(f"Supported formats: {', '.join(sorted(IMAGE_EXTENSIONS))}")
        return
    
    print(f"Found {len(images)} image(s) to process.\n")
    
    # Initialize pipeline
    print("Initializing image processing pipeline...")
    print("(First run may take a few minutes to download AI models)\n")
    
    try:
        pipeline = ImagePipeline(data_dir="data")
    except Exception as e:
        print(f"Error initializing pipeline: {e}")
        return
    
    # Process each image with progress bar
    results = {
        'success': 0,
        'duplicate': 0,
        'error': 0,
        'errors': []
    }
    
    print("Processing images...\n")
    
    for image_path in tqdm(images, desc="Progress", unit="image"):
        try:
            # Generate unique ID
            image_id = str(uuid.uuid4())[:16]
            
            # Process image
            result = pipeline.ingest_image(image_path, image_id)
            
            if result['status'] == 'success':
                results['success'] += 1
                tqdm.write(f"✓ {image_path.name} - Processed successfully (ID: {result['id']})")
            elif result['status'] == 'duplicate':
                results['duplicate'] += 1
                tqdm.write(f"⊘ {image_path.name} - Duplicate detected (ID: {result['id']})")
            else:
                results['error'] += 1
                results['errors'].append((image_path.name, "Unknown status"))
                tqdm.write(f"✗ {image_path.name} - Unknown status")
                
        except Exception as e:
            results['error'] += 1
            error_msg = str(e)
            results['errors'].append((image_path.name, error_msg))
            tqdm.write(f"✗ {image_path.name} - Error: {error_msg}")
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Processing Complete")
    print(f"{'='*60}")
    print(f"Total images found:     {len(images)}")
    print(f"Successfully processed: {results['success']}")
    print(f"Duplicates skipped:     {results['duplicate']}")
    print(f"Errors:                 {results['error']}")
    
    if results['errors']:
        print(f"\nErrors encountered:")
        for filename, error in results['errors']:
            print(f"  - {filename}: {error}")
    
    print(f"\n{'='*60}")
    print(f"Next Steps:")
    print(f"{'='*60}")
    print("1. View the graph in the web interface")
    print("2. Click 'Build Index' to enable similarity search")
    print("3. Use the search bar to find specific images")
    print("4. Click on nodes to view detailed information")
    print(f"{'='*60}\n")

def main():
    if len(sys.argv) != 2:
        print("Usage: python batch_ingest.py <directory_path>")
        print("\nExample:")
        print("  python batch_ingest.py data/images")
        print("  python batch_ingest.py /path/to/your/photos")
        sys.exit(1)
    
    directory_path = sys.argv[1]
    process_images(directory_path)

if __name__ == "__main__":
    main()
