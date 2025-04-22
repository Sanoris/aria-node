from net.swarm_manifest import read_manifest

def assign_roles(role):
    manifest = read_manifest()
    matches = [node for node, data in manifest.items() if role in data.get("skills", [])]
    if matches:
        print(f"[🎯] Nodes matching role '{role}':", matches)
        return matches
    else:
        print(f"[✖] No nodes match role '{role}'")
        return []

if __name__ == "__main__":
    assign_roles("reconbot")
