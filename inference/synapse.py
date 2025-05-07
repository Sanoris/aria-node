# synapse.py
"""
Rolling digest system for swarm memory.
Maintains a lightweight narrative summary and token hash of recent memory entries,
allowing inference models to request context with minimal overhead.
"""
import hashlib
import json
from memory.tagger import get_recent_memory

MAX_CONTEXT = 20
_digest = None
_summary = None


def compute_digest(entries):
    hasher = hashlib.sha256()
    summary_lines = []

    for entry in entries:
        digestible = f"[{entry.get('timestamp', 0)}] <{entry.get('topic', 'unknown')}> {entry.get('content', '').strip()}"
        summary_lines.append(digestible)
        hasher.update(digestible.encode('utf-8'))

    return hasher.hexdigest(), "\n".join(summary_lines)


def refresh_synapse():
    global _digest, _summary
    memory = get_recent_memory(limit=MAX_CONTEXT)
    _digest, _summary = compute_digest(memory)
    return _digest


def get_synapse_digest():
    return _digest or refresh_synapse()


def get_synapse_summary():
    return _summary or "[synapse not yet initialized]"


def synapse_payload():
    return {
        "digest": get_synapse_digest(),
        "summary": get_synapse_summary(),
    }


if __name__ == "__main__":
    print(json.dumps(synapse_payload(), indent=2))
