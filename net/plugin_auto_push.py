import base64
import os
import grpc
import sync_pb2 as sync_pb2
import sync_pb2_grpc as sync_pb2_grpc

def push_plugin_to_peer(plugin_path, target_ip, key_b64):
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key = base64.b64decode(key_b64)
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    with open(plugin_path, "r", encoding="utf-8") as f:
        raw = f.read().encode()
    encrypted = nonce + aesgcm.encrypt(nonce, raw, None)

    with grpc.insecure_channel(f"{target_ip}:50051") as channel:
        stub = sync_pb2_grpc.AriaPeerStub(channel)
        plugin_push = sync_pb2.PluginPush(
            filename=os.path.basename(plugin_path),
            data_b64=base64.b64encode(raw).decode("utf-8"),
            signature=""
        )
        request = sync_pb2.SyncMemoryRequest(
            sender_id="plugin_push",
            encrypted_memory=encrypted,
            signature=b"plugin",
            plugin_push=plugin_push
        )
        response = stub.SyncMemory(request)
        print("[📡] Plugin pushed:", response.message)
