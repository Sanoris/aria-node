# net

**DISCLAIMER: The networking utilities in this directory include code that enables unauthorized deployment behavior. They are provided strictly for research use only.**

This directory forms the networking backbone of Aria-node. It includes peer synchronization, plugin propagation, dashboard transmission, swarm coordination, and payload deployment.

### Components

- **Peer Communication**
  - `peer_client.py`, `aria_server.py`: Perform gRPC handshake, sync memory, transmit encrypted plugins.
  - `dashboard_server.py`, `dashboard_sync.py`: Dashboard receivers and sync logic for memory broadcast.

- **Leadership & Manifest**
  - `dynamic_leader.py`: Chooses leader node via last seen activity.
  - `fork_guard.py`: Detects peer divergence.

- **Propagation & Sync**
  - `encrypted_plugin_sync.py`: Accepts encrypted plugin uploads if sender is trusted.
  - `plugin_receiver.py`, `plugin_trigger_engine.py`: Load and execute synced plugins.

- **Capability & Behavior Mapping**
  - `heuristics.py`: Assigns seed priority score to hosts.
  - `capability_profiler.py`: Aggregates plugin usage stats.

- **Autonomous Deployment**
  - `host_infiltrator.py`: SMB/FTP-based auto-deployer using ranked hosts from priority scan.

This layer is modular, encrypted, and designed for quiet, resilient expansion across local or global mesh environments.
