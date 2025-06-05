"""Evolves existing plugins by randomly or LLM-assisted mutations.

Creates new `plugin_evolved_*.py` files from crossover and mutation of
other plugins. May execute arbitrary generated code, so use with care.
"""

import os
import random
import subprocess
from pathlib import Path
from memory.tagger import log_tagged_memory
from inference.inference_worker import InferenceWorker


TRIGGER = {
    "type": "scheduled",
    "interval": 900  # Every 15 minutes
}

use_llm = True  # Toggle LLM mutation vs random
bitnet_model_path = "/app/BitNet/models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
bitnet_runner = "./BitNet/run_inference.py"

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

def llm_mutate_code(code, plugin1, plugin2):
    prompt = f"Mutate this Python plugin to change its behavior, improve its logic, or introduce useful variation. Preserve the 'run()' function.\n\n[START OF CODE]\n{code}\n[END OF CODE]"
    try:
        response = generate(prompt)
        if not response.strip():
            raise ValueError("BitNet response was empty")
        lines = response.splitlines()
        lines = [l for l in lines if not l.strip().startswith("# GENOME:")]
        genome = f"# GENOME: parents={plugin1} + {plugin2}; mutated=True; source=llm"
        return genome + "\n" + "\n".join(lines)
    except Exception as e:
        log_tagged_memory(f"[LLM] BitNet mutation failed: {e}", topic="plugin", trust="low")
        return None

def evolve_plugins():
    plugin_dir = Path("plugins")
    base_plugins = [f for f in plugin_dir.glob("plugin_*.py") if "evolver" not in f.name]

    if len(base_plugins) < 2:
        return

    scored = [(load_plugin_code(p), p.name) for p in base_plugins]
    scored.sort(key=lambda x: fitness(x[1]), reverse=True)

    valid_pool = [p for p in scored if "quarantine" not in p[1]]
    if len(valid_pool) < 2:
        return

    parent_samples = random.sample(valid_pool, 2)
    code1, plugin1 = parent_samples[0]
    code2, plugin2 = parent_samples[1]

    if use_llm:
        code_to_mutate = crossover_code(code1, code2)
        code_to_mutate = ensure_minimum_structure(code_to_mutate)
        new_code = llm_mutate_code(code_to_mutate, plugin1, plugin2)
        if not new_code:
            # fallback if LLM fails
            new_code = mutate_code(code_to_mutate)
            new_code = ensure_minimum_structure(new_code)
            lines = new_code.splitlines()
            lines = [l for l in lines if not l.strip().startswith("# GENOME:")]
            genome_info = f"# GENOME: parents={plugin1} + {plugin2}; mutated=True; source=fallback"
            new_code = genome_info + "\n" + "\n".join(lines)
    else:
        new_code = crossover_code(code1, code2)
        new_code = mutate_code(new_code)
        new_code = ensure_minimum_structure(new_code)
        lines = new_code.splitlines()
        lines = [l for l in lines if not l.strip().startswith("# GENOME:")]
        genome_info = f"# GENOME: parents={plugin1} + {plugin2}; mutated=True; source=local"
        new_code = genome_info + "\n" + "\n".join(lines)

    count = len([f for f in plugin_dir.glob("plugin_evolved_*.py")])
    new_path = plugin_dir / f"plugin_evolved_{count+1}.py"
    new_path.write_text(new_code, encoding="utf-8")
    log_tagged_memory(f"Evolved new plugin: {new_path.name}", topic="plugin", trust="high")

def run():
    evolve_plugins()
