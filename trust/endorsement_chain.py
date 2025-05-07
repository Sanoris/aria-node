import json
import time
from pathlib import Path

ENDORSEMENTS_PATH = Path("trust/endorsement_chain.json")


def load_endorsements():
    if ENDORSEMENTS_PATH.exists():
        with open(ENDORSEMENTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_endorsements(data):
    with open(ENDORSEMENTS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def endorse_peer(target_peer_id, endorser_id, score_given, reason):
    data = load_endorsements()
    now = time.time()

    if target_peer_id not in data:
        data[target_peer_id] = {
            "trust_score": 0.0,
            "endorsed_by": []
        }

    # Update trust score as a weighted average for now (simplistic)
    past = data[target_peer_id]["endorsed_by"]
    total = sum(entry["score_given"] for entry in past) + score_given
    count = len(past) + 1
    new_score = round(total / count, 4)
    data[target_peer_id]["trust_score"] = new_score

    data[target_peer_id]["endorsed_by"].append({
        "endorser_id": endorser_id,
        "score_given": score_given,
        "timestamp": now,
        "reason": reason
    })

    save_endorsements(data)
    print(f"[🤝] {endorser_id} endorsed {target_peer_id} with score {score_given:.2f} ({reason})")
