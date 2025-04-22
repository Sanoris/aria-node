import os
import time
import subprocess
import psutil
from memory.tagger import log_tagged_memory

WATCH_PROCESS = "node.py"
CHECK_INTERVAL = 30  # seconds

def is_process_running(name):
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if any(name in cmd for cmd in proc.info['cmdline']):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False

def restart_node():
    log_tagged_memory("Node process missing. Attempting restart.", topic="watchdog", trust="high")
    subprocess.Popen(["python", "node.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def watchdog_loop():
    print("[🕷️] Aria Watchdog started.")
    while True:
        if not is_process_running(WATCH_PROCESS):
            print("[⚠️] Aria node not running. Restarting...")
            restart_node()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    watchdog_loop()
