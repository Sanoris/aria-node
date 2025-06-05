# Memory Sync Quickref

This short guide outlines the minimal steps to synchronize memory between Aria nodes.

## 1. Tag memory events

Use `memory/tagger.py` to record events you want to share:

```python
from memory.tagger import log_tagged_memory

log_tagged_memory("Peer handshake succeeded", topic="peer", trust="neutral")
```

Entries are stored in `memory/log.txt`.

## 2. Start the background sync loop

`node.py` defines `background_sync()` which periodically sends recent logs to a peer via gRPC:

```python
from node import background_sync

background_sync()
```

## 3. gRPC request

`net/peer_client.py` builds and sends the sync request as defined in `proto/sync.proto`:

```python
sync_with_peer(peer_address, payload)
```

The payload contains the encrypted memory blob, the current cycle ID, active plugins, and a signature.

## 4. Review synced memory

Received entries are merged into the local log. Inspect `memory/log.txt` or use the tagger utilities to view synced events.

---

For more details on the synchronization protocol see [Memory Sync Architecture](grpc_sync.md).
