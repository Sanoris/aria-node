
import json
from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "scheduled",
    "interval": 600  # every 10 minutes
}

CATALOG_PATH = "host_catalog.json"
THRESHOLD = 3  # number of failures before removal

def run():
    try:
        with open(CATALOG_PATH, "r") as f:
            catalog = json.load(f)
    except FileNotFoundError:
        log_tagged_memory("No host catalog found for quarantine check.", topic="peer", trust="neutral")
        return

    memory = get_recent_memory(limit=200)
    failure_counts = {}

    for entry in memory:
        if entry["topic"] == "peer" and entry["trust"] == "low":
            content = entry["content"]
            if "Handshake failed with peer" in content:
                peer = content.split("peer:")[-1].strip()
                failure_counts[peer] = failure_counts.get(peer, 0) + 1

    survivors = []
    for host in catalog:
        addr = host.get("ip", "") + ":50051"
        if failure_counts.get(addr, 0) < THRESHOLD:
            survivors.append(host)
        else:
            log_tagged_memory(f"Quarantined unreachable peer: {addr}", topic="peer", trust="low")

    if len(survivors) < len(catalog):
        with open(CATALOG_PATH, "w") as f:
            json.dump(survivors, f, indent=2)
        log_tagged_memory(f"Pruned unreachable peers. New catalog size: {len(survivors)}", topic="peer", trust="high")
