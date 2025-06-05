import time
import threading
import importlib.util
from pathlib import Path
import base64
import hashlib
import shutil

from memory.tagger import log_tagged_memory, get_recent_memory

# --- verification helpers ----------------------------------------------------
from crypto.identity.genome import verify_signature                     # code-level sigs
from memory.plugin_manifest import get_manifest                         # manifest file
from crypto.manifest_signer import verify_manifest                      # manifest sigs
from crypto.identity.keys import load_public_key                        # pk for manifest
from cryptography.hazmat.primitives import serialization
import yaml
from utils.plugin_sandbox import run_in_sandbox

# -----------------------------------------------------------------------------


PLUGINS_DIR = Path("plugins")

CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

QUARANTINE_DIR = PLUGINS_DIR.parent / "quarantine"
QUARANTINE_DIR.mkdir(exist_ok=True)



def _quarantine(plugin_path: Path, reason: str):
    """Move a plugin to the quarantine directory and log why."""
    try:
        dest = QUARANTINE_DIR / plugin_path.name
        shutil.move(str(plugin_path), str(dest))
        log_tagged_memory(f"Quarantined plugin {plugin_path.name}: {reason}",
                          topic="plugin", trust="low")
    except Exception as move_err:
        log_tagged_memory(f"Failed to quarantine {plugin_path.name}: {move_err}",
                          topic="plugin", trust="low")


def _verify_plugin(code_bytes: bytes) -> tuple[bool, str]:
    """
    Try manifest verification first (stronger, hashes whole file + author sig).
    Fallback to in-code genome signature if manifest data is missing or invalid.
    Returns (valid, info_message).
    """
    manifest = get_manifest()
    plugin_hash = hashlib.sha256(code_bytes).hexdigest()

    if manifest and plugin_hash in manifest:
        meta = manifest[plugin_hash]
        pubkey = load_public_key()
        if verify_manifest(meta, meta.get("author_signature", ""), pubkey):
            return True, "manifest verified"
        else:
            return False, "manifest signature mismatch"

    # Fallback: genome signature embedded inside the code
    valid, info = verify_signature(code_bytes.decode("utf-8", errors="ignore"))
    return valid, f"genome check: {info}"


# -----------------------------------------------------------------------------
# Plugin loader
# -----------------------------------------------------------------------------
def load_plugins():
    plugins: list = []

    for plugin_file in PLUGINS_DIR.glob("plugin_*.py"):
        try:
            code_bytes = plugin_file.read_bytes()
        except Exception as read_err:
            log_tagged_memory(f"Failed to read plugin {plugin_file.name}: {read_err}",
                              topic="plugin", trust="low")
            continue

        # --- signature / manifest verification -------------------------------
        valid, info = _verify_plugin(code_bytes)
        if not valid:
            _quarantine(plugin_file, info)
            continue

        # --- dynamic import ---------------------------------------------------
        try:
            spec = importlib.util.spec_from_file_location(plugin_file.stem, plugin_file)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
        except Exception as import_err:
            _quarantine(plugin_file, f"import error: {import_err}")
            continue

        # --- basic sanity checks ---------------------------------------------
        if not callable(getattr(mod, "run", None)):
            _quarantine(plugin_file, "missing callable run()")
            continue

        trigger = getattr(mod, "TRIGGER", {})
        ttype = trigger.get("type")
        if ttype not in {"scheduled", "event", "passive"}:
            log_tagged_memory(f"Malformed TRIGGER in {plugin_file.name}: unknown type {ttype}",
                              topic="plugin", trust="low")
        elif ttype == "scheduled" and "interval" not in trigger:
            log_tagged_memory(f"Malformed TRIGGER in {plugin_file.name}: missing 'interval'",
                              topic="plugin", trust="low")
        elif ttype == "event" and "match" not in trigger:
            log_tagged_memory(f"Malformed TRIGGER in {plugin_file.name}: missing 'match'",
                              topic="plugin", trust="low")

        plugins.append(mod)

    return plugins



def scheduled_runner(plugin, interval, sandbox=False):

# -----------------------------------------------------------------------------
# Trigger runners
# -----------------------------------------------------------------------------

    while True:
        try:
            if sandbox:
                run_in_sandbox(plugin.__file__, env_vars={}, work_dir=str(PLUGINS_DIR))
            else:
                plugin.run()
        except Exception as e:

            log_tagged_memory(
                f"Error in plugin {plugin.__name__}: {e}", topic="plugin", trust="low"
            )

        time.sleep(interval)


