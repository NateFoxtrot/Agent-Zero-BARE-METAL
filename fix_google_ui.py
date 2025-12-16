import os
import sys

SETTINGS_PATH = os.path.expanduser("~/agent-zero/python/helpers/settings.py")

if not os.path.exists(SETTINGS_PATH):
    print("❌ Error: settings.py not found.")
    sys.exit(1)

with open(SETTINGS_PATH, "r") as f:
    content = f.read()

print("[-] Applying UI Enhancements to Google Configuration...")

# 1. Ensure 'icon' is in SettingsSection definition
if "icon: str" not in content and "class SettingsSection(TypedDict, total=False):" in content:
    content = content.replace("tab: str", "tab: str\n    icon: str")
    print("✅ Added icon support to Settings Structure")

# 2. Define the Rich HTML Header
google_html = 'google_desc = \"\"\"<div style="display: flex; align-items: center; gap: 15px;"><img src="https://www.gstatic.com/images/branding/product/1x/google_cloud_48dp.png" style="width: 48px; filter: drop-shadow(0 0 2px rgba(255,255,255,0.5));"><div><h4 style="margin:0; color: #669df6;">GOOGLE CLOUD / VERTEX AI</h4><p style="margin:5px 0;">Authentication & Credential Bridge</p></div></div>\"\"\"'

# 3. Replace the old simple description with the rich HTML
# We look for the google_section definition and replace the description
if "google_desc =" not in content:
    # Inject variable before the section definition
    content = content.replace("google_section: SettingsSection = {", google_html + "\n    google_section: SettingsSection = {")

# 4. Update the section dictionary to use the new description and icon
if "google_section: SettingsSection = {" in content:
    # We find the block and update it
    old_block_start = "google_section: SettingsSection = {"
    # We construct the new block content
    new_block = """google_section: SettingsSection = {
        "id": "google_config",
        "title": "Google Configuration",
        "description": google_desc,
        "fields": google_fields,
        "tab": "external",
        "icon": "cloud"
    }"""
    
    # We need a robust replace because the indentation might vary. 
    # Instead, we'll try to replace the known previous structure if it exists
    simple_desc = '"description": "Manage Google Cloud / Vertex AI authentication.",'
    if simple_desc in content:
        content = content.replace(simple_desc, '"description": google_desc,')
        print("✅ Updated Google Description to HTML")

    # Add icon if missing
    if '"icon": "cloud"' not in content and '"description": google_desc' in content:
        content = content.replace('"tab": "external"', '"tab": "external",\n        "icon": "cloud"')
        print("✅ Added Cloud Icon")

with open(SETTINGS_PATH, "w") as f:
    f.write(content)

print("🎉 Google UI Fixed.")
