import socket
import time
import hashlib
import grpc
from datetime import datetime
from memory.tagger import get_recent_memory, log_tagged_memory
from crypto import load_keys
from proto import sync_pb2, sync_pb2_grpc
from net.dashboard_sync import discover_dashboard_url

TRIGGER = {
    "type": "scheduled",
    "interval": 300  # seconds
}

def run():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        memory_entries = get_recent_memory(limit=20)

        # Get node ID
        _, pub = load_keys()
        node_id = hashlib.sha256(pub.public_bytes(
            encoding=2,  # serialization.Encoding.Raw
            format=2     # serialization.PublicFormat.Raw
        )).hexdigest()[:12]

        # Discover dashboard
        dashboard_url = discover_dashboard_url()
        if not dashboard_url:
            log_tagged_memory({
                "event": "dashboard_discovery",
                "status": "not_found",
                "timestamp": time.time()
            }, topic="dashboard", trust="neutral")
            return

        # Strip to IP:port for gRPC
        target = dashboard_url.replace("http://", "").replace("/sync", "")
        with grpc.insecure_channel(target) as channel:
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

        log_tagged_memory({
            "event": "dashboard_sync",
            "status": "success",
            "url": dashboard_url,
            "timestamp": time.time()
        }, topic="dashboard", trust="high")

    except Exception as e:
        log_tagged_memory({
            "event": "dashboard_sync",
            "status": "failure",
            "error": str(e),
            "timestamp": time.time()
        }, topic="dashboard", trust="low")