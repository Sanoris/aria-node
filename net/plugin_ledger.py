"""Plugin lineage ledger using SHA256 hashes."""

import os
import json
import time
import hashlib

LEDGER_PATH = "memory/plugin_ledger.json"


def _compute_hash(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def load_ledger() -> dict:
    try:
        with open(LEDGER_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_ledger(ledger: dict) -> None:
    os.makedirs(os.path.dirname(LEDGER_PATH), exist_ok=True)
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)


def register_plugin(code: str, parent_hash: str | None = None,
                     lineage_map: dict | None = None, label: str | None = None) -> str:
    ledger = load_ledger()
    plugin_hash = _compute_hash(code)
    if plugin_hash in ledger:
        return plugin_hash

    ledger[plugin_hash] = {
        "plugin_hash": plugin_hash,
        "parent_hash": parent_hash,
        "lineage_map": lineage_map or {},
        "label": label,
        "timestamp": time.time(),
    }
    save_ledger(ledger)
    return plugin_hash


def get_lineage(plugin_hash: str) -> list[str]:
    ledger = load_ledger()
    lineage = []
    current = plugin_hash
    while current and current in ledger:
        lineage.append(current)
        current = ledger[current].get("parent_hash")
    return lineage

