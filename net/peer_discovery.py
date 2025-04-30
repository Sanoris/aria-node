import yaml
import socket
import time
import os
import logging
import dns.resolver
from concurrent.futures import ThreadPoolExecutor

CONFIG_PATH = "config.yaml"
SEED_FILE = "peers.seed"

# Logger setup
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("peer_discovery")

def ping_peer(ip, port, timeout=2):
    try:
        with socket.create_connection((ip, int(port)), timeout=timeout):
            return True
    except Exception:
        return False

def load_seeds_from_file(path=SEED_FILE):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def load_seeds_from_dns(domain, use_srv=False):
    try:
        if use_srv:
            answers = dns.resolver.resolve(domain, "SRV")
            srv_records = [f"{rdata.target.to_text().rstrip('.')}: {rdata.port}" for rdata in answers]
            return srv_records
        else:
            answers = dns.resolver.resolve(domain, "TXT")
            txt_records = [rdata.to_text().strip('"') for rdata in answers]
            return sum((record.split(",") for record in txt_records), [])
    except Exception as e:
        logger.error(f"DNS seed failed: {e}")
        return []

def check_seed(seed, timeout):
    ip_port = seed.split(":")
    if len(ip_port) == 2 and ping_peer(ip_port[0], ip_port[1], timeout=timeout):
        return seed
    return None

def update_seed_file(new_peers, path=SEED_FILE):
    existing = set(load_seeds_from_file(path))
    with open(path, "a") as f:
        for peer in new_peers:
            if peer not in existing:
                f.write(peer + "\n")

def discover_peers():
    with open(CONFIG_PATH, "r") as f:
        cfg = yaml.safe_load(f)

    existing_peers = cfg.get("sync_peers", [])
    dns_seed_domain = cfg.get("dns_seed", None)
    use_srv = cfg.get("dns_seed_srv", False)
    ping_timeout = cfg.get("ping_timeout", 2)
    MAX_PEERS = cfg.get("max_peers", 100)

    seeds = existing_peers.copy()

    if dns_seed_domain:
        seeds += load_seeds_from_dns(dns_seed_domain, use_srv=use_srv)

    # Deduplicate seeds
    seeds = list(set(seeds))

    discovered = []

    # Parallel ping/discovery
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda s: check_seed(s, ping_timeout), seeds)
        for result in results:
            if result:
                print(f"[+] Found live peer: {result}")
                discovered.append(result)
            else:
                print("[-] Peer offline")

    # Deduplicate final list
    new_peers = list(set(discovered))
    new_peers = new_peers[:MAX_PEERS]

    cfg["sync_peers"] = new_peers

    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(cfg)

    print(f"[✓] Discovery complete. {len(discovered)} live peer(s) retained.")


if __name__ == "__main__":
    discover_peers()
