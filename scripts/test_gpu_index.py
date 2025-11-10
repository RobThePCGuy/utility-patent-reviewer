#!/usr/bin/env python3
"""Test GPU detection in the actual index classes"""

import sys
from pathlib import Path

import torch

# Add the project to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing GPU detection in patent-reviewer...\n")
print("=" * 60)

# Test 1: Import torch directly
print("\n1. Testing PyTorch CUDA:")

print(f"   PyTorch version: {torch.__version__}")
print(f"   CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   GPU: {torch.cuda.get_device_name(0)}")

# Test 2: Test the get_device function from server.py
print("\n2. Testing server.py get_device():")
try:
    from mcp_server.server import get_device

    device = get_device()
    print(f"   Device selected: {device}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 3: Test the get_device function from patent_index.py
print("\n3. Testing patent_index.py get_device():")
try:
    from mcp_server.patent_index import get_device

    device = get_device()
    print(f"   Device selected: {device}")
except Exception as e:
    print(f"   ERROR: {e}")

# Test 4: Try initializing SentenceTransformer with GPU
print("\n4. Testing SentenceTransformer GPU usage:")
try:
    from sentence_transformers import SentenceTransformer

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"   Attempting to load model on: {device}")

    # Try to load a tiny model for testing
    model = SentenceTransformer("all-MiniLM-L6-v2", device=device)
    print("   Model loaded successfully")
    print(f"   Model device: {model.device}")
except Exception as e:
    print(f"   ERROR: {e}")

print("\n" + "=" * 60)
print("Test complete")
