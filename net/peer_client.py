import grpc
import time
import json
import sys, os
import hashlib
import re
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from proto import sync_pb2, sync_pb2_grpc
from crypto.peer_keys import save_peer_public_key, load_peer_public_key
from crypto import load_key_from_file, encrypt_message, load_keys
from cryptography.hazmat.primitives import serialization
from memory.tagger import log_tagged_memory
from trust.manager import initialize_peer_trust
from plugins.analysis import analyze_peer_plugins

CURRENT_CYCLE_ID = 42

def load_active_plugins(directory="plugins"):
    try:
        return [f.split(".")[0] for f in os.listdir(directory) if f.endswith(".py")]
    except FileNotFoundError:
        return []

def load_peers(catalog_path="host_catalog.json"):
    try:
        with open(catalog_path, "r") as f:
            hosts = json.load(f)
        return [h["ip"] + ":50051" for h in hosts if "ip" in h]
    except FileNotFoundError:
        return []

def perform_handshake_with_peer(peer_address):
    try:
        with grpc.insecure_channel(peer_address) as channel:
            stub = sync_pb2_grpc.AriaPeerStub(channel)

            priv_key, pub_key = load_keys()
            temp_key = pub_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            handshake_request = sync_pb2.HandshakeRequest(sender_public_key=temp_key)
            handshake_response = stub.PerformHandshake(handshake_request)

            peer_public_key = handshake_response.peer_public_key
            save_peer_public_key(peer_address, peer_public_key)
            log_tagged_memory(
                f"Handshake complete with new peer: {peer_address}",
                topic="peer",
                trust="neutral"
            )
            initialize_peer_trust(peer_address)
            return peer_public_key  # ✅ fixed: return the peer's key
    except grpc.RpcError as e:
        print(f"[Handshake Error] Failed to perform handshake with {peer_address}: {e}")
        log_tagged_memory(f"Handshake failed with peer: {peer_address}", topic="peer", trust="low")
        return False

def sanitize_peer_address(peer_address):
    return re.sub(r'[^a-zA-Z0-9_.-]', '_', peer_address)

def sync_with_peer(peer_address, memory_payload=b"", signature=b"sync"):
    from .sync_scheduler import update_status
    try:
        peer_public_key = load_peer_public_key(peer_address)
        if not peer_public_key:
            print(f"[Sync] No public key found for {peer_address}. Initiating handshake...")
            if not perform_handshake_with_peer(peer_address):
                update_status(peer_address, success=False)
                return

        with grpc.insecure_channel(peer_address) as channel:
            stub = sync_pb2_grpc.AriaPeerStub(channel)
            shared_key = load_key_from_file()
            encrypted_memory = encrypt_message(shared_key, memory_payload) if memory_payload else b""

            priv_key, pub_key = load_keys()
            sender_id = hashlib.sha256(pub_key.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )).hexdigest()[:12]

            active_plugins = load_active_plugins()

            request = sync_pb2.SyncMemoryRequest(
                sender_id=sender_id,
                encrypted_memory=encrypted_memory,
                signature=signature,
                current_cycle_id=str(CURRENT_CYCLE_ID),
                active_plugins=active_plugins
            )
            response = stub.SyncMemory(request)

            print(f"[Sync] Peer: {peer_address}, Response: {response.message}, Peer Cycle: {response.peer_cycle_id}")

            # ✅ Plugin validation (if active_plugins returned)
            if hasattr(response, "active_plugins"):
                if not analyze_peer_plugins(response.active_plugins):
                    log_tagged_memory(
                        f"Peer {peer_address} plugins failed trust validation. Ignoring sync.",
                        topic="peer",
                        trust="low"
                    )
                    return

            if response.peer_cycle_id != str(CURRENT_CYCLE_ID):
                print(f"[Sync] Cycle mismatch with {peer_address}, triggering data sync...")
                full_sync_payload = b"[Full Sync] Cycle alignment data."
                encrypted_full_sync = encrypt_message(shared_key, full_sync_payload)
                full_sync_request = sync_pb2.SyncMemoryRequest(
                    sender_id=sender_id,
                    encrypted_memory=encrypted_full_sync,
                    signature=b"sync",
                    current_cycle_id=str(CURRENT_CYCLE_ID),
                    active_plugins=active_plugins
                )
                full_sync_response = stub.SyncMemory(full_sync_request)
                print(f"[Full Sync] Sent to {peer_address}, Response: {full_sync_response.message}")
            update_status(peer_address, success=True)
    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.UNAVAILABLE:
            print(f"[!] Peer {peer_address} unavailable (connection refused). Skipping.")
            update_status(peer_address, success=False)
        else:
            print(f"[Error] Sync failed with {peer_address}: {e}")
            update_status(peer_address, success=False)

if __name__ == "__main__":
    from sync_scheduler import run_scheduler
    from net.aria_server import serve

    import threading
    threading.Thread(target=serve, daemon=True).start()
    run_scheduler()
    while True:
        time.sleep(3600)