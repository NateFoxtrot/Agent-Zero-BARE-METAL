#!/bin/bash

# Define Paths
SOURCE_DIR="$HOME/agent-zero"
DEST_DIR="$HOME/Agent-Zero-Bare-Metal-PUBLIC"

echo "🚀 Preparing Public Release (SearXNG Edition)..."
echo "Source: $SOURCE_DIR"
echo "Destination: $DEST_DIR"

# 1. Create Destination and Clone Files
rsync -av --progress "$SOURCE_DIR/" "$DEST_DIR/" \
    --exclude 'logs' \
    --exclude 'tmp' \
    --exclude 'memory' \
    --exclude 'knowledge' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude '.env' \
    --exclude 'agent-zero-bare.sh' \
    --exclude 'venv' \
    --exclude 'node_modules' \
    --exclude 'workspace'

mkdir -p "$DEST_DIR/logs"
mkdir -p "$DEST_DIR/tmp"
mkdir -p "$DEST_DIR/memory/default"
mkdir -p "$DEST_DIR/knowledge/default"
mkdir -p "$DEST_DIR/workspace"

# 2. Update Requirements (NO DuckDuckGo)
echo "📦 Updating requirements.txt..."
cat << 'EOF' >> "$DEST_DIR/requirements.txt"
google-cloud-aiplatform
EOF

# 3. Create Generic start.sh
echo "📜 Creating generic start.sh..."
cat << 'EOF' > "$DEST_DIR/start.sh"
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
EOF
chmod +x "$DEST_DIR/start.sh"

# 4. Create Settings Template (Vertex Global Fix)
echo "⚙️ Creating settings.template.json..."
cat << 'EOF' > "$DEST_DIR/settings.template.json"
{
    "chat_model_provider": "google",
    "chat_model_name": "gemini-3-pro-preview",
    "chat_model_kwargs": {
        "temperature": "1.0",
        "custom_llm_provider": "vertex_ai",
        "vertex_location": "global",
        "vertex_project": ""
    },
    "util_model_provider": "vertex_ai",
    "util_model_name": "gemini-2.0-flash-exp",
    "util_model_kwargs": {
        "temperature": "0",
        "custom_llm_provider": "vertex_ai",
        "vertex_location": "global",
        "vertex_project": ""
    },
    "browser_model_provider": "vertex_ai",
    "browser_model_name": "gemini-2.0-flash-exp",
    "browser_model_kwargs": {
        "temperature": "0",
        "custom_llm_provider": "vertex_ai",
        "vertex_location": "global",
        "vertex_project": ""
    },
    "google_vertex_project": "",
    "google_vertex_location": "global",
    "google_json_key_path": "",
    "shell_interface": "local",
    "mcp_server_enabled": false,
    "sentinel_enabled": true
}
EOF

# 5. Create .env.example
echo "🔐 Creating .env.example..."
cat << 'EOF' > "$DEST_DIR/.env.example"
GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account-key.json"
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
PERPLEXITY_API_KEY=""
EOF

# 6. Apply Code Refactors

# A. Playwright Helper
cat << 'EOF' > "$DEST_DIR/python/helpers/playwright.py"
import os, glob, subprocess, sys
from pathlib import Path
from python.helpers import files, print_style

def get_playwright_binary():
    home = Path.home()
    system_cache = home / ".cache" / "ms-playwright"
    patterns = [
        "chromium-*/chrome-linux/chrome",
        "chromium_headless_shell-*/chrome-linux/headless_shell",
        "chromium-*/chrome-linux/chrome.exe",
        "chromium_headless_shell-*/chrome-linux/headless_shell.exe"
    ]
    for pattern in patterns:
        matches = list(system_cache.glob(pattern))
        if matches:
            matches.sort(key=lambda p: str(p), reverse=True)
            return str(matches[0])
            
    pw_cache = Path(files.get_abs_path("tmp/playwright"))
    for pattern in ["chromium_headless_shell-*/chrome-*/headless_shell", "chromium_headless_shell-*/chrome-*/headless_shell.exe"]:
        matches = list(pw_cache.glob(pattern))
        if matches: return str(matches[0])
    return None

def ensure_playwright_binary():
    bin = get_playwright_binary()
    if bin: return bin
    env = os.environ.copy()
    subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"], env=env)
    bin = get_playwright_binary()
    if bin: return bin
    raise Exception("Playwright binary not found.")
EOF

# B. Search & Helpers (Copying the fixed versions from Source)
cp "$SOURCE_DIR/python/tools/search_engine.py" "$DEST_DIR/python/tools/search_engine.py"
cp "$SOURCE_DIR/python/helpers/searxng.py" "$DEST_DIR/python/helpers/searxng.py"

# C. Patch Browser Agent imports
sed -i 's/from python.helpers.playwright import ensure_playwright_binary/from python.helpers.playwright import ensure_playwright_binary, get_playwright_binary/' "$DEST_DIR/python/tools/browser_agent.py"

# 7. Create README
echo "📖 Creating README.md..."
cat << 'EOF' > "$DEST_DIR/README.md"
# Agent Zero (Bare Metal Edition)

A fully autonomous, multi-modal AI agent framework refactored for local ("bare metal") execution.

## Features
- **Bare Metal Native**: Runs directly in a Conda environment.
- **Vertex AI Global**: Pre-configured for Gemini 2.0/3.0 Preview models.
- **Standard Search**: Supports standard SearXNG (via Docker) and Perplexity.
- **Local Browser**: Uses system Playwright binaries.

## Installation
1. `conda create -n agent-zero-local python=3.11 && conda activate agent-zero-local`
2. `pip install -r requirements.txt && playwright install chromium`
3. Copy `.env.example` to `.env` and add your keys.
4. Run `./start.sh`
EOF

echo "✅ Release prepared at: $DEST_DIR"
