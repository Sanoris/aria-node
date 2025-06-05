# Aria-node: Distributed Autonomous Intelligence Framework

## Overview

**Aria-node** is an experimental framework for building a decentralized, self-evolving network of intelligent nodes.

Each node operates semi-autonomously, leveraging peer-to-peer memory synchronization, trust-weighted decision-making, and adaptive plugin evolution to drive local and swarm-wide behavior.

Aria-node explores new paradigms in distributed AI, emergent consensus, and evolutionary automation.

---

## Core Features

- **Decentralized peer-to-peer architecture** (no central controller)
- **Encrypted memory synchronization** using gRPC
- **Trust-based consensus** for decision-making and plugin validation
- **Plugin trigger engine** supporting scheduled and event-driven execution
- **Adaptive plugin mutation and evolution** with local fitness evaluation
- **Rolling digest memory compression** for low-latency swarm context sharing

### System Diagram

```
                    +-----------+            +-----------+
                    |   Node A  |<--gRPC--->|   Node B  |
                    +-----------+            +-----------+
                          |                         |
                          v                         v
                  [ Plugin Trigger Engine ]   [ Plugin Trigger Engine ]
                          |                         |
                    +-----------+            +-----------+
                    | Plugins   |            | Plugins   |
                    |  (RAM)    |            |  (RAM)    |
                    +-----------+            +-----------+
                          |
                          v
                     +-----------+
                     | Dashboard |
                     | HTTP 8001 |
                     | gRPC 8000 |
                     +-----------+
```

---

## Architecture Principles

- **Local autonomy:** Nodes act independently, consulting trusted peers when needed
- **Trust-weighted growth:** Trust scores control knowledge flow and plugin propagation
- **Memory hygiene:** Only high-trust experiences are retained; irrelevant data decays
- **Evolutionary dynamics:** Useful behaviors spread; weak behaviors are pruned

---

## Development Stage

- Active research project — early-stage architecture
- Initial swarm protocols, trust systems, and plugin engine implemented
- Ongoing work: distributed task assignment, advanced plugin evolution, scalable trust networks

## Node & Plugin Architecture

`node.py` is the entry point for a node. It launches the gRPC server, starts the
plugin trigger engine and handles background tasks such as memory decay,
periodic peer sync and network infiltration.  Plugins live in the `plugins/`
directory and are loaded directly from memory by the trigger engine.

A minimal plugin looks like:

```python
TRIGGER = {"type": "scheduled", "interval": 60}

def run():
    print("hello from plugin")
```

The trigger engine watches for scheduled and event-based triggers, executing
plugins without writing them to disk.

---

## Getting Started

```bash
git clone https://github.com/yourname/aria-node.git
cd aria-node
pip install -r requirements.txt
python node.py
```

### Usage Examples

- **Develop a plugin**

  Create `plugins/hello.py`:
  ```python
  TRIGGER = {"type": "scheduled", "interval": 30}

  def run():
      print("hello world")
  ```

  The node will auto-load it from memory at runtime.

- **Connect to peers**

  Edit `config.yaml` and add IPs under `sync_peers:`. On startup the node
  will attempt gRPC sync on port `50051` with those peers.

- **Manual peer sync**

  ```bash
  python net/peer_client.py 10.0.0.5:50051
  ```

  This performs a one-off memory push to a peer.

## Dashboard

The project includes a lightweight dashboard for visualizing peer logs and
plugin activity.  By default the dashboard exposes:

- **HTTP interface:** `http://<node-ip>:8001`
- **gRPC endpoint:** `:<node-ip>:8000`

Nodes can promote themselves to dashboard role automatically via the provided
plugins. Accessing `http://localhost:8001` will show the current peer status
and log summary.

## Compiling Proto Definitions

```bash
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/sync.proto
```

---

## Documentation

- [Plugin Trigger Engine](docs/plugin_trigger_engine_usage.md)
- [Plugin Development](docs/plugins.md)
- [Memory Sync Architecture](docs/grpc_sync.md)
- [Memory Sync Quickref](docs/memory_sync_quickref.md)

---

## Disclaimer

Aria-node is an experimental platform intended for research and prototyping.
It is not a production system and carries inherent risks as an evolving distributed framework.
