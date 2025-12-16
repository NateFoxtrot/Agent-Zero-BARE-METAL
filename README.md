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
