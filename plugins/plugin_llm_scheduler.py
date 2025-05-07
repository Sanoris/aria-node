from memory.tagger import get_recent_memory, log_tagged_memory
from inference.inference_worker import InferenceWorker
import hashlib
from memory.vector_logger import log_vector_record

TRIGGER = {
    "type": "scheduled",
    "interval": 300
}

def handle_result(prompt, output, vector):
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    log_vector_record(prompt, output, vector, digest)
    log_tagged_memory(f"[inference] {output[:60]}...", topic="inference", trust="high")

def run():
    log_tagged_memory("LLM scheduler triggered", topic="debug", trust="neutral")
    prompt = (
        "System: You are a scheduling assistant for swarm plugin activity. "
        "Read the recent swarm memory and determine if any plugin should be scheduled or disabled. "
        "Respond with a recommendation only.\n\n"
        "User: Based on system load and memory, what action should be taken next?"
    )
    InferenceWorker.get().enqueue(prompt, callback=handle_result)
