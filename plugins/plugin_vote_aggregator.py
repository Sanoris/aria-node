from memory.tagger import get_recent_memory, log_tagged_memory
from net.swarm_vote import swarm_vote

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # every 5 minutes
}

def run():
    logs = get_recent_memory(limit=200)
    result = swarm_vote(logs, tag="decision")

    summary = (
        f"Vote results: YES={result['yes']} | NO={result['no']} | ABSTAIN={result['abstain']}"
        f" | Net Score: {result['net']}"
    )

    log_tagged_memory(summary, topic="swarm", trust="neutral")