#!/usr/bin/env python3
"""
Automatic GPU/CPU Detection and PyTorch Installation
Detects hardware and installs the correct PyTorch version automatically
"""

import platform
import subprocess
import sys


def run_command(cmd, description="Running command"):
    """Run a command and return success status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_nvidia_gpu():
    """Check if NVIDIA GPU is available"""
    try:
        if platform.system() == "Windows":
            result = subprocess.run(
                "nvidia-smi", shell=True, capture_output=True, text=True, timeout=5
            )
        else:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except Exception:
        return False


def get_compute_capability():
    """Detect GPU compute capability from nvidia-smi"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            compute_cap = result.stdout.strip()
            if compute_cap:
                return float(compute_cap)
    except Exception:
        pass
    return None


def install_pytorch(gpu_available=False, compute_cap=None):
    """Install appropriate PyTorch version"""

    if not gpu_available:
        print("\n" + "=" * 60)
        print("No NVIDIA GPU detected - Installing CPU version")
        print("=" * 60)
        cmd = f"{sys.executable} -m pip install torch torchvision"
        return run_command(cmd, "Installing PyTorch (CPU)")

    # RTX 5090/5080 (compute 12.0+) need CUDA 12.8, older GPUs use 12.8 too
    if compute_cap and compute_cap >= 10.0:
        cuda_pkg = "cu128"
        cuda_name = "12.8"
        print("\n" + "=" * 60)
        print(f"RTX 5090/5080 detected (Compute {compute_cap}) - Installing CUDA {cuda_name}")
        print("=" * 60)
    else:
        cuda_pkg = "cu128"  # Default to 12.8 for best compatibility
        cuda_name = "12.8"
        print("\n" + "=" * 60)
        print(f"NVIDIA GPU detected - Installing CUDA {cuda_name} version")
        print("=" * 60)

    # Uninstall any existing PyTorch first
    subprocess.run(
        f"{sys.executable} -m pip uninstall -y torch torchvision torchaudio",
        shell=True,
        capture_output=True,
    )

    cmd = f"{sys.executable} -m pip install torch torchvision --index-url https://download.pytorch.org/whl/{cuda_pkg}"
    return run_command(cmd, f"Installing PyTorch (CUDA {cuda_name})")


def verify_installation():
    """Verify PyTorch installation and GPU detection"""
    print("\n" + "=" * 60)
    print("Verifying installation...")
    print("=" * 60)

    try:
        import torch

        print(f"\n[OK] PyTorch version: {torch.__version__}")

        if torch.cuda.is_available():
            print("[OK] CUDA available: Yes")
            print(f"[OK] GPU: {torch.cuda.get_device_name(0)}")
            print(f"[OK] VRAM: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
            return True, "GPU"
        else:
            print("[OK] CUDA available: No (using CPU)")
            return True, "CPU"
    except Exception as e:
        print(f"\n[FAIL] Error: {e}")
        return False, None


def main():
    """Main auto-setup routine"""
    print("=" * 60)
    print("Utility Patent Reviewer - Automatic Setup")
    print("=" * 60)
    print("\nDetecting your system configuration...")

    # Detect OS
    os_name = platform.system()
    print(f"[OK] Operating System: {os_name}")

    # Detect GPU
    has_gpu = check_nvidia_gpu()
    compute_cap = None
    if has_gpu:
        compute_cap = get_compute_capability()
        if compute_cap:
            print(f"[OK] NVIDIA GPU detected (Compute Capability {compute_cap})")
        else:
            print("[OK] NVIDIA GPU detected")
    else:
        print("[OK] No NVIDIA GPU detected (will use CPU)")

    # Install PyTorch
    print("\n" + "=" * 60)
    print("Installing PyTorch with optimal settings...")
    print("=" * 60)

    success, output = install_pytorch(has_gpu, compute_cap)

    if not success:
        print("\n✗ Installation failed!")
        print(output)
        return 1

    # Verify
    success, device = verify_installation()

    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] Setup Complete!")
        print("=" * 60)
        if device == "GPU":
            print("\nYour system is configured to use GPU acceleration (5-10x faster)")
        else:
            print("\nYour system is configured to use CPU")
        print("\nNext steps:")
        print("  1. Run: patent-reviewer setup")
        print("  2. Run: patent-reviewer download-patents")
        return 0
    else:
        print("\n[FAIL] Verification failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
