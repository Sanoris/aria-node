import hashlib
import time
import json
from pathlib import Path

FACTIONS_FILE = Path("trust/factions.json")
FACTION_MIN_SIGNERS = 7

FACTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

def hash_faction_schema(schema: dict, signer_ids: list[str]) -> str:
    base = json.dumps(schema, sort_keys=True) + "|" + "|".join(sorted(signer_ids))
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def hash_name(name: str) -> str:
    return hashlib.sha256(name.encode("utf-8")).hexdigest()

def propose_faction(schema: dict, signer_ids: list[str], origin_node: dict = None):
    if len(signer_ids) < FACTION_MIN_SIGNERS:
        raise ValueError(f"Need at least {FACTION_MIN_SIGNERS} signers to form a faction.")

    faction_id = hash_faction_schema(schema, signer_ids)
    faction_record = {
        "id": faction_id,
        "schema": schema,
        "signers": signer_ids,
        "created_at": time.time()
    }

    if origin_node:
        human_name = origin_node.get("human_name")
        faction_record["origin"] = {
            "node_id": origin_node.get("node_id"),
            "name_hash": hash_name(human_name) if human_name else None,
            "hint": origin_node.get("hint", human_name)
        }

    factions = load_factions()
    if faction_id not in factions:
        factions[faction_id] = faction_record
        save_factions(factions)

    return faction_id

def load_factions():
    if FACTIONS_FILE.exists():
        with open(FACTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_factions(data):
    with open(FACTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def get_faction_schema(faction_id):
    factions = load_factions()
    return factions.get(faction_id, {}).get("schema")

def list_factions():
    factions = load_factions()
    return list(factions.keys())