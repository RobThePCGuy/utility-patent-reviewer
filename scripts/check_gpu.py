#!/usr/bin/env python3
"""Check GPU availability and PyTorch CUDA support"""

import subprocess
import sys

# Check PyTorch
try:
    import torch

    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(
        f"CUDA version (compiled): {torch.version.cuda if hasattr(torch.version, 'cuda') else 'N/A'}"
    )

    if torch.cuda.is_available():
        print("\nGPU Details:")
        print(f"  Device count: {torch.cuda.device_count()}")
        for i in range(torch.cuda.device_count()):
            print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
            props = torch.cuda.get_device_properties(i)
            print(f"    Memory: {props.total_memory / 1024**3:.1f} GB")
            print(f"    Compute Capability: {props.major}.{props.minor}")
    else:
        print("\nNo CUDA GPU detected by PyTorch")
        print("\nPossible reasons:")
        print("  1. PyTorch CPU version installed (most common)")
        print("  2. No NVIDIA GPU in system")
        print("  3. NVIDIA drivers not installed")
        print("  4. CUDA toolkit version mismatch")

except ImportError:
    print("PyTorch not installed")
    sys.exit(1)

# Check if running on Windows
if sys.platform == "win32":
    print("\nWindows detected. To install PyTorch with CUDA:")
    print("  Visit: https://pytorch.org/get-started/locally/")
    print("  Select: Windows, Pip, Python, CUDA 11.8 or 12.1")
    print("\nTypical command:")
    print(
        "  pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
    )
else:
    print("\nTo install PyTorch with CUDA support:")
    print("  Visit: https://pytorch.org/get-started/locally/")

# Check NVIDIA driver
print("\n" + "=" * 60)
print("Checking NVIDIA driver...")
print("=" * 60)

try:
    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("NVIDIA driver installed:")
        print(result.stdout)
    else:
        print("nvidia-smi command failed")
        print("NVIDIA drivers may not be installed")
except FileNotFoundError:
    print("nvidia-smi not found")
    print("NVIDIA drivers are NOT installed or not in PATH")
except Exception as e:
    print(f"Error checking NVIDIA driver: {e}")
