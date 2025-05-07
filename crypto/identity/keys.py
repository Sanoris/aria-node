# Node's own identity management
import os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

KEY_DIR = "crypto/keys"
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private_key.pem")

def generate_keypair():
    private_key = Ed25519PrivateKey.generate()
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    return private_key

def load_keys():
    if not os.path.exists(PRIVATE_KEY_PATH):
        return generate_keypair()

    with open(PRIVATE_KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )
    return private_key

def load_public_key():
    return load_keys().public_key()