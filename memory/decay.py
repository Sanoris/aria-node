import time
import os

DECAY_RULES = {
    "chat": {"ttl": 60 * 60 * 24},          # 1 day
    "sync": {"ttl": 60 * 60 * 24 * 7},      # 1 week
    "recon": {"ttl": 60 * 60 * 24 * 3},     # 3 days
    "admin": {"ttl": 60 * 60 * 24 * 30},    # 1 month
}

def extract_timestamp(line):
    try:
        return time.mktime(time.strptime(line.split(" ")[0], "%Y-%m-%dT%H:%M:%S"))
    except:
        return 0

def extract_tag(line, tag):
    start = line.find(f"[{tag}:")
    if start == -1:
        return None
    end = line.find("]", start)
    return line[start + len(tag) + 2:end]

def decay_memory(filepath="memory/log.txt"):
    now = time.time()
    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    kept = []
    for line in lines:
        ts = extract_timestamp(line)
        topic = extract_tag(line, "topic")
        if topic in DECAY_RULES:
            ttl = DECAY_RULES[topic]["ttl"]
            if now - ts <= ttl:
                kept.append(line)
        else:
            kept.append(line)  # unknown topic = preserve

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(kept)
    print(f"[🧠] Memory decay complete. {len(kept)} entries preserved.")

if __name__ == "__main__":
    decay_memory()
