# Plugin Documentation

## `plugin_arp_watcher.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "passive"
}
```

---

## `plugin_dashboard_autopromote.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "event",
  "match": {
    "event": "dashboard_discovery",
    "status": "not_found",
    "knockKnock": "urdead"
  }
}
```

---

## `plugin_dashboard_stepdown.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "event",
  "match": {
    "topic": "role",
    "role": "dashboard"
  }
}
```

---

## `plugin_dashboard_sync.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 30
}
```

---

## `plugin_genetic_evolver.py`

plugin_genetic_evolver.py

---

## `plugin_lan_scanner.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_smb_replicator.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "event",
  "match": {
    "topic": "role",
    "role": "donkeyman"
  }
}
```

---

## `plugin_update_proxy.py`

*No docstring provided.*

**Trigger:**
```json
{
  "type": "event",
  "match": {
    "topic": "role",
    "role": "dashboard"
  }
}
```

---

