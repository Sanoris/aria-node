"""Aggregates swarm votes from memory and logs a summary.

Purely informational but could be misleading if memory contains spam or
manipulated votes.
"""

from memory.tagger import get_recent_memory, log_tagged_memory
from net.swarm_vote import swarm_vote

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # every 5 minutes
}

def run():
    logs = get_recent_memory(limit=200)
    result = swarm_vote(logs, tag="decision")
    if not result:
        return

    summary = (
        f"Vote results: YES={result['yes']} | NO={result['no']} | ABSTAIN={result['abstain']}"
        f" | Net Score: {result['net']}"
    )

    log_tagged_memory(summary, topic="swarm", trust="neutral")