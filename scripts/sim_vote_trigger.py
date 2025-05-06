from memory.tagger import log_tagged_memory
import time

def simulate_decision():
    # Context for the LLM to analyze
    log_tagged_memory("plugin_stealth_sync.py synced with 3 peers", topic="plugin", trust="high")
    log_tagged_memory("Peer 192.168.1.42 failed trust validation with plugin_stealth_sync.py", topic="trust", trust="low")
    time.sleep(1)

    # Trigger decision
    log_tagged_memory("Proposing decision: plugin_stealth_sync.py:promote", topic="decision", trust="neutral")

if __name__ == "__main__":
    simulate_decision()