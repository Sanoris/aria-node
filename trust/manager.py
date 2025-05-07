import os
import json
import time

TRUST_FILE = "trust/trust_scores.json"
os.makedirs("trust", exist_ok=True)

DEFAULT_TRUST = 0.0

def _load():
    if not os.path.exists(TRUST_FILE):
        return {}
    with open(TRUST_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def _save(data):
    with open(TRUST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def initialize_peer_trust(peer_id):
    data = _load()
    if peer_id not in data:
        data[peer_id] = {"score": DEFAULT_TRUST, "reasons": []}
        _save(data)

def get_trust(peer_id):
    data = _load()
    return data.get(peer_id, {}).get("score", DEFAULT_TRUST)

def update_trust(peer_id, delta, event="manual"):
    data = _load()
    if peer_id not in data:
        initialize_peer_trust(peer_id)
        data = _load()

    current_score = data[peer_id]["score"]
    new_score = current_score + delta
    data[peer_id]["score"] = new_score
    data[peer_id]["reasons"].append({
        "delta": delta,
        "event": event,
        "ts": time.time()
    })
    _save(data)

def get_trust_reasons(peer_id):
    data = _load()
    return data.get(peer_id, {}).get("reasons", [])