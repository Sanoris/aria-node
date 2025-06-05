"""Uses an LLM to summarize recent memory and provide swarm insights.

Could leak private data via prompts and may misinterpret context,
leading to misleading analysis.
"""

import os
import sys
import signal
import platform
import argparse
import hashlib
from memory.tagger import get_recent_memory, log_tagged_memory
from memory.vector_logger import log_vector_record
from inference.inference_worker import InferenceWorker

TRIGGER = {
    "type": "scheduled",
    "interval": 30,
}

def handle_result(prompt, output, vector):
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    log_vector_record(prompt, output, vector, digest)

    assistant_response = None
    for line in output.splitlines():
        if line.strip().startswith("Assistant:"):
            assistant_response = line.strip().removeprefix("Assistant:").strip()
            break

    if assistant_response:
        log_tagged_memory(f"LLM Insight: {assistant_response}", topic="swarm_reflection", trust="inferred")
    else:
        log_tagged_memory("LLM Insight: (no assistant response found)", topic="swarm_reflection", trust="low")

def run():
    memories = get_recent_memory(limit=20)
    memory_lines = []
    for entry in memories:
        topic = entry.get("topic", "")
        content = entry.get("content", "")
        if isinstance(content, dict):
            content = str(content)
        memory_lines.append(f"- [{topic}] {content}")

    prompt = (
        "System: You are a distributed node's internal thinking engine. "
        "Review the following recent memories. Identify one current issue or opportunity clearly and briefly.\n\n"
        "User:\n" + "\n".join(memory_lines) +
        "\n\nUser: Provide a one-line summary of what the swarm appears to be doing and one suggestion. "
        "Do NOT include the phrases: 'Current swarm phase is', 'Potential risks include', or 'What is the status of the swarm?'"
    )

    InferenceWorker.get().enqueue(prompt, callback=handle_result)

# Optional CLI for manual testing
if __name__ == "__main__":
    signal.signal(signal.SIGINT, lambda s, f: sys.exit(0))
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prompt", required=True)
    args = parser.parse_args()
    InferenceWorker.get().enqueue(args.prompt, callback=handle_result)
