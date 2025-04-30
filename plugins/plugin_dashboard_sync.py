import socket
from datetime import datetime
from memory.tagger import get_recent_memory, log_tagged_memory
from net.dashboard_sync import sync_to_dashboard, discover_dashboard_url

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # seconds
}

def run():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        memory_entries = get_recent_memory(limit=20)

        # Discover dashboard URL dynamically
        dashboard_url = discover_dashboard_url()
        if dashboard_url:
            sync_to_dashboard(ip, memory_entries)
            log_tagged_memory(f"Synced logs to {dashboard_url}", topic="dashboard", trust="high")
        else:
            log_tagged_memory("Dashboard URL not found", topic="dashboard", trust="neutral")
    except Exception as e:
        log_tagged_memory(f"Dashboard sync failed: {e}", topic="dashboard", trust="low")