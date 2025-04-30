# crypto/peer_keys.py

import os

PEER_KEY_DIR = "crypto/peers"

def get_peer_key_path(peer_address):
    safe_name = peer_address.replace(":", "_")
    return os.path.join(PEER_KEY_DIR, f"{safe_name}.pem")

def save_peer_public_key(peer_address, public_key_pem):
    os.makedirs(PEER_KEY_DIR, exist_ok=True)
    with open(get_peer_key_path(peer_address), "wb") as f:
        f.write(public_key_pem)

def load_peer_public_key(peer_address):
    try:
        with open(get_peer_key_path(peer_address), "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None