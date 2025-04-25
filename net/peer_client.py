import grpc
import time
import json
import sys, os
import hashlib
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from proto import sync_pb2, sync_pb2_grpc
from crypto import load_key_from_file, encrypt_message, load_keys
from cryptography.hazmat.primitives import serialization


CURRENT_CYCLE_ID = 42

def load_active_plugins(directory="plugins"):
    try:
        return [f.split(".")[0] for f in os.listdir(directory) if f.endswith(".py")]
    except FileNotFoundError:
        return []

# Load peers from host catalog
def load_peers(catalog_path="host_catalog.json"):
    try:
        with open(catalog_path, "r") as f:
            hosts = json.load(f)
        return [h["ip"] + ":50051" for h in hosts if "ip" in h]
    except FileNotFoundError:
        return []

def sync_with_peer(peer_address, memory_payload=b"", signature=b"sync"):
    from .sync_scheduler import update_status  # Import status updater
    try:
        with grpc.insecure_channel(peer_address) as channel:
            stub = sync_pb2_grpc.AriaPeerStub(channel)
            shared_key = load_key_from_file()
            encrypted_memory = encrypt_message(shared_key, memory_payload) if memory_payload else b""

            # Generate sender_id from public key fingerprint
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

            # Trigger sync if cycles mismatch
            if response.peer_cycle_id != str(CURRENT_CYCLE_ID):
                print(f"[Sync] Cycle mismatch with {peer_address}, triggering data sync...")
                # Full sync logic: send updated memory payload
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
