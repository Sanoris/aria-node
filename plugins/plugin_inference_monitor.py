import time
from memory.tagger import log_tagged_memory
from inference.inference_worker import InferenceWorker

TRIGGER = {
    "type": "scheduled",
    "interval": 60  # every minute
}

MAX_QUEUE_THRESHOLD = 10

def run():
    worker = InferenceWorker.get()
    queue_size = worker.queue.qsize()

    if queue_size > 0:
        log_tagged_memory(f"[monitor] Inference queue size: {queue_size}", topic="inference", trust="neutral")

    if queue_size > MAX_QUEUE_THRESHOLD:
        log_tagged_memory(
            f"Swarm delay advisory: Inference queue backlog is high ({queue_size} entries). Consider throttling low-priority plugins.",
            topic="inference",
            trust="inferred"
        )