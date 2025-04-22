def evaluate_host(host, manifest):
    ip = host["ip"]
    ports = host.get("ports", [])
    existing_nodes = manifest.keys()
    score = 0
    reasons = []

    # Skip if already seeded
    if ip in existing_nodes:
        return 0, "already seeded"

    if 50051 in ports:
        score += 2
        reasons.append("has peer port")

    if 22 in ports:
        score += 1
        reasons.append("SSH reachable")

    if 80 in ports:
        score += 1
        reasons.append("HTTP reachable")

    if len(ports) >= 3:
        score += 1
        reasons.append("multi-service host")

    # Add bonus if swarm has low recon coverage
    recon_count = sum(1 for node in manifest.values() if "reconbot" in node.get("skills", []))
    if recon_count < 2:
        score += 2
        reasons.append("need reconbots")

    return score, ", ".join(reasons)
