import socket
from datetime import datetime
from memory.tagger import get_recent_memory, log_tagged_memory
from net.dashboard_sync import sync_to_dashboard

def run():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        memory_entries = get_recent_memory(limit=20)
        sync_to_dashboard(ip, memory_entries)
        log_tagged_memory("Synced logs to dashboard", topic="dashboard", trust="high")
    except Exception as e:
        log_tagged_memory(f"Dashboard sync failed: {e}", topic="dashboard", trust="low")