import grpc
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'crypto'))

import sync_pb2 as sync_pb2
import sync_pb2_grpc as sync_pb2_grpc
from crypto import load_keys, encrypt_message
from crypto import load_key_from_file

def sync_with_peer(target_ip, target_port=50051):
    priv, pub = load_keys()
    node_id = "aria-node-001"
    shared_key = load_key_from_file()

    with open("memory/log.txt", "r", encoding="utf-8") as f:
        mem_data = f.read().encode()

    encrypted = encrypt_message(shared_key, mem_data)

    with grpc.insecure_channel(f"{target_ip}:{target_port}") as channel:
        stub = sync_pb2_grpc.AriaPeerStub(channel)
        packet = sync_pb2.MemoryPacket(
            sender_id=node_id,
            encrypted_memory=encrypted,
            signature=b"dummy"
        )
        response = stub.SyncMemory(packet)
        print("[+] Sync result:", response.message)

if __name__ == "__main__":
    target = input("Peer IP: ")
    sync_with_peer(target)
