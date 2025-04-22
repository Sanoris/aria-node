def run():
    import platform, os
    from memory.tagger import log_tagged_memory
    info = f"System: {platform.system()}, Release: {platform.release()}, PID: {os.getpid()}"
    log_tagged_memory(info, topic="sysinfo", trust="low")
