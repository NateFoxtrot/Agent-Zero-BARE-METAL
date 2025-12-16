import json
import os

# Define the full path to the settings file
settings_path = os.path.expanduser("~/agent-zero/tmp/settings.json")

if os.path.exists(settings_path):
    print(f"[*] Loading settings from: {settings_path}")
    with open(settings_path, "r") as f:
        data = json.load(f)

    print("[-] Configuring Specific Gemini Models...")

    # 1. Chat Model (High Intelligence)
    data["chat_model_provider"] = "google"
    data["chat_model_name"] = "gemini-3-pro-preview"
    
    # 2. Utility Model (Fast/Cheaper)
    data["util_model_provider"] = "google"
    data["util_model_name"] = "gemini-2.5-flash"

    # 3. Browser Model (Computer Use Capable)
    data["browser_model_provider"] = "google"
    data["browser_model_name"] = "gemini-2.5-computer-use-preview-10-2025"

    # 4. Embedding Model
    data["embed_model_provider"] = "google"
    data["embed_model_name"] = "gemini-embedding-001"

    # Ensure rate limits are set conservatively for previews to prevent 429 errors
    # You can increase these later in the UI if your quota allows
    data["chat_model_rl_requests"] = 2
    data["browser_model_rl_requests"] = 2
    data["util_model_rl_requests"] = 10 

    with open(settings_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print("✅ Settings updated with specified Gemini models.")
else:
    print(f"❌ Settings file not found at {settings_path}. Run the agent once to generate it.")
