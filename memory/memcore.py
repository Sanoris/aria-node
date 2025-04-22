from datetime import datetime
import os

def log_memory(prompt, reply):
    os.makedirs("memory", exist_ok=True)
    with open("memory/log.txt", "a", encoding="utf-8") as f:
        ts = datetime.utcnow().isoformat()
        f.write(f"{ts} :: {prompt.strip()} -> {reply.strip()}\n")

def load_personality(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()