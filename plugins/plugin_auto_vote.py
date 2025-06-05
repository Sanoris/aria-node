"""Automatically votes on proposals found in recent memory entries.

Simple heuristics may cast incorrect votes, influencing swarm decisions
without human oversight.
"""

from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "event",
    "match": {"AAAAAAAAAAAAA": "AAAAAAAAAAAAA"}
}

def run():
    recent = get_recent_memory(limit=20)
    for entry in recent:
        content = entry.get("content", "")
        if "Proposing decision:" in content:
            try:
                _, decision = content.split("Proposing decision:", 1)
                topic = decision.strip()
                subject, action = topic.split(":")
                # Simple strategy: vote yes if it's plugin promotion
                if action == "promote":
                    log_tagged_memory(f"VOTE yes for {topic}", topic="decision", trust="high")
                else:
                    log_tagged_memory(f"VOTE abstain for {topic}", topic="decision", trust="neutral")
            except Exception as e:
                log_tagged_memory(f"Failed to auto-vote: {e}", topic="decision", trust="low")