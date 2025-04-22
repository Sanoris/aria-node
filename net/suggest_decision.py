def publish_decision(decision_text):
    from memory.tagger import log_tagged_memory
    log_tagged_memory(decision_text, topic="decision", trust="high")
