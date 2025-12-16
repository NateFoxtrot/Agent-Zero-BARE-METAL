import json
import os

# Explicit path to the settings file
settings_path = os.path.expanduser("~/agent-zero/tmp/settings.json")

if os.path.exists(settings_path):
    print(f"[*] Loading settings from: {settings_path}")
    with open(settings_path, "r") as f:
        data = json.load(f)
    
    print("[-] Applying DeepSeek V3.2 Speciale Configuration...")

    # ---------------------------------------------------------
    # 1. CHAT MODEL: DeepSeek V3.2 Speciale (Reasoning)
    # ---------------------------------------------------------
    # Uses the specific endpoint required for this limited model
    data["chat_model_provider"] = "deepseek"
    data["chat_model_name"] = "deepseek-reasoner"
    data["chat_model_api_base"] = "https://api.deepseek.com/v3.2_speciale_expires_on_20251215"
    
    # ---------------------------------------------------------
    # 2. UTILITY MODEL: Google Gemini 2.0 Flash
    # ---------------------------------------------------------
    # Must use Google to handle JSON output reliably.
    # API Base MUST be empty to use default Google servers.
    data["util_model_provider"] = "google"
    data["util_model_name"] = "gemini-2.0-flash"
    data["util_model_api_base"] = "" 

    # ---------------------------------------------------------
    # 3. BROWSER MODEL: Google Gemini 2.0 Flash (Computer Use)
    # ---------------------------------------------------------
    data["browser_model_provider"] = "google"
    data["browser_model_name"] = "gemini-2.0-flash"
    data["browser_model_api_base"] = ""

    # ---------------------------------------------------------
    # 4. EMBEDDING MODEL: Google Gemini
    # ---------------------------------------------------------
    data["embed_model_provider"] = "google"
    data["embed_model_name"] = "gemini-embedding-001"
    data["embed_model_api_base"] = ""

    # ---------------------------------------------------------
    # 5. SAFETY & TYPES
    # ---------------------------------------------------------
    # Ensure ctx_length is an integer to prevent crashes
    data["chat_model_ctx_length"] = 100000
    data["util_model_ctx_length"] = 100000
    
    # Set conservative rate limit for Speciale
    data["chat_model_rl_requests"] = 50 

    with open(settings_path, "w") as f:
        json.dump(data, f, indent=4)
    
    print("✅ Success: Settings updated. Chat routed to Speciale endpoint.")
else:
    print(f"❌ Error: Settings file not found at {settings_path}")
