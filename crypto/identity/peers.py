# Peer public key registry
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

PEER_KEY_DIR = "crypto/peer_keys"

def get_peer_key_path(peer_id):
    return os.path.join(PEER_KEY_DIR, f"{peer_id}.pub")

def save_peer_public_key(peer_id, pubkey_bytes):
    os.makedirs(PEER_KEY_DIR, exist_ok=True)
    path = get_peer_key_path(peer_id)
    with open(path, "wb") as f:
        f.write(pubkey_bytes)

def load_peer_public_key(peer_id):
    path = get_peer_key_path(peer_id)
    with open(path, "rb") as f:
        return Ed25519PublicKey.from_public_bytes(f.read())