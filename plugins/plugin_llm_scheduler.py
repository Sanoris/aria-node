import time
from memory.tagger import get_recent_memory, log_tagged_memory
from BitNet.run_inference import generate  # assumes generate(prompt) returns LLM output

TRIGGER = {
    "type": "scheduled",
    "interval": 30  # every 2 minutes
}

def run():
    logs = get_recent_memory(limit=100)
    proposals = {}

    for entry in logs:
        if entry.get("topic") == "decision":
            content = entry.get("content", "")
            if "Proposing decision:" in content:
                try:
                    _, decision = content.split("Proposing decision:", 1)
                    topic = decision.strip()
                    if topic not in proposals:
                        proposals[topic] = entry
                except:
                    continue

    for topic, entry in proposals.items():
        subject, action = topic.split(":")
        plugin_logs = []
        trust_logs = []

        for e in logs:
            content = e.get("content", "")
            if subject in content:
                if e.get("topic") == "plugin":
                    plugin_logs.append(content)
                elif e.get("topic") == "trust":
                    trust_logs.append(content)

        prompt = f"""
Decision topic: {topic}

Recent plugin logs:
{chr(10).join(plugin_logs[-5:])}

Recent trust-related logs:
{chr(10).join(trust_logs[-5:])}

Should we vote YES, NO, or ABSTAIN? Respond with a one-line justification.
"""

        result = generate(prompt)
        response = result.strip().lower()

        if "yes" in response:
            log_tagged_memory(f"VOTE yes for {topic} — {result}", topic="decision", trust="high")
        elif "no" in response:
            log_tagged_memory(f"VOTE no for {topic} — {result}", topic="decision", trust="low")
        else:
            log_tagged_memory(f"VOTE abstain for {topic} — {result}", topic="decision", trust="neutral")