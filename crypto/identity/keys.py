# Node's own identity management
import os
import json
import base64
import hashlib
from datetime import datetime
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

KEY_DIR = "crypto/keys"
PRIVATE_KEY_PATH = os.path.join(KEY_DIR, "node_private_key.pem")
ROTATIONS_PATH = os.path.join(KEY_DIR, "rotations.json")

def generate_keypair():
    private_key = Ed25519PrivateKey.generate()
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    return private_key

def _save_private_key(private_key):
    os.makedirs(KEY_DIR, exist_ok=True)
    with open(PRIVATE_KEY_PATH, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

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

def rotate_keys():
    old_key = load_keys()
    new_key = Ed25519PrivateKey.generate()
    _save_private_key(new_key)

    rotation_record = {
        "node_id": hashlib.sha256(
            old_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).hexdigest()[:16],
        "current_key": base64.b64encode(
            new_key.public_key().public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).decode("utf-8"),
        "prev_keys": [],
        "rotation_signature": base64.b64encode(
            old_key.sign(
                new_key.public_key().public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                )
            )
        ).decode("utf-8"),
        "rotated_at": datetime.utcnow().isoformat() + "Z",
    }

    try:
        if os.path.exists(ROTATIONS_PATH):
            with open(ROTATIONS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = []
    except Exception:
        data = []

    data.append(rotation_record)
    with open(ROTATIONS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return new_key
