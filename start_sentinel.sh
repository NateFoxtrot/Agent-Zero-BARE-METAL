#!/bin/bash
# Title for the window manager
echo -ne "\033]0;👁️ Agent Overwatch\007"

echo "----------------------------------------------------------------"
echo "👁️  Starting Sentinel Watchdog..."
echo "----------------------------------------------------------------"

# 1. Ensure we are in the right directory
cd "$HOME/agent-zero"

# 2. Activate Conda Environment
CONDA_BASE=""
possible_conda_paths=("$HOME/miniconda3" "$HOME/anaconda3" "/opt/miniconda3" "/opt/anaconda3")
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
    # Fallback attempt
    if command -v conda &> /dev/null; then
        source $(conda info --base)/etc/profile.d/conda.sh 2>/dev/null
        conda activate agent-zero-local
    fi
fi

# 3. Run Supervisor
if [ -f "supervisor.py" ]; then
    echo "✅ Supervisor Active. Monitoring System..."
    python supervisor.py
else
    echo "❌ ERROR: supervisor.py missing!"
    read -p "Press Enter to close..."
    exit 1
fi

# 4. Clean Exit
echo ""
echo "🛑 Sentinel stopped. Closing terminal..."
sleep 2
exit
