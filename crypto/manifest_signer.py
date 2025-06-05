import json
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.exceptions import InvalidSignature


def _hash_dict(data: dict) -> bytes:
    serialized = json.dumps(data, sort_keys=True).encode("utf-8")
    return hashlib.sha256(serialized).digest()


def sign_manifest(manifest: dict, private_key: Ed25519PrivateKey) -> str:
    h = _hash_dict(manifest)
    signature = private_key.sign(h)
    return base64.b64encode(signature).decode("utf-8")


def verify_manifest(manifest: dict, signature_b64: str, public_key: Ed25519PublicKey) -> bool:
    h = _hash_dict(manifest)
    try:
        signature = base64.b64decode(signature_b64)
        public_key.verify(signature, h)
        return True
    except (InvalidSignature, ValueError):
        return False
