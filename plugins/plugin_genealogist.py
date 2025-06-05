"""Reports lineage information for evolved plugins by reading genome headers.

Useful for tracing plugin origins but may reveal details about mutations
or source nodes if leaked.
"""

import os
import json
from memory.tagger import log_tagged_memory

TRIGGER = {
    "type": "scheduled",
    "interval": 900  # Every 15 minutes
}

def extract_genome_header(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    genome_lines = [line.strip("# ").strip() for line in lines if line.strip().startswith("# GENOME")]
    if not genome_lines:
        return None
    return genome_lines[0].replace("GENOME:", "").strip()

def run():
    plugin_dir = "plugins"
    evolved = [f for f in os.listdir(plugin_dir) if f.startswith("plugin_evolved_") and f.endswith(".py")]

    if not evolved:
        return

    ancestry = {}

    for plugin in evolved:
        genome = extract_genome_header(os.path.join(plugin_dir, plugin))
        if genome:
            ancestry[plugin] = genome

    if ancestry:
        summary = json.dumps(ancestry, indent=2)
        log_tagged_memory(f"Evolved plugin lineage:\n{summary}", topic="genealogist", trust="high")
