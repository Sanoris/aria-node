import socket
import yaml

def detect_fork(peer_ips):
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    forks = [ip for ip in peer_ips if ip != local_ip]
    if forks:
        print(f"[⚠️] Possible fork detected: {forks}")
        return True
    return False

if __name__ == "__main__":
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
        peer_list = [p.split(":")[0] for p in cfg.get("peer_list", [])]
        detect_fork(peer_list)
