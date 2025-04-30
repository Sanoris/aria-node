import time
import socket
from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "event",
    "match": {
        "topic": "dashboard",
        "event": "dashboard_discovery",
        "status": "not_found"
    }
}

def run():
    try:
        # Check if any dashboards are already announced
        dashboards = get_recent_memory(topic="role", limit=10)
        for d in dashboards:
            if d.get("content", {}).get("role") == "dashboard":
                return  # A dashboard already exists

        # No dashboard found — this node will step up
        ip = socket.gethostbyname(socket.gethostname())
        log_tagged_memory({
            "role": "dashboard",
            "ip": ip,
            "port": 8000,
            "timestamp": time.time()
        }, topic="role", trust="self")
        print(f"[🌟] Promoting self to dashboard: http://{ip}:8000")

    except Exception as e:
        log_tagged_memory({
            "event": "dashboard_autopromote_failure",
            "error": str(e),
            "timestamp": time.time()
        }, topic="dashboard", trust="low")