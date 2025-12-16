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
