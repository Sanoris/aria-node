import base64
import hashlib
import json
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

def extract_metadata_line(code):
    for line in code.splitlines():
        if line.strip().startswith("# __GENOME__:"):
            return line.strip()
    return None

def parse_metadata(code):
    line = extract_metadata_line(code)
    if not line:
        return None
    try:
        return json.loads(line.split(":", 1)[1].strip())
    except Exception:
        return None

def compute_hash(code):
    return hashlib.sha256(code.encode("utf-8")).digest()

def verify_signature(code):
    meta = parse_metadata(code)
    if not meta:
        return False, "Missing or invalid GENOME metadata"

    try:
        signature = base64.b64decode(meta["signature"])
        pubkey_bytes = base64.b64decode(meta["pubkey"])
        plugin_hash = compute_hash(code)

        pubkey = Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        pubkey.verify(signature, plugin_hash)

        expected_origin = hashlib.sha256(pubkey_bytes).hexdigest()[:16]
        if expected_origin != meta.get("origin"):
            return False, "Origin mismatch"

        return True, expected_origin
    except (KeyError, InvalidSignature, Exception) as e:
        return False, f"Verification failed: {e}"

def sign_plugin(code, private_key):
    plugin_hash = compute_hash(code)
    signature = private_key.sign(plugin_hash)
    pubkey = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    metadata = {
        "origin": hashlib.sha256(pubkey).hexdigest()[:16],
        "pubkey": base64.b64encode(pubkey).decode("utf-8"),
        "signature": base64.b64encode(signature).decode("utf-8"),
    }
    metadata_line = "# __GENOME__: " + json.dumps(metadata)
    return metadata_line + "\n" + code