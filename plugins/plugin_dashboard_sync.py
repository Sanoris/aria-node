import socket
import time
import hashlib
import grpc
from datetime import datetime
from memory.tagger import get_recent_memory, log_tagged_memory
from crypto import load_keys
from proto import sync_pb2, sync_pb2_grpc
from net.dashboard_sync import discover_dashboard_url
from cryptography.hazmat.primitives import serialization
from net.peer_client import load_active_plugins, load_peers, perform_handshake_with_peer, sanitize_peer_address, sync_with_peer
import json

TRIGGER = {
    "type": "scheduled",
    "interval": 30  # seconds
}

def run():
    try:
        
        memory_entries = get_recent_memory(limit=555)
        serialized = [json.dumps(e).encode("utf-8") for e in memory_entries]
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
        target = sanitize_peer_address(dashboard_url)
        sync_with_peer(target, serialized)

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