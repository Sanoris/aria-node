# ✅ aria-node TODO.md

This is the prioritized task list to stabilize and evolve the `aria-node` system.
Each section lists the file(s) involved and what's needed.

---

## 🔧 1. Fix Plugin Sync Mechanism

- [ ]  **Add** `string signature = 3;` to `PluginPush` in `sync.proto`
- [ ]  Regenerate `sync_pb2.py` after proto change
- [ ]  **Patch** `aria_server.py → SyncMemory()` to pass plugin signature into `receive_and_write_plugin()`
- [ ]  **Clean up** legacy usage of `MemoryPacket` in `plugin_auto_push.py`

---

## 🔒 2. Unify Log Format Readers

- [ ]  **Refactor** `decay.py` to parse `log.txt` as JSON, not old tag format
- [ ]  **Update** `swarm_vote.py` if present, to do JSON-based vote tallying
- [ ]  Ensure `tagger.py` log writes are consistent with all readers

---

## 🧠 3. Standardize Trust & Vote Logic

- [ ]  **Fix** `plugin_llm_auto_vote.py` to import `endorse_peer` from `endorsement_chain.py`
- [ ]  Provide required args: `(target_peer_id, endorser_id, score, reason)`
- [ ]  Decide: stick with `swarm_vote` or adopt `request_vote()` in future voting plugins
- [ ]  Begin calling `update_trust()` where applicable (e.g., plugin outcomes)

---

## 📁 4. Update Documentation

- [ ]  Run `scripts/genDocs.py` to regenerate `docs/plugins.md`
- [ ]  Add plugin replication explanation to `grpc_sync.md`
- [ ]  Fix/remove broken `docs/memory_sync_quickref.md` link in `README.md`
- [ ]  Clarify if/when to run `protoc` in README

---

## 🚀 5. Improve Plugin Consistency Checks

- [x]  Add logic to `plugin_trigger_engine.py`:
  - [x]  Warn if `run()` missing
  - [x]  Warn if malformed `TRIGGER`
- [x]  Print/log quarantine messages clearly

---

## 🧪 6. Test Swarm Cycle

- [ ]  Start 2+ nodes
- [ ]  Confirm:
  - [ ]  Plugin push works (with signed plugin)
  - [ ]  Event plugins auto-trigger
  - [ ]  Bad plugins get tagged by `plugin_instincts.py`
  - [ ]  `plugin_pruner.py` removes failing ones
- [ ]  Watch logs for unexpected errors or dropped memory

---

## 🎨 7. Polish README and UX

- [ ]  Add system diagram or visual to `README.md`
- [ ]  Clarify role of `node.py`, plugin architecture
- [ ]  Add usage examples: plugin dev, swarm connection, peer sync
- [ ]  Mention dashboard port + purpose explicitly
