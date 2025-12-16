import json
import os

settings_path = os.path.expanduser("~/agent-zero/tmp/settings.json")

if os.path.exists(settings_path):
    print(f"[*] Loading settings from: {settings_path}")
    with open(settings_path, "r") as f:
        data = json.load(f)

    print("[-] Applying Connection Stability Fixes...")

    # 1. Increase global timeout (give the model 10 minutes to think/respond)
    # 2. Enable aggressive retries (try 3 times if server disconnects)
    if "litellm_global_kwargs" not in data or not isinstance(data["litellm_global_kwargs"], dict):
        data["litellm_global_kwargs"] = {}
    
    # Set/Update values
    data["litellm_global_kwargs"]["timeout"] = 600  # 600 seconds = 10 minutes
    data["litellm_global_kwargs"]["num_retries"] = 3
    data["litellm_global_kwargs"]["request_timeout"] = 600

    with open(settings_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print("✅ Settings updated: Timeouts increased to 10 minutes + 3 Retries enabled.")
else:
    print(f"❌ Settings file not found at {settings_path}.")
