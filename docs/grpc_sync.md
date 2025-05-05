# Memory Syncing in Aria-node

Aria-node performs encrypted peer-to-peer memory synchronization using gRPC, trust scoring, and plugin-aware payloads.

---

## 🔄 Overview

Each node maintains a local memory log (`memory/log.txt`) which records tagged, timestamped events. These memory logs are:

- Created using `memory/tagger.py`
- Periodically pushed to a selected peer using gRPC (`peer_client.py`)
- Merged into local context by the receiving peer

This enables decentralized swarm cognition.

---

## 🧠 Memory Logging

Module: `memory/tagger.py`

```python
log_tagged_memory("Peer handshake succeeded", topic="peer", trust="neutral")
```

Each entry looks like:

```json
{
  "timestamp": 1714925324.154,
  "topic": "peer",
  "trust": "neutral",
  "content": "Peer handshake succeeded"
}
```

Tagged logs support filtering, decay, and trust-aware pruning.

---

## 🔁 Periodic Sync Loop

Defined in `node.py → background_sync()`

```python
def background_sync():
    while True:
        SYNC_PEERS = load_peers()
        entries = get_recent_memory(limit=20)
        payload = json.dumps(entries).encode("utf-8")
        sync_with_peer(random.choice(SYNC_PEERS).strip(), payload)
```

The node selects a peer and sends the latest memory entries via gRPC every cycle.

---

## 📡 gRPC Request Payload

Defined in `proto/sync.proto` and sent via `peer_client.py`:

```python
request = sync_pb2.SyncMemoryRequest(
    sender_id=sender_id,
    encrypted_memory=encrypted_memory,
    signature=b"sync",
    current_cycle_id="42",
    active_plugins=active_plugins
)
```

Payload includes:

- `sender_id` – public key hash
- `encrypted_memory` – encrypted blob from memory logs
- `active_plugins` – plugin list
- `current_cycle_id` – sync round
- `signature` – shared swarm identity proof

---

## 🧠 Trust + Validation

From `peer_client.py`:

```python
if not analyze_peer_plugins(response.active_plugins):
    log_tagged_memory(
        f"Peer {peer_address} plugins failed trust validation. Ignoring sync.",
        topic="peer",
        trust="low"
    )
    return
```

Each peer validates plugin lists before accepting memory.

---

## 🛠 File Map

| File | Purpose |
|------|---------|
| `memory/tagger.py` | Tags, stores, and retrieves memory logs |
| `node.py` | Background sync scheduler |
| `net/peer_client.py` | Performs sync with peer |
| `proto/sync.proto` | gRPC protocol for memory requests |
| `trust/manager.py` | Peer trust & sync filtering (optional) |

---

## 🔐 Security Notes

- Payloads encrypted with `crypto/peer_keys.py`
- Signed with local identity key
- Trust validation may reject memory from unknown/untrusted peers

---

## 📈 Future Ideas

- Differential sync (skip unchanged)
- Tag-based selective sync (e.g. only "network" logs)
- Cross-node memory index federation
