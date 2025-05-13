# plugins

This directory contains the modular plugin system for Aria-node. Each file defines an autonomous unit of functionality, triggered either on a schedule, passively via listeners, or through specific event matching. The plugin system supports self-evolution, network awareness, swarm governance, and inference monitoring.

### Categories

- **Network + Sync**
  - ARP scanning, memory sync with dashboards, dynamic dashboard promotion/retirement.

- **Inference Monitoring**
  - Latency tracking and queue size alerts to inform swarm throttling.

- **Cultural + Genetic Systems**
  - Auto-voting, plugin evolution via crossover/mutation, plugin ancestry logging.

### Evolution Support

Plugins may be evolved via LLM or local mutation. Genome headers are embedded for lineage tracking (`# GENOME:`).

This modular architecture promotes decentralized behavior while enabling organic, swarm-led improvement over time.
