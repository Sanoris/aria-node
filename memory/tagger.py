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

def get_recent_memory(limit=20):
    try:
        with open("memory/log.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        entries = []
        for line in lines:
            timestamp = line[:26]
            msg = line[27:].strip()
            topic = "unknown"
            if "[topic:" in msg:
                topic = msg.split("[topic:")[1].split("]")[0]
                msg = msg.split("]")[-1].strip()
            entries.append({"timestamp": timestamp, "msg": msg, "topic": topic})
        return entries
    except Exception:
        return []