# utils/hash_utils.py
import hashlib
from pathlib import Path

def sha256_file(path):
    """Returns the SHA-256 hash of a file as hex."""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def hash_plugin_directory(plugin_dir):
    """Returns a dict of plugin file names to SHA-256 hashes."""
    hashes = {}
    for plugin in Path(plugin_dir).glob("plugin_*.py"):
        hashes[plugin.name] = sha256_file(plugin)
    return hashes
