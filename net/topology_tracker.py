import yaml
import socket

def build_peer_map():
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)
    node = cfg["node_name"]
    peer_ips = [p.split(":")[0] for p in cfg["peer_list"]]
    local = socket.gethostbyname(socket.gethostname())
    print(f"[🌐] Node: {node} @ {local}")
    print("[🛰] Peers:")
    for ip in peer_ips:
        print(f" - {ip}")
