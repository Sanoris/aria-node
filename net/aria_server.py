import grpc
from concurrent import futures
from proto import sync_pb2, sync_pb2_grpc
from crypto import load_keys
from cryptography.hazmat.primitives import serialization

class AriaPeerServicer(sync_pb2_grpc.AriaPeerServicer):
    def PerformHandshake(self, request, context):
        print("[🤝] Received handshake request.")
        _, pub = load_keys()
        pub_bytes = pub.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        return sync_pb2.HandshakeResponse(peer_public_key=pub_bytes)


    def SyncMemory(self, request, context):
        print(f"[📨] SyncMemory called by: {request.sender_id}")
        return sync_pb2.SyncMemoryResponse(
            message="Memory sync accepted.",
            peer_cycle_id="42",
            active_plugins=["plugin_dashboard_sync"]
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sync_pb2_grpc.add_AriaPeerServicer_to_server(AriaPeerServicer(), server)
    server.add_insecure_port("[::]:50051")
    print("[+] Aria peer sync server running on port 50051.")
    server.start()
    server.wait_for_termination()