# trust/manager.py

trust_db = {}

def initialize_peer_trust(peer_address):
    if peer_address not in trust_db:
        trust_db[peer_address] = 0.5  # neutral initial trust score
        print(f"[🔐] Initialized trust for {peer_address} to 0.5")