# Swarm Manifest Ledger

This document describes how the plugin ledger maintains a directed acyclic graph (DAG) of plugin ancestry. Each plugin is identified by the SHA256 hash of its source code. Entries are stored in `memory/plugin_ledger.json`.

## Entry Format
```json
{
  "plugin_hash": "<sha256>",
  "parent_hash": "<sha256 or null>",
  "lineage_map": {},
  "label": "optional human label",
  "timestamp": 1710000000.0
}
```

## Usage
Plugins register themselves via `net.plugin_ledger.register_plugin(code, parent_hash)`.
The resulting ledger represents evolutionary history without requiring global consensus.
