import yaml

CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def extract_tag(line, tag):
    start = line.find(f"[{tag}:")
    if start == -1:
        return None
    end = line.find("]", start)
    return line[start + len(tag) + 2:end]

def filter_memory_for_peer(peer_name):
    cfg = load_config()
    allowed_topics = cfg.get("peer_rules", {}).get(peer_name, {}).get("topics", [])
    allowed_trust = cfg.get("peer_rules", {}).get(peer_name, {}).get("trust", [])

    with open("memory/log.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()

    filtered = []
    for line in lines:
        topic = extract_tag(line, "topic")
        trust = extract_tag(line, "trust")
        if (topic in allowed_topics or not allowed_topics) and (trust in allowed_trust or not allowed_trust):
            filtered.append(line.strip())

    return filtered
