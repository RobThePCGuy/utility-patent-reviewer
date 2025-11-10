#!/bin/bash
# GPU PyTorch Manual Reinstall Script
# NOTE: install.py automatically installs PyTorch with GPU support
# Only use this script if you need to manually reinstall PyTorch with CUDA
# (e.g., after accidentally installing CPU version)

echo "Installing PyTorch with CUDA 12.8 support..."
venv/bin/pip uninstall -y torch torchvision torchaudio
venv/bin/pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128

echo ""
echo "Verifying GPU detection..."
venv/bin/python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo ""
echo "Done! GPU support installed."
