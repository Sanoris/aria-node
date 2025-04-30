import os
import grpc
from datetime import datetime
from memory.tagger import get_recent_memory, log_tagged_memory
from proto import sync_pb2, sync_pb2_grpc
from crypto import load_keys
import hashlib
from cryptography.hazmat.primitives import serialization

def discover_dashboard_url():
    override_url = os.getenv("DASHBOARD_URL")
    if override_url:
        return override_url

    candidates = get_recent_memory(topic="role", limit=10)
    for entry in candidates:
        content = entry.get("content", {})
        if content.get("role") == "dashboard":
            ip = content.get("ip")
            port = content.get("port", 8000)
            if not ip:
                continue
            try:
                channel = grpc.insecure_channel(f"{ip}:{port}")
                grpc.channel_ready_future(channel).result(timeout=2)
                return f"{ip}:{port}"
            except Exception:
                continue
    return None

def sync_to_dashboard(ip: str, memory_entries: list):
    try:
        dashboard_address = discover_dashboard_url()
        if not dashboard_address:
            log_tagged_memory("No dashboard found — sync aborted", topic="dashboard", trust="low")
            return

        _, pub = load_keys()
        node_id = hashlib.sha256(pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )).hexdigest()[:12]

        with grpc.insecure_channel(dashboard_address) as channel:
            stub = sync_pb2_grpc.AriaPeerStub(channel)
            stub.SendToDashboard(sync_pb2.DashboardSyncRequest(
                sender_id=node_id,
                entries=[
                    sync_pb2.MemoryEntry(
                        topic=e.get("topic", "misc"),
                        msg=e.get("msg", "Unknown entry"),
                        timestamp=e.get("timestamp", datetime.now().isoformat())
                    ) for e in memory_entries
                ]
            ))
    except Exception as e:
        log_tagged_memory(f"Failed to sync to dashboard: {e}", topic="dashboard", trust="low")