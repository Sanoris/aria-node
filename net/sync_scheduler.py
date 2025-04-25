import threading
import time
import yaml
import json
import os
from .peer_client import sync_with_peer

CONFIG_PATH = "config.yaml"
STATUS_PATH = "peer_status.json"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def update_status(peer, success=True):
    status = {}
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, "r") as f:
            status = json.load(f)
    status.setdefault(peer, {"last_seen": None, "failures": 0})

    if success:
        status[peer]["last_seen"] = time.time()
        status[peer]["failures"] = 0
    else:
        status[peer]["failures"] += 1

    with open(STATUS_PATH, "w") as f:
        json.dump(status, f, indent=2)

def sync_loop(peers, interval):
    while True:
        for peer in peers:
            try:
                print(f"[>] Syncing with {peer}")
                sync_with_peer(peer)
                update_status(peer, success=True)
            except Exception as e:
                print(f"[!] Failed to sync with {peer}: {e}")
                update_status(peer, success=False)
        time.sleep(interval)

def run_scheduler():
    config = load_config()
    peers = config.get("peer_list", [])
    interval = config.get("sync_interval", 60)
    thread = threading.Thread(target=sync_loop, args=(peers, interval), daemon=True)
    thread.start()
    print("[+] Aria whisper sync scheduler running...")

if __name__ == "__main__":
    run_scheduler()
    while True:
        time.sleep(3600)
