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
        f"[Vote Summary] YES={result['yes']} | NO={result['no']} | ABSTAIN={result['abstain']} | Net={result['net']}"
    )
    log_tagged_memory(summary, topic="swarm", trust="neutral")

    if result["net"] >= 2 and result["yes"] > result["no"]:
        # Try to extract the most recent topic voted on
        for entry in reversed(logs):
            if entry.get("topic") == "decision" and "Proposing decision:" in entry.get("content", ""):
                try:
                    _, proposal = entry["content"].split("Proposing decision:", 1)
                    action_topic = proposal.strip()
                    log_tagged_memory(f"Action approved: {action_topic}", topic="swarm", trust="high")
                    break
                except:
                    continue