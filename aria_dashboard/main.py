import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from net.dashboard_server import serve_grpc
from datetime import datetime
import json

app = FastAPI()
log_path = Path("./aria_dashboard/peer_logs.json")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"msg": "Aria dashboard running."}

@app.get("/logs")
def get_logs():
    if not log_path.exists():
        return {}
    with open(log_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

@app.post("/sync")
def peer_sync(payload: dict):
    sender_id = payload.get("ip", "unknown")
    entries = payload.get("entries", [])
    new_logs = [
        {
            "timestamp": e.get("timestamp", datetime.now().isoformat()),
            "msg": e.get("msg", "Unknown entry"),
            "topic": e.get("topic", "misc")
        }
        for e in entries
    ]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.touch(exist_ok=True)
    try:
        with open(log_path, "r+") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = {}
            existing.setdefault(sender_id, []).extend(new_logs)
            f.seek(0)
            json.dump(existing, f, indent=2)
            f.truncate()
    except Exception as e:
        print(f"[⚠️] Failed to write logs from {sender_id}: {e}")
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "alive"}

if __name__ == "__main__":
    # Start gRPC listener (non-blocking)
    serve_grpc(port=8000)

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)