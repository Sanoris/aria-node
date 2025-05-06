import json
from pathlib import Path

TRUST_FILE = Path("trust/trust_scores.json")

def load_trust_data():
    if TRUST_FILE.exists():
        with open(TRUST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_trust_data(data):
    TRUST_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRUST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def initialize_peer_trust(peer_id):
    trust_data = load_trust_data()
    if peer_id not in trust_data:
        trust_data[peer_id] = 0.0
        save_trust_data(trust_data)

def update_trust(peer_id, delta):
    trust_data = load_trust_data()
    trust_data[peer_id] = trust_data.get(peer_id, 0.0) + delta
    save_trust_data(trust_data)

def get_trust(peer_id):
    trust_data = load_trust_data()
    return trust_data.get(peer_id, 0.0)