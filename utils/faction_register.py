import hashlib
import json
from net.swarm_manifest import read_manifest, MANIFEST_PATH
from pathlib import Path

def hash_faction(name: str) -> str:
    return hashlib.sha256(name.encode("utf-8")).hexdigest()

def register_faction(name, motto, author, genesis_note):
    faction_id = hash_faction(name)
    manifest = read_manifest()

    if "factions" not in manifest:
        manifest["factions"] = {}

    if faction_id in manifest["factions"]:
        print(f"[!] Faction already exists: {name}")
        return faction_id

    manifest["factions"][faction_id] = {
        "name": name,
        "motto": motto,
        "author": author,
        "genesis": genesis_note
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=4)
    
    print(f"[+] Faction '{name}' registered under ID: {faction_id}")
    return faction_id

# Optional manual call
if __name__ == "__main__":
    name = input("Faction name: ")
    motto = input("Faction motto: ")
    author = input("Author: ")
    genesis = input("Genesis/Note: ")
    register_faction(name, motto, author, genesis)
