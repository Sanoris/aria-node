import requests
from datetime import datetime

DASHBOARD_URL = "http://127.0.0.1:8000/sync"

def sync_to_dashboard(ip: str, memory_entries: list):
    try:
        payload = {
            "ip": ip,
            "entries": [
                {
                    "timestamp": e.get("timestamp", datetime.now().isoformat()),
                    "msg": e.get("msg", "Unknown entry"),
                    "topic": e.get("topic", "misc")
                } for e in memory_entries
            ]
        }
        requests.post(DASHBOARD_URL, json=payload, timeout=3)
    except Exception as e:
        from memory.tagger import log_tagged_memory
        log_tagged_memory(f"Failed to sync to dashboard: {e}", topic="dashboard", trust="low")