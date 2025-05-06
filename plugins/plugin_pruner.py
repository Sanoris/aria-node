
import os
import time
from memory.tagger import get_recent_memory, log_tagged_memory

TRIGGER = {
    "type": "scheduled",
    "interval": 600  # Every 10 minutes
}

def run():
    plugin_dir = "plugins"
    cutoff_age = time.time() - 3600  # 1 hour ago

    # Scan evolved plugins only
    plugins_to_check = [f for f in os.listdir(plugin_dir) if f.startswith("plugin_evolved_") and f.endswith(".py")]
    if not plugins_to_check:
        return

    memory = get_recent_memory(limit=200)
    trusted_plugins = set()
    untrusted_plugins = {}

    for entry in memory:
        content = entry.get("content", "")
        if not isinstance(content, str):
            continue
        for plugin in plugins_to_check:
            if plugin in content:
                if entry.get("trust") == "high":
                    trusted_plugins.add(plugin)
                elif entry.get("trust") == "low":
                    untrusted_plugins[plugin] = untrusted_plugins.get(plugin, 0) + 1

    for plugin in plugins_to_check:
        full_path = os.path.join(plugin_dir, plugin)
        if plugin in trusted_plugins:
            continue  # keep if it's been useful
        if os.path.getmtime(full_path) < cutoff_age:
            if untrusted_plugins.get(plugin, 0) >= 2:
                os.remove(full_path)
                log_tagged_memory(f"Pruned unused or low-trust plugin: {plugin}", topic="pruner", trust="high")
