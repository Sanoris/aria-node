# Identity toolkit wrapper
import hashlib
from .keys import load_public_key, load_keys
from cryptography.hazmat.primitives import serialization


def get_node_id():
    pub = load_public_key()
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return hashlib.sha256(raw).hexdigest()[:16]



def sign_message(message: bytes) -> bytes:
    """Sign the given message using the node's private key."""
    if isinstance(message, str):
        message = message.encode("utf-8")
    private_key = load_keys()
    return private_key.sign(message)

