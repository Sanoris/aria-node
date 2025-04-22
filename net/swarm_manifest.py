import json
import time

MANIFEST_PATH = "memory/swarm_manifest.json"

def update_manifest(node_id, role, skills, last_seen=None):
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except:
        data = {}

    last_seen = last_seen or time.time()
    data[node_id] = {
        "role": role,
        "skills": skills,
        "last_seen": last_seen
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"[🔍] Updated manifest for {node_id}")

def read_manifest():
    try:
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}
