#!/bin/bash
cd "$(dirname "$0")"

# --- ENVIRONMENT SETUP ---
CONDA_BASE=""
possible_conda_paths=("$HOME/miniconda3" "$HOME/anaconda3" "/opt/miniconda3" "/opt/anaconda3")
for path in "${possible_conda_paths[@]}"; do
    if [ -f "$path/etc/profile.d/conda.sh" ]; then
        CONDA_BASE="$path"
        break
    fi
done
[ -n "$CONDA_BASE" ] && source "$CONDA_BASE/etc/profile.d/conda.sh"

if conda env list | grep -q "agent-zero-local"; then
    conda activate agent-zero-local
fi

# --- LOAD .ENV ---
if [ -f .env ]; then
    set -a; source .env; set +a
elif [ -f .env.example ]; then
    echo "⚠️  .env not found. Copying .env.example..."
    cp .env.example .env
    echo "   Please edit .env and restart."
    exit 1
fi

# --- OLLAMA CHECK ---
if command -v ollama &> /dev/null && ! pgrep -x "ollama" > /dev/null; then
    ollama serve > /dev/null 2>&1 &
    sleep 5
fi

# --- SENTINEL ---
SENTINEL_SCRIPT="./start_sentinel.sh"
if command -v gnome-terminal &> /dev/null; then
    gnome-terminal --title="Agent Overwatch" --geometry=80x10 -- "$SENTINEL_SCRIPT"
elif command -v xterm &> /dev/null; then
    xterm -T "Sentinel Watchdog" -geometry 80x10 -e "$SENTINEL_SCRIPT" &
else
    bash "$SENTINEL_SCRIPT" > logs/supervisor.log 2>&1 &
fi

cleanup() {
    pkill -f "supervisor.py"
    docker stop searxng > /dev/null 2>&1
}
trap cleanup EXIT INT TERM

# --- SEARXNG STARTUP ---
# Attempts to start the standard SearXNG container on port 55510
if command -v docker &> /dev/null; then
    if ! docker ps --format '{{.Names}}' | grep -q "^searxng$"; then
        echo "[*] Starting SearXNG container..."
        docker start searxng > /dev/null 2>&1 || docker run -d --name searxng -p 55510:8080 -e SEARXNG_BASE_URL=http://localhost:55510/ searxng/searxng:latest > /dev/null 2>&1
    fi
else
    echo "⚠️  Docker not found. SearXNG tool will fail unless running on http://localhost:55510"
fi

# --- START UI ---
echo "Starting Agent Zero UI at http://localhost:50001"
python run_ui.py --port 50001 --host 0.0.0.0
