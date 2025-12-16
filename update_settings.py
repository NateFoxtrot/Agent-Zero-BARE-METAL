import json
import os

settings_path = os.path.expanduser("~/agent-zero/tmp/settings.json")

# Load existing settings
if os.path.exists(settings_path):
    with open(settings_path, 'r') as f:
        data = json.load(f)
else:
    data = {}

# FORCE correct model and SAFE rate limits for Gemini 3
data["chat_model_provider"] = "google"
data["chat_model_name"] = "gemini-exp-1206" # The technical name for Gemini 3 Experimental/Preview
data["chat_model_rl_requests"] = 2  # 2 requests per minute (Safe for Preview)
data["chat_model_rl_input"] = 0
data["chat_model_rl_output"] = 0

# Apply same to browser model to prevent parallel crashes
data["browser_model_provider"] = "google"
data["browser_model_name"] = "gemini-exp-1206"
data["browser_model_rl_requests"] = 2

# Save back
with open(settings_path, 'w') as f:
    json.dump(data, f, indent=4)

print("✅ Settings updated: Forced Gemini 3 Experimental with Rate Limits.")
