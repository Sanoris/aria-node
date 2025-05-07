import threading
import queue
from BitNet.run_inference import generate
from memory.vector_logger import log_vector_record
from memory.tagger import log_tagged_memory
import hashlib
import time

class InferenceWorker:
    _instance = None

    def __init__(self):
        self.queue = queue.Queue()
        self.recent_delays = queue.Queue()
        self.thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.thread.start()

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def enqueue(self, prompt, callback=None):
        timestamp = time.time()
        self.queue.put((prompt, callback, timestamp))

    def _default_handler(self, prompt, output, vector):
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        log_vector_record(prompt, output, vector, digest)
        log_tagged_memory(f"[inference] {output[:60]}...", topic="inference", trust="high")

    def _worker_loop(self):
        while True:
            prompt, callback, timestamp = self.queue.get()
            delay = time.time() - timestamp
            self.recent_delays.put(delay)
            try:
                output, vector = generate(prompt)
                if callback:
                    callback(prompt, output, vector)
                else:
                    self._default_handler(prompt, output, vector)
            except Exception as e:
                log_tagged_memory(f"[inference_worker] Error: {e}", topic="inference", trust="low")