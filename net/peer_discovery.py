import yaml
import socket
import time
import requests
import dns.resolver

CONFIG_PATH = "config.yaml"
SEED_FILE = "peers.seed"

def ping_peer(ip, port):
    try:
        with socket.create_connection((ip, int(port)), timeout=2):
            return True
    except Exception:
        return False

def load_seeds_from_file(path=SEED_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_seeds_from_dns(domain):
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        txt_records = [rdata.to_text().strip('"') for rdata in answers]
        return sum((record.split(",") for record in txt_records), [])
    except Exception as e:
        print(f"[!] DNS seed failed: {e}")
        return []

def discover_peers():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    peers = cfg.get("peer_list", [])
    seeds = load_seeds_from_file()

    dns_seed_domain = cfg.get("dns_seed")
    if dns_seed_domain:
        seeds += load_seeds_from_dns(dns_seed_domain)

    discovered = []
    for seed in seeds:
        ip_port = seed.split(":")
        if len(ip_port) == 2 and ping_peer(*ip_port):
            if seed not in peers and seed not in discovered:
                print(f"[+] Found live peer: {seed}")
                discovered.append(seed)
        else:
            print(f"[-] Peer offline: {seed}")

    if discovered:
        peers += discovered
        cfg["peer_list"] = list(set(peers))
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(cfg, f)
        print(f"[✓] Added {len(discovered)} new peer(s) to config.yaml")

if __name__ == "__main__":
    discover_peers()
