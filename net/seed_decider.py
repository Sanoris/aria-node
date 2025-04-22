import json
from net.heuristics import evaluate_host

CATALOG = "host_catalog.json"
MANIFEST = "memory/swarm_manifest.json"
PRIORITY_FILE = "priority_targets.json"

def load_hosts():
    try:
        with open(CATALOG, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[!] No host catalog found — skipping prioritization.")
        return []

def load_manifest():
    try:
        with open(MANIFEST, "r") as f:
            return json.load(f)
    except:
        return {}

def prioritize():
    hosts = load_hosts()
    manifest = load_manifest()
    ranked = []
    for host in hosts:
        score, reason = evaluate_host(host, manifest)
        ranked.append({
            "ip": host["ip"],
            "ports": host["ports"],
            "score": score,
            "reason": reason
        })

    ranked.sort(key=lambda x: -x["score"])
    with open(PRIORITY_FILE, "w") as f:
        json.dump(ranked, f, indent=2)
    print(f"[📊] Prioritized {len(ranked)} hosts.")
    return ranked

if __name__ == "__main__":
    prioritize()
