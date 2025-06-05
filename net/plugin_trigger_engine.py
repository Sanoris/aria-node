import time
import threading
import importlib.util
from pathlib import Path
from memory.tagger import log_tagged_memory, get_recent_memory
import base64
from cryptography.hazmat.primitives import serialization
from memory.plugin_manifest import get_manifest
from crypto.manifest_signer import verify_manifest
from crypto.identity.keys import load_public_key
import hashlib

PLUGINS_DIR = Path("plugins")


def load_plugins():
    import shutil
    plugins = []
    for plugin_file in PLUGINS_DIR.glob("plugin_*.py"):
        try:
            manifest = get_manifest()
            code_bytes = plugin_file.read_bytes()
            plugin_hash = hashlib.sha256(code_bytes).hexdigest()
            meta = manifest.get(plugin_hash)
            if not meta:
                log_tagged_memory(f"Manifest missing for {plugin_file.name}", topic="plugin", trust="low")
                continue
            pub = load_public_key()
            if not verify_manifest(meta, meta.get("author_signature", ""), pub):
                raise ValueError("signature mismatch")

            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            # warn if run() missing
            if not hasattr(mod, "run") or not callable(getattr(mod, "run")):
                log_tagged_memory(
                    f"Plugin {plugin_file.name} missing run()",
                    topic="plugin",
                    trust="low",
                )

            # warn if malformed TRIGGER
            trigger = getattr(mod, "TRIGGER", None)
            if not isinstance(trigger, dict) or "type" not in trigger:
                log_tagged_memory(
                    f"Plugin {plugin_file.name} has malformed TRIGGER",
                    topic="plugin",
                    trust="low",
                )

            plugins.append(mod)
        except Exception as e:
            from memory.tagger import log_tagged_memory
            quarantine_dir = PLUGINS_DIR.parent / "quarantine"
            quarantine_dir.mkdir(exist_ok=True)
            quarantined_path = quarantine_dir / plugin_file.name
            try:
                shutil.move(str(plugin_file), str(quarantined_path))
                msg = f"Quarantined broken plugin {plugin_file.name}: {e}"
                log_tagged_memory(msg, topic="plugin", trust="low")
                print(msg)
            except Exception as move_err:
                msg = f"Failed to quarantine {plugin_file.name}: {move_err}"
                log_tagged_memory(msg, topic="plugin", trust="low")
                print(msg)
    return plugins


def scheduled_runner(plugin, interval):
    while True:
        try:
            plugin.run()
        except Exception as e:
            log_tagged_memory(f"Error in plugin {plugin.__name__}: {e}", topic="plugin", trust="low")
        time.sleep(interval)

def entry_matches(entry, match_dict):
    if not isinstance(entry, dict):
        return False
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

def receive_and_write_plugin(filename, data_b64, signature):
    try:
        from crypto import load_keys
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        code_bytes = base64.b64decode(data_b64)
        _, pub = load_keys()
        pub_bytes = pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)

        signature_bytes = base64.b64decode(signature)
        pub_key.verify(signature_bytes, code_bytes)  # throws if bad

        path = PLUGINS_DIR / filename
        path.write_text(code_bytes.decode("utf-8"), encoding="utf-8")

        log_tagged_memory(f"Verified and saved plugin: {filename}", topic="plugin", trust="high")
        log_tagged_memory(f"Plugin {filename} imported via replication", topic="fitness", trust="neutral")

        if "GENOME:" not in code_bytes.decode("utf-8"):
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n# GENOME: source=replicated; origin={filename}\n")

        return True
    except Exception as e:
        log_tagged_memory(f"Plugin verification failed: {e}", topic="plugin", trust="low")
        return False


if __name__ == "__main__":
    start_plugins()
    while True:
        time.sleep(60)
