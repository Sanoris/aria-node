import time
import json
from statistics import mean
from memory.tagger import log_tagged_memory
from inference.inference_worker import InferenceWorker

TRIGGER = {
    "type": "scheduled",
    "interval": 120  # every 2 minutes
}

LOG_FILE = "logs/inference_latency.jsonl"

def run():
    worker = InferenceWorker.get()

    delays = []
    while not worker.recent_delays.empty():
        try:
            delay = worker.recent_delays.get_nowait()
            delays.append(delay)
        except:
            break

    if not delays:
        return

    avg_delay = mean(delays)
    max_delay = max(delays)

    log_tagged_memory(
        f"Inference delay stats: avg {avg_delay:.2f}s, max {max_delay:.2f}s over {len(delays)} jobs",
        topic="inference",
        trust="neutral"
    )

    log_entry = {
        "timestamp": time.time(),
        "avg_delay": avg_delay,
        "max_delay": max_delay,
        "count": len(delays)
    }

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\\n")