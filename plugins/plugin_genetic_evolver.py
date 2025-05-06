import os
import random
import base64
from pathlib import Path
from memory.tagger import log_tagged_memory

TRIGGER = {
    "type": "scheduled",
    "interval": 900  # Every 15 minutes
}

def load_plugin_code(plugin_path):
    with open(plugin_path, "r", encoding="utf-8") as f:
        return f.read()

def crossover_code(code1, code2):
    split1 = code1.splitlines()
    split2 = code2.splitlines()
    pivot = min(len(split1), len(split2)) // 2
    return "\n".join(split1[:pivot] + split2[pivot:])

def mutate_code(code):
    lines = code.splitlines()
    if lines:
        idx = random.randint(0, len(lines) - 1)
        lines[idx] = "# mutation: " + lines[idx]
    return "\n".join(lines)

def ensure_minimum_structure(code):
    if "TRIGGER" not in code:
        code = 'TRIGGER = {"type": "scheduled", "interval": 600}\n\n' + code
    if "def run():" not in code:
        code += '\n\ndef run():\n    from memory.tagger import log_tagged_memory\n    log_tagged_memory("Evolved plugin executed.", topic="plugin", trust="neutral")\n'
    return code

def fitness(plugin_name):
    from memory.tagger import get_recent_memory
    memory = get_recent_memory(limit=300)
    success = sum(1 for e in memory if e["topic"] == "fitness" and plugin_name in e.get("content", "") and e["trust"] == "high")
    failure = sum(1 for e in memory if e["topic"] == "fitness" and plugin_name in e.get("content", "") and e["trust"] == "low")
    return success - (2 * failure)

def evolve_plugins():
    plugin_dir = Path("plugins")
    base_plugins = [f for f in plugin_dir.glob("plugin_*.py") if "evolver" not in f.name]

    if len(base_plugins) < 2:
        return

    scored = [(load_plugin_code(p), p.name) for p in base_plugins]
    scored.sort(key=lambda x: fitness(x[1]), reverse=True)

    plugin1, plugin2 = scored[0][1], scored[1][1]
    code1, code2 = scored[0][0], scored[1][0]

    new_code = crossover_code(code1, code2)
    new_code = mutate_code(new_code)
    new_code = ensure_minimum_structure(new_code)
    genome_info = f"# GENOME: parents={plugin1} + {plugin2}; mutated=True\n"
    new_code = genome_info + new_code

    count = len([f for f in plugin_dir.glob("plugin_evolved_*.py")])
    new_path = plugin_dir / f"plugin_evolved_{count+1}.py"
    new_path.write_text(new_code, encoding="utf-8")
    log_tagged_memory(f"Evolved new plugin: {new_path.name}", topic="plugin", trust="high")

def run():
    evolve_plugins()