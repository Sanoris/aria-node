import grpc
import sys, os, yaml, socket
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'proto'))
from crypto.crypto_utils import encrypt_message, load_key_from_file
from crypto.identity import sign_message
import proto.sync_pb2 as sync_pb2
import proto.sync_pb2_grpc as sync_pb2_grpc

CONFIG_PATH = "config.yaml"

def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_node_id(cfg):
    node_id = cfg.get("node_id")
    if not node_id:
        hostname = socket.gethostname()
        node_id = f"aria-{hostname}"
    return node_id

def secure_sync_with_peer(target_ip, target_port=50051):
    cfg = load_config()
    node_id = get_node_id(cfg)
    key = load_key_from_file()
    with open("memory/log.txt", "r", encoding="utf-8") as f:
        mem_data = f.read().encode()
    encrypted = encrypt_message(key, mem_data)
    signature = sign_message(mem_data)

    with grpc.insecure_channel(f"{target_ip}:{target_port}") as channel:
        stub = sync_pb2_grpc.AriaPeerStub(channel)
        packet = sync_pb2.MemoryPacket(
            sender_id=node_id,
            encrypted_memory=encrypted,
            signature=signature
        )
        response = stub.SyncMemory(packet)
        print("[+] Sync result:", response.message)

if __name__ == "__main__":
    target = input("Peer IP: ")
    secure_sync_with_peer(target)
