import json
import os
from typing import Dict, Any

MANIFEST_PATH = "memory/plugin_manifest.json"


def _load() -> Dict[str, Any]:
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data: Dict[str, Any]):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def record_plugin(plugin_hash: str, metadata: Dict[str, Any]):
    data = _load()
    data[plugin_hash] = metadata
    _save(data)


def get_manifest() -> Dict[str, Any]:
    return _load()
