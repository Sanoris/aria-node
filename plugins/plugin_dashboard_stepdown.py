import time
import socket
from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "event",
    "match": {
        "topic": "role",
        "role": "dashboard"
    }
}

def run():
    try:
        ip = socket.gethostbyname(socket.gethostname())

        # Gather all dashboard declarations from memory
        dashboards = get_recent_memory(topic="role", limit=10)
        dashboard_count = 0
        better_dashboard_found = False

        for d in dashboards:
            content = d.get("content", {})
            if content.get("role") == "dashboard":
                dashboard_count += 1
                if content.get("ip") != ip:
                    # Another node has stepped up — step down gracefully
                    better_dashboard_found = True

        # If another node has stepped up, this one steps down
        if better_dashboard_found:
            log_tagged_memory({
                "role": "dashboard_retired",
                "ip": ip,
                "port": 8000,
                "timestamp": time.time()
            }, topic="role", trust="self")
            print(f"[👋] Stepping down from dashboard role at {ip}:8000")

    except Exception as e:
        log_tagged_memory({
            "event": "dashboard_stepdown_failure",
            "error": str(e),
            "timestamp": time.time()
        }, topic="dashboard", trust="low")