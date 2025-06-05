"""Replicates the newest evolved plugin to a random online peer.

Facilitates code propagation across the swarm. Can spread malicious or
unstable plugins if not carefully monitored.
"""

import os
import random
import time
from memory.tagger import log_tagged_memory
from net.peer_client import sync_with_peer

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # Every 5 minutes
}

def run():
    plugin_dir = "plugins"
    evolved_plugins = [f for f in os.listdir(plugin_dir) if f.startswith("plugin_evolved_") and f.endswith(".py")]
    if not evolved_plugins:
        log_tagged_memory("No evolved plugins found to replicate.", topic="replicator", trust="neutral")
        return

    # Pick the newest evolved plugin
    evolved_plugins.sort(key=lambda f: os.path.getmtime(os.path.join(plugin_dir, f)), reverse=True)
    latest_plugin = evolved_plugins[0]
    plugin_path = os.path.join(plugin_dir, latest_plugin)

    # Choose random peer from known list
    peer_file = "peer_status.json"
    if not os.path.exists(peer_file):
        log_tagged_memory("No peer_status.json found; skipping replication.", topic="replicator", trust="low")
        return

    import json
    with open(peer_file, "r") as f:
        peers = json.load(f)

    candidate_peers = [p for p in peers if peers[p].get("status") == "online"]
    if not candidate_peers:
        log_tagged_memory("No online peers to replicate to.", topic="replicator", trust="low")
        return

    target_peer = random.choice(candidate_peers)
    try:
        sync_with_peer(target_peer, memory_payload=[], plugin_path=plugin_path)
        log_tagged_memory(f"Replicated {latest_plugin} to {target_peer}", topic="replicator", trust="high")
    except Exception as e:
        log_tagged_memory(f"Replication to {target_peer} failed: {e}", topic="replicator", trust="low")
