# Identity toolkit wrapper
import hashlib
from .keys import load_public_key
from cryptography.hazmat.primitives import serialization


def get_node_id():
    pub = load_public_key()
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    return hashlib.sha256(raw).hexdigest()[:16]
