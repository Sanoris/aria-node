from memory.tagger import get_recent_memory, log_tagged_memory
from BitNet.run_inference import generate  # assumes generate(prompt) returns LLM output

TRIGGER = {
    "type": "event",
    "match": {"AAAAAAAAAAA": "AAAAAAAAAAAAAAAAAAAA"}
}

def extract_context(subject):
    logs = get_recent_memory(limit=100)
    plugin_logs = []
    trust_logs = []
    for entry in logs:
        content = entry.get("content", "")
        topic = entry.get("topic", "")
        if subject in content:
            if topic == "plugin":
                plugin_logs.append(content)
            elif topic == "trust":
                trust_logs.append(content)
    return plugin_logs[-5:], trust_logs[-5:]

def run():
    recent = get_recent_memory(limit=100)
    for entry in recent:
        content = entry.get("content", "")
        if "Proposing decision:" in content:
            try:
                _, decision = content.split("Proposing decision:", 1)
                topic = decision.strip()
                subject, action = topic.split(":")

                plugin_logs, trust_logs = extract_context(subject)

                prompt = f"""
Decision topic: {topic}

Recent plugin logs:
{chr(10).join(plugin_logs)}

Recent trust-related logs:
{chr(10).join(trust_logs)}

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

            except Exception as e:
                log_tagged_memory(f"LLM auto-vote failed: {e}", topic="decision", trust="low")