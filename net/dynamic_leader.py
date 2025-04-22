import time
from net.swarm_manifest import read_manifest

def elect_leader():
    manifest = read_manifest()
    if not manifest:
        print("[⚠️] No peers in manifest.")
        return None
    sorted_peers = sorted(manifest.items(), key=lambda x: -x[1]["last_seen"])
    leader = sorted_peers[0]
    print(f"[👑] Selected leader: {leader[0]}")
    return leader[0]
