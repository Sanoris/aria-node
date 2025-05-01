import json
import os
import time
import subprocess
from pathlib import Path
from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "event",
    "match": {
        "topic": "role",
        "role": "dashboard"
    }
}

TEMPLATE_PATH = "./aria_proxy/dashboard_proxy.conf"
NGINX_OUTPUT_PATH = "/etc/nginx/conf.d/aria_dashboard.conf"
MEMORY_LOG_PATH = "./aria_dashboard/peer_logs.json"

def extract_latest_dashboard_ip():
    try:
        with open(MEMORY_LOG_PATH, "r") as f:
            logs = json.load(f)
        for node_id, entries in logs.items():
            for entry in reversed(entries):
                if entry.get("topic") == "role":
                    content = entry if "role" in entry else entry.get("content", {})
                    if content.get("role") == "dashboard":
                        return content.get("ip")
    except Exception as e:
        log_tagged_memory(f"[proxy_plugin] Failed to read memory: {e}", topic="dashboard", trust="low")
    return None

def run():
    ip = extract_latest_dashboard_ip()
    if not ip:
        log_tagged_memory("[proxy_plugin] No dashboard IP found", topic="dashboard", trust="low")
        return

    try:
        if not Path(TEMPLATE_PATH).exists():
            log_tagged_memory(f"[proxy_plugin] Missing template file: {TEMPLATE_PATH}", topic="dashboard", trust="low")
            return

        with open(TEMPLATE_PATH, "r") as f:
            template = f.read()

        new_conf = template.replace("DASHBOARD_IP", ip)

        Path(os.path.dirname(NGINX_OUTPUT_PATH)).mkdir(parents=True, exist_ok=True)

        with open(NGINX_OUTPUT_PATH, "w") as f:
            f.write(new_conf)

        subprocess.run(["nginx", "-s", "reload"], check=True)
        log_tagged_memory(f"[proxy_plugin] Nginx updated to route to {ip}:8000", topic="dashboard", trust="high")

    except Exception as e:
        log_tagged_memory(f"[proxy_plugin] Failed to update nginx: {e}", topic="dashboard", trust="low")