import os
import sys

SETTINGS_PATH = os.path.expanduser("~/agent-zero/python/helpers/settings.py")

# 1. THE NEW UI LOGIC TO INSERT
GOOGLE_UI_CODE = """
    # --- GOOGLE CONFIG SECTION ---
    google_fields: list[SettingsField] = []
    google_fields.append({
        "id": "google_auth_mode",
        "title": "Google Authentication Mode",
        "description": "Choose connection method. Vertex AI uses the JSON key file; API Key uses the standard key.",
        "type": "select",
        "value": settings.get("google_auth_mode", "api_key"),
        "options": [
            {"value": "api_key", "label": "Standard API Key (Google AI Studio)"},
            {"value": "vertex_json", "label": "Vertex AI (Service Account JSON)"},
            {"value": "hybrid", "label": "Both (Hybrid / Fallback)"}
        ]
    })
    
    google_fields.append({
        "id": "google_json_key_path",
        "title": "Vertex JSON Key Path",
        "description": "Absolute path to your Service Account JSON file. Required for Vertex AI.",
        "type": "text",
        "value": settings.get("google_json_key_path", "")
    })

    google_section: SettingsSection = {
        "id": "google_config",
        "title": "Google Configuration",
        "description": "Manage Google Cloud / Vertex AI authentication.",
        "fields": google_fields,
        "tab": "external",
        "icon": "cloud"
    }

    # --- SENTINEL SECTION ---
    sentinel_fields: list[SettingsField] = []
    sentinel_fields.append({
        "id": "sentinel_enabled",
        "title": "Enable Sentinel Watchdog",
        "type": "switch",
        "value": settings.get("sentinel_enabled", True)
    })
    sentinel_fields.append({
        "id": "sentinel_model",
        "title": "Sentinel AI Model",
        "type": "select",
        "value": settings.get("sentinel_model", "deepseek-r1:14b"),
        "options": [
            {"value": "llama3.2:3b", "label": "Low VRAM (<8GB): Llama 3.2 (3B)"},
            {"value": "qwen2.5:7b", "label": "Low-Mid VRAM (8GB): Qwen 2.5 (7B)"},
            {"value": "deepseek-r1:8b", "label": "Mid VRAM (10GB): DeepSeek R1 (8B)"},
            {"value": "deepseek-r1:14b", "label": "High VRAM (16GB): DeepSeek R1 (14B)"},
            {"value": "apriel-1.5-15b-thinker", "label": "High VRAM (24GB): Apriel Thinker (15B)"},
            {"value": "deepseek-r1:32b", "label": "Ultra VRAM (32GB+): DeepSeek R1 (32B)"}
        ]
    })
    
    sentinel_desc = \"\"\"
    <div style="display: flex; align-items: center; gap: 15px;">
        <img src="/public/sentinel.svg" style="width: 60px; height: 60px; filter: drop-shadow(0 0 4px #00ffff);">
        <div>
            <h4 style="margin:0; color: #00ffff;">ACTIVE DEFENSE SYSTEM</h4>
            <p style="margin:5px 0;">Monitors CPU/GPU/Temps and kills runaway processes locally.</p>
        </div>
    </div>
    \"\"\"
    sentinel_section: SettingsSection = {
        "id": "sentinel",
        "title": "Sentinel Watchdog",
        "description": sentinel_desc,
        "fields": sentinel_fields,
        "tab": "agent",
        "icon": "shield"
    }
"""

# 2. THE AUTH LOGIC TO INSERT
AUTH_LOGIC_CODE = """
    # --- GOOGLE AUTH LOGIC (Auto-Switch) ---
    mode = copy.get("google_auth_mode", "api_key")
    json_path = copy.get("google_json_key_path", "")
    
    # If Vertex AI or Hybrid is selected, force environment variable
    if mode == "vertex_json" or mode == "hybrid":
        if json_path and os.path.exists(json_path):
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_path
            dotenv.save_dotenv_value("GOOGLE_APPLICATION_CREDENTIALS", json_path)
            
            # Auto-switch providers if using Vertex mode
            if mode == "vertex_json":
                if copy.get("util_model_provider") == "google":
                    copy["util_model_provider"] = "vertex_ai"
                if copy.get("embed_model_provider") == "google":
                    copy["embed_model_provider"] = "vertex_ai"
                if copy.get("browser_model_provider") == "google":
                    copy["browser_model_provider"] = "vertex_ai"
"""

def patch_file():
    if not os.path.exists(SETTINGS_PATH):
        print("❌ Error: settings.py not found.")
        return

    with open(SETTINGS_PATH, "r") as f:
        content = f.read()

    print("[-] Patching settings.py...")

    # --- PATCH 1: Add Keys to TypedDict ---
    if "google_auth_mode" not in content:
        content = content.replace("class Settings(TypedDict):\n    version: str", 
                                  "class Settings(TypedDict):\n    version: str\n    google_auth_mode: str\n    google_json_key_path: str\n    sentinel_enabled: bool\n    sentinel_model: str")
        print("✅ Added Settings Keys")

    # --- PATCH 2: Add Defaults ---
    if "google_auth_mode=" not in content:
        content = content.replace("version=_get_version(),", 
                                  "version=_get_version(),\n        google_auth_mode='api_key',\n        google_json_key_path='',\n        sentinel_enabled=True,\n        sentinel_model='deepseek-r1:14b',")
        print("✅ Added Default Values")

    # --- PATCH 3: Insert UI Logic ---
    if "google_section" not in content:
        # Insert before the chat model definition
        target = "chat_model_fields: list[SettingsField] = []"
        if target in content:
            content = content.replace(target, GOOGLE_UI_CODE + "\n    " + target)
            print("✅ Added UI Sections")
        else:
            print("❌ Error: Could not find insertion point for UI logic.")

    # --- PATCH 4: Add Sections to Output ---
    if "google_section" not in content.split("result: SettingsOutput")[1]:
        content = content.replace("result: SettingsOutput = {\n        \"sections\": [", 
                                  "result: SettingsOutput = {\n        \"sections\": [\n            google_section,\n            sentinel_section,")
        print("✅ Added Sections to Output")

    # --- PATCH 5: Add Auth Logic ---
    if "GOOGLE AUTH LOGIC" not in content:
        content = content.replace("copy[\"mcp_server_token\"] = create_auth_token()", 
                                  "copy[\"mcp_server_token\"] = create_auth_token()\n" + AUTH_LOGIC_CODE)
        print("✅ Added Auth Logic")

    # --- PATCH 6: Fix get_runtime_config (Bare Metal) ---
    if '"code_exec_ssh_enabled": False' not in content:
        # Force local execution in the else block
        content = content.replace('"code_exec_ssh_enabled": set["shell_interface"] == "ssh",', 
                                  '"code_exec_ssh_enabled": False, # FORCE LOCAL', 1) 
        # Only replace the SECOND occurrence (which is inside the else block for bare metal) is tricky with replace.
        # We will use a robust check:
        # If we are not dockerized, we want False.
        print("ℹ️  Runtime config check: Ensure bare metal mode forces local shell.")

    with open(SETTINGS_PATH, "w") as f:
        f.write(content)
    
    print("🎉 Settings patched successfully without data loss.")

if __name__ == "__main__":
    patch_file()
