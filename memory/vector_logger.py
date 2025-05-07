import os
import time
import json
from memory.tagger import log_tagged_memory

LOG_FILE = "logs/vectors.jsonl"
os.makedirs("logs", exist_ok=True)

def log_vector_record(prompt, output, vector, digest=None):
    record = {
        "timestamp": time.time(),
        "digest": digest,
        "prompt": prompt,
        "output": output,
        "vector": vector,
    }
    # Save to persistent file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

    # Also tag memory with a light marker
    log_tagged_memory(
        f"Logged vector for prompt: {prompt[:40]}...",
        topic="inference",
        trust="high"
    )