import time
import threading
import importlib.util
from pathlib import Path
from memory.tagger import log_tagged_memory, get_recent_memory

PLUGINS_DIR = Path("plugins")

def load_plugins():
    plugins = []
    for plugin_file in PLUGINS_DIR.glob("plugin_*.py"):
        spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        plugins.append(mod)
    return plugins

def scheduled_runner(plugin, interval):
    while True:
        try:
            plugin.run()
        except Exception as e:
            log_tagged_memory(f"Error in plugin {plugin.__name__}: {e}", topic="plugin", trust="low")
        time.sleep(interval)

def entry_matches(entry, match_dict):
    return all(entry.get(k) == v for k, v in match_dict.items())

def event_watcher(plugin, match_dict):
    last_seen_timestamp = None

    while True:
        recent_entries = get_recent_memory(limit=10)
        for entry in recent_entries:
            timestamp = entry.get("timestamp")
            if last_seen_timestamp and timestamp <= last_seen_timestamp:
                continue
            if entry_matches(entry.get("content", {}), match_dict) or entry_matches(entry, match_dict):
                try:
                    plugin.run()
                    log_tagged_memory(f"Triggered plugin {plugin.__name__} on event match", topic="plugin", trust="high")
                except Exception as e:
                    log_tagged_memory(f"Event plugin {plugin.__name__} error: {e}", topic="plugin", trust="low")
        if recent_entries:
            last_seen_timestamp = recent_entries[-1].get("timestamp")
        time.sleep(30)

def start_plugins():
    plugins = load_plugins()
    for plugin in plugins:
        trigger = getattr(plugin, "TRIGGER", {})
        ttype = trigger.get("type")
        interval = trigger.get("interval", 300)
        if ttype == "scheduled":
            t = threading.Thread(target=scheduled_runner, args=(plugin, interval), daemon=True)
            t.start()
            log_tagged_memory(f"Started scheduled plugin {plugin.__name__}", topic="plugin", trust="high")
        elif ttype == "passive":
            try:
                plugin.run()
                log_tagged_memory(f"Started passive plugin {plugin.__name__}", topic="plugin", trust="high")
            except Exception as e:
                log_tagged_memory(f"Passive plugin {plugin.__name__} error: {e}", topic="plugin", trust="low")
        elif ttype == "event":
            match_dict = trigger.get("match", {})
            t = threading.Thread(target=event_watcher, args=(plugin, match_dict), daemon=True)
            t.start()
            log_tagged_memory(f"Started event plugin {plugin.__name__} (watching for match: {match_dict})", topic="plugin", trust="high")

def run_plugins_by_trigger(trigger):
    plugins = load_plugins()
    for plugin in plugins:
        if plugin.__name__ == trigger:
            try:
                plugin.run()
                print(f"[⚡] Triggered plugin: {trigger}")
            except Exception as e:
                print(f"[!] Plugin {trigger} failed: {e}")

if __name__ == "__main__":
    start_plugins()
    while True:
        time.sleep(60)