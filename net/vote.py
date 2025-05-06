import json
from memory.tagger import log_tagged_memory
from swarm_vote import swarm_vote
from swarm_merge import merge_peer_logs
from trust.manager import get_trust

VOTE_THRESHOLD = 0.7  # total weighted approval threshold

def request_vote(subject, action):
    topic = f"{subject}:{action}"
    log_tagged_memory(f"Proposing decision: {topic}", topic="decision", trust="neutral")

    # Merge logs and count votes with trust
    entries = merge_peer_logs()
    weighted_total = 0.0
    vote_map = swarm_vote(entries)

    for peer_id, vote in vote_map.get(topic, {}).items():
        weight = get_trust(peer_id)
        if vote.lower() == "yes":
            weighted_total += weight
        elif vote.lower() == "no":
            weighted_total -= weight * 1.2  # penalize dissent slightly

    log_tagged_memory(f"Weighted vote score for {topic}: {weighted_total:.2f}", topic="decision", trust="neutral")
    return weighted_total >= VOTE_THRESHOLD