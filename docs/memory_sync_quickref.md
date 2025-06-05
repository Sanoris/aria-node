# 📝 Memory Sync Quick Reference

This guide provides the essential commands and file locations used by Aria-node's memory synchronization features. For a more detailed explanation see [Memory Sync Architecture](grpc_sync.md).

---

## 💾 Logging Memory Entries

Use `memory/tagger.py` to write timestamped events to `memory/log.txt`:

```python
from memory.tagger import log_tagged_memory

log_tagged_memory("Peer handshake succeeded", topic="peer", trust="neutral")
```

Entries are stored in JSON format and can be inspected directly in `memory/log.txt`.

---

## 🔁 Manual Sync With a Peer

You can push recent memory entries to another node using `net/peer_client.py`:

```bash
python net/peer_client.py --peer <peer_address> --push --limit 20
```

This sends the last 20 log entries over gRPC to the specified peer.

---

## 🛠 Key Files

| File | Purpose |
|------|---------|
| `memory/tagger.py` | Create and retrieve memory logs |
| `net/peer_client.py` | Perform gRPC sync with peers |
| `proto/sync.proto` | gRPC request/response definitions |

These components work together to keep nodes in sync.

