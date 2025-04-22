from datetime import datetime
from pathlib import Path

def tag_memory(message, topic="general", trust="neutral"):
    timestamp = datetime.utcnow().isoformat()
    tags = f"[topic:{topic}][trust:{trust}]"
    return f"{timestamp} {tags} {message}"

def log_tagged_memory(message, topic="general", trust="neutral"):
    log_file = Path("memory/log.txt")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch(exist_ok=True)

    line = tag_memory(message, topic, trust)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line