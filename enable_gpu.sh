#!/bin/bash

# Ensure we are in the agent-zero directory
cd ~/agent-zero

echo "----------------------------------------------------------------"
echo "🔌 Enabling GPU Acceleration for Agent Zero"
echo "----------------------------------------------------------------"

# 1. Activate Conda Environment
# We reuse the logic from the bare metal runner to find conda
CONDA_BASE=""
possible_conda_paths=(
    "$HOME/miniconda3"
    "$HOME/anaconda3"
    "/opt/miniconda3"
    "/opt/anaconda3"
)
for path in "${possible_conda_paths[@]}"; do
    if [ -f "$path/etc/profile.d/conda.sh" ]; then
        CONDA_BASE="$path"
        break
    fi
done

if [ -n "$CONDA_BASE" ]; then
    source "$CONDA_BASE/etc/profile.d/conda.sh"
    conda activate agent-zero-local
else
    if [[ -n "$CONDA_PREFIX" ]]; then
         # Already inside an env or conda is in path
         echo "[*] Assuming Conda is in PATH..."
    else
         echo "❌ Conda not found. Cannot proceed."
         exit 1
    fi
fi

# 2. Uninstall CPU versions
echo "[*] Removing existing CPU-only PyTorch versions..."
pip uninstall -y torch torchvision torchaudio

# 3. Install CUDA versions (CUDA 12.1 is broadly compatible)
echo "[*] Installing PyTorch with CUDA 12.1 support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 4. Verification
echo "----------------------------------------------------------------"
echo "[*] Verifying GPU access..."
python -c "import torch; print(f'⚡ PyTorch Version: {torch.__version__}'); print(f'⚡ CUDA Available:  {torch.cuda.is_available()}'); print(f'⚡ GPU Device:      {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
echo "----------------------------------------------------------------"

if python -c "import torch; exit(0 if torch.cuda.is_available() else 1)"; then
    echo "✅ SUCCESS: Agent Zero is now powered by your GPU."
else
    echo "⚠️ WARNING: GPU not detected. You may need to install NVIDIA drivers."
fi
echo "----------------------------------------------------------------"

