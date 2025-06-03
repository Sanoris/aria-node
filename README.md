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

---

## Getting Started

```bash
git clone https://github.com/yourname/aria-node.git
cd aria-node
pip install -r requirements.txt
python node.py
```

## Compiling Proto Definitions

```bash
python -m grpc_tools.protoc -I./proto --python_out=./proto --grpc_python_out=./proto ./proto/sync.proto
```

---

## Documentation

- [Plugin Trigger Engine](docs/plugin_trigger_engine_usage.md)
- [Plugin Development](docs/plugins.md)
- [Memory Sync Architecture](docs/grpc_sync.md)
- [Swarm Manifest Ledger](docs/manifest_ledger.md)
- [Memory Sync Quickref](docs/memory_sync_quickref.md)

---

## Disclaimer

Aria-node is an experimental platform intended for research and prototyping.
It is not a production system and carries inherent risks as an evolving distributed framework.