def entry_matches(entry, match_dict):
    return isinstance(entry, dict) and all(entry.get(k) == v for k, v in match_dict.items())


def event_watcher(plugin, match_dict):
    last_seen_timestamp = None
    while True:
        recent_entries = get_recent_memory(limit=10)
        for entry in recent_entries:
            ts = entry.get("timestamp")
            if last_seen_timestamp and ts <= last_seen_timestamp:
                continue
            if entry_matches(entry.get("content", {}), match_dict) or entry_matches(entry, match_dict):
                try:
                    plugin.run()
                    log_tagged_memory(f"Triggered plugin {plugin.__name__} on event match",
                                      topic="plugin", trust="high")
                except Exception as e:
                    log_tagged_memory(f"Event plugin {plugin.__name__} error: {e}",
                                      topic="plugin", trust="low")
        if recent_entries:
            last_seen_timestamp = recent_entries[-1].get("timestamp")
        time.sleep(30)


# -----------------------------------------------------------------------------
# Main control functions
# -----------------------------------------------------------------------------
def start_plugins():
    config = load_config()
    sandbox_enabled = config.get("plugin_sandbox_enabled", False)

    plugins = load_plugins()
    for plugin in plugins:
        trigger = getattr(plugin, "TRIGGER", {})
        ttype = trigger.get("type")
        interval = trigger.get("interval", 300)

        if ttype == "scheduled":

            t = threading.Thread(
                target=scheduled_runner,
                args=(plugin, interval, sandbox_enabled),
                daemon=True,
            )
            t.start()
            log_tagged_memory(
                f"Started scheduled plugin {plugin.__name__}", topic="plugin", trust="high"
            )
        elif ttype == "passive":
            try:
                if sandbox_enabled:
                    run_in_sandbox(plugin.__file__, env_vars={}, work_dir=str(PLUGINS_DIR), wait=False)
                else:
                    plugin.run()
                log_tagged_memory(
                    f"Started passive plugin {plugin.__name__}", topic="plugin", trust="high"
                )
            except Exception as e:
                log_tagged_memory(
                    f"Passive plugin {plugin.__name__} error: {e}", topic="plugin", trust="low"
                )
        elif ttype == "event":
            match_dict = trigger.get("match", {})
            t = threading.Thread(target=event_watcher, args=(plugin, match_dict), daemon=True)
            t.start()
            log_tagged_memory(
                f"Started event plugin {plugin.__name__} (watching for match: {match_dict})",
                topic="plugin",
                trust="high",
            )


def run_plugins_by_trigger(trigger_name):
    for plugin in load_plugins():
        if plugin.__name__ == trigger_name:
            try:
                plugin.run()
                print(f"[⚡] Triggered plugin: {trigger_name}")
            except Exception as e:
                print(f"[!] Plugin {trigger_name} failed: {e}")


# -----------------------------------------------------------------------------
# Replication helper
# -----------------------------------------------------------------------------
def receive_and_write_plugin(filename, data_b64, signature):
    try:
        from crypto import load_keys
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        code_bytes = base64.b64decode(data_b64)
        _, pub = load_keys()
        pub_key = Ed25519PublicKey.from_public_bytes(
            pub.public_bytes(encoding=serialization.Encoding.Raw,
                             format=serialization.PublicFormat.Raw)
        )

        pub_key.verify(base64.b64decode(signature), code_bytes)  # raises if invalid

        path = PLUGINS_DIR / filename
        path.write_text(code_bytes.decode("utf-8"), encoding="utf-8")

        log_tagged_memory(f"Verified and saved plugin: {filename}", topic="plugin", trust="high")
        log_tagged_memory(f"Plugin {filename} imported via replication",
                          topic="fitness", trust="neutral")

        if "GENOME:" not in code_bytes.decode("utf-8"):
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n# GENOME: source=replicated; origin={filename}\n")

        return True
    except Exception as e:
        log_tagged_memory(f"Plugin verification failed: {e}", topic="plugin", trust="low")
        return False


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    start_plugins()
    while True:
        time.sleep(60)
