import os
import json
import hashlib
import base64
from pathlib import Path
from memory.tagger import log_tagged_memory
from crypto.identity.genome import parse_metadata, compute_hash
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature

KNOWN_HASHES_PATH = "plugins/known_hashes.json"
PEER_KEYS_DIR = "crypto/peer_keys"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_known_hashes() -> dict:
    if os.path.exists(KNOWN_HASHES_PATH):
        with open(KNOWN_HASHES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def verify_signature(code: str) -> bool:
    """Verify plugin signature if GENOME metadata present."""
    meta = parse_metadata(code)
    if not meta:
        return True  # no signature to verify
    try:
        origin = meta.get("origin")
        signature = base64.b64decode(meta["signature"])
        pubkey_bytes = base64.b64decode(meta["pubkey"])
        pubkey = Ed25519PublicKey.from_public_bytes(pubkey_bytes)
        pubkey.verify(signature, compute_hash(code))
        key_file = Path(PEER_KEYS_DIR) / f"{origin}.pub"
        if key_file.exists():
            if key_file.read_bytes() != pubkey_bytes:
                return False
        return True
    except (InvalidSignature, KeyError, Exception):
        return False


def analyze_peer_plugins(plugin_list, plugin_dir: str = "plugins") -> bool:
    """Validate plugins by hash and optional signature."""
    known_hashes = load_known_hashes()
    all_good = True
    for name in plugin_list:
        fname = name if name.endswith(".py") else f"{name}.py"
        path = Path(plugin_dir) / fname
        if not path.exists():
            log_tagged_memory(f"Plugin missing locally: {fname}", topic="peer", trust="low")
            all_good = False
            continue
        file_hash = sha256_file(path)
        expected = known_hashes.get(fname)
        if expected != file_hash:
            log_tagged_memory(f"Hash mismatch for {fname}", topic="peer", trust="low")
            all_good = False
        else:
            log_tagged_memory(f"Hash ok for {fname}", topic="peer", trust="high")
        try:
            code = path.read_text(encoding="utf-8")
            if verify_signature(code):
                log_tagged_memory(f"Signature verified for {fname}", topic="peer", trust="high")
            else:
                log_tagged_memory(f"Signature verify failed for {fname}", topic="peer", trust="low")
                all_good = False
        except Exception as e:
            log_tagged_memory(f"Signature check error for {fname}: {e}", topic="peer", trust="low")
            all_good = False
    return all_good
