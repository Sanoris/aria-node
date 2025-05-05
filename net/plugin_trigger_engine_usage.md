# 🧠 Aria Plugin Trigger Engine — Usage & Capabilities Overview

## 🔄 Supported Trigger Types

Plugins are activated based on a `TRIGGER` dictionary defined in each plugin module:

```python
TRIGGER = {
    "type": "scheduled" | "event" | "passive",
    ...
}
```

---

### 1. **Scheduled Plugins**
- **Field:** `"type": "scheduled"` with `"interval": <seconds>`
- **Behavior:** Executes repeatedly on a set timer.
- **Example Usage:** Telemetry reporting, LAN scans, scheduled syncs.

**Handled by:**
```python
scheduled_runner(plugin, interval)
```

---

### 2. **Event-Based Plugins**
- **Field:** `"type": "event"`, with `"match": {key: value}`
- **Behavior:** Watches the memory log for any entry where key-values match the `match` dict.
- **Example Usage:** Reacting to peer joining, changes in swarm role, network detection.

**Handled by:**
```python
event_watcher(plugin, match_dict)
```

Event matching uses:
```python
def entry_matches(entry, match_dict)
```
which checks that all key-value pairs match either in:
- the outer entry, or
- `entry["content"]` if present.

---

### 3. **Passive Plugins**
- **Field:** `"type": "passive"`
- **Behavior:** Executes once immediately at boot (usually runs its own loop).
- **Example Usage:** Background sniffers, passive ARP listeners.

---

## 🧬 Dynamic Loading & Execution

Plugins are dynamically loaded from `plugins/` using `importlib`. Each plugin must define a `run()` function and may optionally define a `TRIGGER`.

```python
plugins = load_plugins()
```

### Safety:
Each plugin execution is wrapped in `try/except` and logs to memory with `log_tagged_memory()`.

---

## 📡 Memory Matching

- `get_recent_memory(limit=10)` fetches the latest memory entries to scan for event matches.
- Plugin is triggered if any recent entry matches the specified trigger condition.

---

## ✅ Manual Trigger Support

The engine can also manually invoke a plugin by name:

```python
run_plugins_by_trigger("plugin_name")
```

---

## 📓 Plugin Author Guide

To define a plugin:

```python
TRIGGER = {
    "type": "event",
    "match": {
        "topic": "role",
        "role": "dashboard"
    }
}

def run():
    # do stuff
```