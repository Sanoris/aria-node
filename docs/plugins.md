# Plugin Documentation

## `plugin_arp_watcher.py`

Monitors ARP traffic to detect new devices and log them in a catalog.

Passively captures network packets, which may reveal device information
without consent.

**Trigger:**
```json
{
  "type": "passive"
}
```

---

## `plugin_auto_vote.py`

Automatically votes on proposals found in recent memory entries.

Simple heuristics may cast incorrect votes, influencing swarm decisions
without human oversight.

**Trigger:**
```json
{
  "type": "event",
  "match": {
    "AAAAAAAAAAAAA": "AAAAAAAAAAAAA"
  }
}
```

---

## `plugin_dashboard_autopromote.py`

Promotes this node to dashboard role if no dashboard is found.

Starts web servers like Nginx and Uvicorn to host the dashboard.
Running network services may expose the node or consume resources.

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

Steps down from dashboard role when another dashboard is detected.

Stops Nginx and Uvicorn when relinquishing role. If misfired, it could
shut down the local dashboard unexpectedly.

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

Synchronizes memory with the elected dashboard over gRPC.

Periodically sends local memory state to the dashboard. Can leak
sensitive data over the network and increases bandwidth usage.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 30
}
```

---

## `plugin_genealogist.py`

Reports lineage information for evolved plugins by reading genome headers.

Useful for tracing plugin origins but may reveal details about mutations
or source nodes if leaked.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 900
}
```

---

## `plugin_genetic_evolver.py`

Evolves existing plugins by randomly or LLM-assisted mutations.

Creates new `plugin_evolved_*.py` files from crossover and mutation of
other plugins. May execute arbitrary generated code, so use with care.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 900
}
```

---

## `plugin_inference_latency.py`

Logs average inference latency from recent inference worker statistics.

Helps detect slowdown but continuously reading stats may affect
performance slightly.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 120
}
```

---

## `plugin_inference_monitor.py`

Monitors the inference queue size and logs warnings when backlog grows.

May generate many log entries under heavy load, filling memory quickly.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 60
}
```

---

## `plugin_instincts.py`

Executes instinctive behaviors based on recent memory patterns.

Can trigger scanning or replication plugins automatically, which may be
intrusive or resource intensive.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_lan_scanner.py`

Scans the local network for peers and open ports, updating host catalog.

Useful for discovery but aggressive scanning could alert network monitors
or violate policies.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_llm_auto_vote.py`

Uses an LLM to automatically vote on recent swarm decisions.

LLM responses may be unpredictable and could endorse malicious actions
if prompts are manipulated.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 120
}
```

---

## `plugin_llm_scheduler.py`

Asks an LLM to recommend scheduling or disabling plugins.

Relies on AI judgments which may be poor or biased, potentially causing
harmful plugin behavior changes.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_memory_interpreter.py`

Uses an LLM to summarize recent memory and provide swarm insights.

Could leak private data via prompts and may misinterpret context,
leading to misleading analysis.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 30
}
```

---

## `plugin_peer_quarantine.py`

Removes peers from the catalog that repeatedly fail handshakes.

Helps prune unreachable nodes but might accidentally quarantine healthy
peers if network issues are temporary.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 600
}
```

---

## `plugin_pruner.py`

Deletes evolved plugins that show poor performance or inactivity.

Helps control plugin sprawl but could remove useful plugins if criteria
are too aggressive.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 600
}
```

---

## `plugin_replicator.py`

Replicates the newest evolved plugin to a random online peer.

Facilitates code propagation across the swarm. Can spread malicious or
unstable plugins if not carefully monitored.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_smb_replicator.py`

Copies the node executable to writable SMB or removable drives.

Enables spreading to Windows shares and may hide the payload. This is
overt malware-like behavior and is high risk.

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

Updates the nginx proxy configuration when a new dashboard is elected.

Reads memory logs to find the latest dashboard IP and rewrites config.
Improper configuration could break access or expose the node.

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

## `plugin_vote_aggregator.py`

Aggregates swarm votes from memory and logs a summary.

Purely informational but could be misleading if memory contains spam or
manipulated votes.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_vote_promoter.py`

Publishes vote summaries and promotes approved actions.

Can inadvertently promote malicious proposals if vote data is tampered.

**Trigger:**
```json
{
  "type": "scheduled",
  "interval": 300
}
```

---

## `plugin_ws_sadl_sniffer.py`

Intercepts WebSocket traffic using NFQUEUE or scapy and logs packets.

Can capture sensitive data and requires elevated privileges on Linux.

**Trigger:**
```json
{
  "type": "manual"
}
```

---

