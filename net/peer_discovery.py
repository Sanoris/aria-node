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

    peers = cfg.get("peer_list", [])
    seeds = load_seeds_from_file()

    dns_seed_domain = cfg.get("dns_seed")
    if dns_seed_domain:
        use_srv = cfg.get("dns_seed_srv", False)
        seeds += load_seeds_from_dns(dns_seed_domain, use_srv=use_srv)

    discovered = []
    ping_timeout = cfg.get("ping_timeout", 2)

    # Parallel ping
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda s: check_seed(s, ping_timeout), seeds)
        for result in results:
            if result:
                logger.info(f"[+] Found live peer: {result}")
                discovered.append(result)
            else:
                logger.warning(f"[-] Peer offline")

    # Handle peer expiry
    current_time = time.time()
    peer_expiry = cfg.get("peer_expiry", 86400)
    new_peers = []
    for peer in peers:
        if current_time - peer.get("last_seen", 0) < peer_expiry:
            new_peers.append(peer)
        else:
            logger.warning(f"[-] Peer expired: {peer['ip']}:{peer['port']}")

    for seed in discovered:
        ip, port = seed.split(":")
        new_peers.append({"ip": ip, "port": int(port), "last_seen": current_time})

    cfg["peer_list"] = new_peers

    with open(CONFIG_PATH, "w") as f:
        yaml.dump(cfg, f)
    logger.info(f"[✓] Discovery complete. {len(discovered)} new peer(s) added.")

    if discovered:
        update_seed_file(discovered)

if __name__ == "__main__":
    discover_peers()
