"""GPU/CPU device detection utility"""

import os
import sys


def get_device() -> str:
    """Detect and return the best available device for computation.

    Environment variables:
        FORCE_CPU=1          - Force CPU usage even if GPU is available
        CUDA_VISIBLE_DEVICES - Control which GPUs are visible (PyTorch standard)

    Returns:
        'cuda' if GPU available and not disabled, 'cpu' otherwise
    """
    # Check if CPU is forced via environment variable
    force_cpu = os.environ.get("FORCE_CPU", "0").lower() in ("1", "true", "yes")

    if force_cpu:
        print("CPU forced via FORCE_CPU environment variable", file=sys.stderr)
        return "cpu"

    # Check for CUDA availability
    try:
        import torch

        if torch.cuda.is_available():
            device = "cuda"
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"GPU detected: {gpu_name} ({gpu_memory:.1f}GB VRAM)", file=sys.stderr)
            return device
        else:
            print("GPU not available, using CPU...", file=sys.stderr)
            return "cpu"
    except ImportError:
        print("PyTorch not available, using CPU...", file=sys.stderr)
        return "cpu"
