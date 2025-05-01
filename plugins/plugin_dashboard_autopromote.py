import time
import socket
import subprocess
import os
from memory.tagger import get_recent_memory, log_tagged_memory
from net.dashboard_server import serve_grpc

TRIGGER = {
    "type": "event",
    "match": {
        "event": "dashboard_discovery",
        "status": "not_found",
        "knockKnock": "urdead"
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

        # Start Nginx if not already running
        try:
            subprocess.run(["nginx", "-t"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["nginx"], check=False)
            print("[🌐] Nginx started.")
        except Exception as e:
            log_tagged_memory(f"[autopromote] Failed to start nginx: {e}", topic="dashboard", trust="low")

        # Start Uvicorn dashboard server as background process
        try:
            subprocess.Popen([
                "uvicorn", "aria_dashboard.main:app",
                "--host", "0.0.0.0", "--port", "8000"
            ])
            print("[🚀] Uvicorn dashboard server launched.")
            #serve_grpc(port=8000)  # Start gRPC server in the same process
        except Exception as e:
            log_tagged_memory(f"[autopromote] Failed to start uvicorn: {e}", topic="dashboard", trust="low")

    except Exception as e:
        log_tagged_memory({
            "event": "dashboard_autopromote_failure",
            "error": str(e),
            "timestamp": time.time()
        }, topic="dashboard", trust="low")