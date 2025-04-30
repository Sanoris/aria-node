import json
import time
from pathlib import Path
import datetime

MEMORY_FILE = "memory/log.txt"

def log_tagged_memory(content, topic="misc", trust="neutral"):
    entry = {
        "timestamp": time.time(),
        "topic": topic,
        "trust": trust,
        "content": content
    }
    Path("memory").mkdir(exist_ok=True)
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def tag_memory(message, topic="general", trust="neutral"):
    timestamp = datetime.utcnow().isoformat()
    tags = f"[topic:{topic}][trust:{trust}]"
    return f"{timestamp} {tags} {message}"

'''def log_tagged_memory(message, topic="general", trust="neutral"):
    log_file = Path("memory/log.txt")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch(exist_ok=True)

    line = tag_memory(message, topic, trust)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line'''

def get_recent_memory(limit=20, topic=None):
    try:
        with open("memory/log.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        entries = [json.loads(line.strip()) for line in lines]
        if topic:
            entries = [e for e in entries if e.get("topic") == topic]
        return entries
    except Exception:
        return []