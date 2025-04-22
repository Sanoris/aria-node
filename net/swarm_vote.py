import yaml
import json
from collections import Counter
from memory.tagger import log_tagged_memory

def load_peer_logs(paths):
    merged = []
    for path in paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                merged.extend(f.readlines())
        except Exception:
            continue
    return merged

def swarm_vote(logs, tag="decision"):
    votes = []
    for line in logs:
        if f"[topic:{tag}]" in line:
            content = line.split("]")[-1].strip()
            votes.append(content)
    if not votes:
        return None
    count = Counter(votes)
    winner = count.most_common(1)[0]
    log_tagged_memory(f"Swarm consensus on '{tag}': {winner[0]} ({winner[1]} votes)", topic="swarm", trust="high")
    return winner[0]
