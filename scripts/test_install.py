#!/usr/bin/env python3
"""Verify installation - Run this after install.py completes"""
import sys

print("=" * 60)
print("Utility Patent Reviewer - Installation Verification")
print("=" * 60)

# Test imports
print("\n[1/4] Testing package imports...")
try:
    import faiss
    import mcp
    import numpy
    import sentence_transformers
    import torch
    import transformers

    # PyMuPDF check - just verify it's available
    try:
        import pymupdf  # noqa: F401
    except ImportError:
        print("⚠ PyMuPDF not installed (optional for PDF processing)")
    print("✓ All core packages imported successfully")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test versions
print("\n[2/4] Checking package versions...")
print(f"✓ PyTorch: {torch.__version__}")
print(f"✓ Transformers: {transformers.__version__}")
print(f"✓ Sentence Transformers: {sentence_transformers.__version__}")
print(f"✓ FAISS: {faiss.__version__}")
print(f"✓ NumPy: {numpy.__version__}")
# MCP version check with proper error handling
mcp_version = getattr(mcp, "__version__", "installed")
print(f"✓ MCP: {mcp_version}")

# Check version compatibility
versions_ok = True
if not torch.__version__.startswith("2.9"):
    print(f"⚠ PyTorch version {torch.__version__} may not be optimal")
    versions_ok = False

if not transformers.__version__.startswith("4.44"):
    print(f"⚠ Transformers version {transformers.__version__} may have compatibility issues")
    versions_ok = False

if not sentence_transformers.__version__.startswith("3.1"):
    print(
        f"⚠ Sentence Transformers version {sentence_transformers.__version__} may have compatibility issues"
    )
    versions_ok = False

if versions_ok:
    print("✓ Package versions are compatible")

# Test GPU
print("\n[3/4] Checking GPU availability...")
print(f"✓ CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    try:
        gpu_name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✓ GPU: {gpu_name}")
        print(f"✓ VRAM: {vram:.1f}GB")

        # Check if it's an RTX 5090/5080
        if "RTX 50" in gpu_name:
            if "+cu128" in torch.__version__ or "+cu130" in torch.__version__:
                print("✓ RTX 5090/5080 with correct CUDA version")
            else:
                print(f"⚠ RTX 5090/5080 detected but PyTorch is {torch.__version__}")
                print("  Expected: CUDA 12.8 or 13.0")
    except Exception as e:
        print(f"⚠ GPU detected but error getting details: {e}")
else:
    print("ℹ Running on CPU (no NVIDIA GPU detected)")

# Test basic functionality
print("\n[4/4] Testing basic functionality...")
try:
    # Test sentence transformer model loading (small model)
    print("  Loading embedding model (this may take a moment)...")
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    # Test embedding generation
    test_text = "This is a test patent claim."
    embedding = model.encode(test_text)

    print("✓ Embedding model loaded and working")
    print(f"✓ Generated {len(embedding)}-dimensional embedding")  # Test if using GPU
    if torch.cuda.is_available():
        device = next(model.parameters()).device
        if "cuda" in str(device):
            print("✓ Model is using GPU")
        else:
            print("ℹ Model is using CPU (this is normal if you haven't moved it to GPU)")

except Exception as e:
    print(f"✗ Functionality test failed: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("✓ INSTALLATION VERIFIED SUCCESSFULLY!")
print("=" * 60)

if torch.cuda.is_available():
    print("\n🚀 GPU acceleration is enabled - you'll get 5-10x faster performance!")
else:
    print("\n💻 Running on CPU - still works, just slower than GPU mode")

print("\nNext steps:")
print("  1. Download USPTO rules: patent-reviewer setup")
print("  2. (Optional) Download patents: patent-reviewer download-patents")
print("  3. Start using in Claude Code!")
print("\n" + "=" * 60)
