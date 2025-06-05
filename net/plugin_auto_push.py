import base64
import os
import grpc
from proto import sync_pb2, sync_pb2_grpc
from crypto import load_keys

def push_plugin_to_peer(plugin_path, target_ip):
    priv_key, _ = load_keys()
    with open(plugin_path, "rb") as f:
        plugin_bytes = f.read()
    plugin_push = sync_pb2.PluginPush(
        filename=os.path.basename(plugin_path),
        data_b64=base64.b64encode(plugin_bytes).decode("utf-8"),
        signature=priv_key.sign(plugin_bytes)
    )

    with grpc.insecure_channel(f"{target_ip}:50051") as channel:
        stub = sync_pb2_grpc.AriaPeerStub(channel)
        request = sync_pb2.SyncMemoryRequest(
            sender_id="plugin_push",
            encrypted_memory=b"",
            signature=b"plugin",
            current_cycle_id="0",
            active_plugins=[],
            plugin_push=plugin_push
        )
        response = stub.SyncMemory(request)
        print("[📡] Plugin pushed:", response.message)
