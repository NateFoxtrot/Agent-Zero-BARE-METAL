import psutil
import time
import os
import subprocess
import requests
import json
import glob
import sys

# --- CONSTANTS ---
OLLAMA_URL = "http://localhost:11434/api/chat"
AGENT_DIR = os.path.expanduser("~/agent-zero")
SETTINGS_FILE = os.path.join(AGENT_DIR, "tmp/settings.json")

# Default safety limits (overridden by UI)
CPU_TEMP_LIMIT = 88
CPU_USAGE_LIMIT = 98
SUSTAINED_LOAD_TIME = 30

print(f"👁️  Sentinel Watchdog Initializing...")

def get_settings():
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        if not temps: return 0
        for name in ['coretemp', 'k10temp', 'zenpower', 'cpu_thermal', 'package_id_0']:
            if name in temps:
                return max(entry.current for entry in temps[name])
        return 0
    except:
        return 0

def kill_process(pid, name, reason):
    try:
        p = psutil.Process(pid)
        p.terminate() 
        time.sleep(0.5)
        if p.is_running():
            p.kill() 
        
        msg = f"⚡ [SENTINEL] Killed {name} ({pid}). Reason: {reason}"
        print(msg)
        subprocess.run(['notify-send', '-u', 'critical', 'Agent Sentinel', msg])
    except:
        pass

def get_recent_logs():
    try:
        log_files = glob.glob(os.path.join(AGENT_DIR, "logs", "*.html"))
        if not log_files: return ""
        latest_log = max(log_files, key=os.path.getctime)
        with open(latest_log, 'r', errors='ignore') as f:
            return "".join(f.readlines()[-20:])
    except:
        return ""

def consult_ai(model_name, logs, proc_list):
    prompt = f"""
    You are a System Supervisor. Analyze this Agent status.
    RUNNING PROCESSES: {proc_list}
    RECENT AGENT LOGS: {logs}
    OUTPUT JSON ONLY: {{"action": "none" | "kill_bash", "reason": "brief explanation"}}
    """
    try:
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "format": "json",
            "stream": False
        }
        res = requests.post(OLLAMA_URL, json=payload, timeout=15)
        return json.loads(res.json()['message']['content'])
    except:
        return {"action": "none"}

# --- MONITOR LOOP ---
high_load_start = None
last_ai_check = 0

print("✅ Sentinel Active.")

while True:
    try:
        # 1. THROTTLE (Crucial Fix)
        time.sleep(1) 

        # 2. LOAD SETTINGS
        settings = get_settings()
        enabled = settings.get("sentinel_enabled", True)
        model_name = settings.get("sentinel_model", "deepseek-r1:14b")
        
        if not enabled:
            continue

        # 3. HARDWARE REFLEX
        cpu_pct = psutil.cpu_percent(interval=None) # Non-blocking since we sleep manually
        temp = get_cpu_temp()
        
        if temp > CPU_TEMP_LIMIT:
            print(f"🔥 CRITICAL TEMP: {temp}°C")
            procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                         key=lambda p: p.info['cpu_percent'], reverse=True)
            if procs:
                top = procs[0]
                if top.info['name'] in ['bash', 'python', 'python3', 'node', 'chrome', 'ollama_runner']:
                    kill_process(top.info['pid'], top.info['name'], f"Thermal Critical ({temp}C)")

        if cpu_pct > CPU_USAGE_LIMIT:
            if high_load_start is None: high_load_start = time.time()
            duration = time.time() - high_load_start
            
            if duration > SUSTAINED_LOAD_TIME:
                print(f"⚠️  Sustained High Load ({int(duration)}s). Scanning...")
                procs = sorted(psutil.process_iter(['pid', 'name', 'cpu_percent']), 
                             key=lambda p: p.info['cpu_percent'], reverse=True)
                if procs and procs[0].info['name'] in ['bash', 'sh', 'python3']:
                     kill_process(procs[0].info['pid'], procs[0].info['name'], "Tight Loop Detected")
                     high_load_start = None
        else:
            high_load_start = None

        # 4. COGNITIVE CHECK (Every 30s)
        if time.time() - last_ai_check > 30:
            last_ai_check = time.time()
            
            shells = [p.info for p in psutil.process_iter(['pid', 'name', 'create_time']) 
                     if p.info['name'] in ['bash', 'python3'] and (time.time() - p.info['create_time'] > 60)]
            
            # Only bother the AI if we have >5 shells open for more than a minute
            if len(shells) > 5: 
                print(f"🔎 Analyzing {len(shells)} active shells...")
                logs = get_recent_logs()
                decision = consult_ai(model_name, logs, str(shells))
                if decision.get('action') == 'kill_bash':
                    print(f"🤖 AI INTERVENTION: {decision.get('reason')}")
                    oldest = min(shells, key=lambda x: x['create_time'])
                    kill_process(oldest['pid'], oldest['name'], "AI Supervisor Cleanup")

    except KeyboardInterrupt:
        break
    except Exception as e:
        pass 
