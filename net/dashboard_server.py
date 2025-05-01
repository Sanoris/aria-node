import grpc
import threading
import json
from pathlib import Path
from concurrent import futures
from datetime import datetime
from proto import sync_pb2, sync_pb2_grpc

log_path = Path("./aria_dashboard/peer_logs.json")

class AriaPeerServicer(sync_pb2_grpc.AriaPeerServicer):
    def SendToDashboard(self, request, context):
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)

        new_logs = []
        for entry in request.entries:
            new_logs.append({
                "timestamp": entry.timestamp or datetime.now().isoformat(),
                "msg": entry.msg,
                "topic": entry.topic
            })

        try:
            with open(log_path, "r+") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = {}
                existing.setdefault(request.sender_id, []).extend(new_logs)
                f.seek(0)
                json.dump(existing, f, indent=2)
                f.truncate()
        except Exception as e:
            print(f"[⚠️] Failed to write logs from {request.sender_id}: {e}")

        return sync_pb2.DashboardSyncResponse(message="Dashboard received sync.")

    def ShareMemory(self, request, context):
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)

        memory_by_sender = {"shared": []}

        for entry_json in request.entries:
            try:
                entry = json.loads(entry_json)
                memory_by_sender["shared"].append(entry)
            except Exception as e:
                print("[❌] Failed to parse shared memory entry:", e)

        try:
            with open(log_path, "r+") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = {}
                for sender, entries in memory_by_sender.items():
                    existing.setdefault(sender, []).extend(entries)
                f.seek(0)
                json.dump(existing, f, indent=2)
                f.truncate()
        except Exception as e:
            print("[💥] Failed to store shared memory:", e)

        return sync_pb2.MemorySyncResponse(status="ok")

def serve_grpc(port=8000):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sync_pb2_grpc.add_AriaPeerServicer_to_server(AriaPeerServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    print(f"[✅] gRPC dashboard server listening on port {port}")
    server.start()
    threading.Thread(target=server.wait_for_termination, daemon=True).start()