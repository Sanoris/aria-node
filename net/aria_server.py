import grpc
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from proto import sync_pb2, sync_pb2_grpc
from crypto import load_keys, decrypt_message
from crypto import load_key_from_file, decrypt_message


class AriaPeerServicer(sync_pb2_grpc.AriaPeerServicer):
    def SyncMemory(self, request, context):
        sender_id = request.sender_id
        encrypted_memory = request.encrypted_memory
        signature = request.signature

        priv, _ = load_keys()
        shared_key = load_key_from_file()
        try:
            decrypted = decrypt_message(shared_key, encrypted_memory)
            with open("memory/log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{sender_id}] {decrypted.decode()}\n")
            return sync_pb2.SyncAck(success=True, message="Memory accepted.")
        except Exception as e:
            return sync_pb2.SyncAck(success=False, message=f"Decryption failed: {str(e)}")

def serve():
    from concurrent import futures
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sync_pb2_grpc.add_AriaPeerServicer_to_server(AriaPeerServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("[+] Aria peer sync server running on port 50051.")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()
