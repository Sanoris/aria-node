import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from net.dashboard_server import serve_grpc
from datetime import datetime
import json
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI()
log_path = Path("./aria_dashboard/peer_logs.json")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PluginCommand(BaseModel):
    node: str
    plugin: str
    action: str

class SyncEntry(BaseModel):
    timestamp: str
    msg: str
    topic: str

class PeerSync(BaseModel):
    ip: str
    entries: list[SyncEntry]


@app.get("/peers", response_class=HTMLResponse)
def get_peers():
    with open(log_path, "r") as f:
        data = json.load(f)
    html = ""
    for peer in data.keys():
        html += f'<button class="block mb-1 hover:text-white" hx-get="/logs/{peer}" hx-target="#log-panel">{peer}</button>'
    return html

@app.get("/logs/{node}", response_class=HTMLResponse)
def get_logs(node: str):
    with open(log_path, "r") as f:
        data = json.load(f)
    logs = data.get(node, [])
    html = f"<h3 class='text-lg mb-2'>Logs for {node}</h3><ul class='list-disc ml-4'>"
    for entry in logs:
        html += f"<li><b>{entry['timestamp']}</b>: {entry['msg']} <i class='text-xs'>[{entry['topic']}]</i></li>"
    html += "</ul>"

    # plugin trigger form
    plugin_options = ""
    for plugin_file in Path("../plugins").glob("plugin_*.py"):
        plugin_name = plugin_file.stem
        plugin_options += f'<option value="{plugin_name}">{plugin_name}</option>'

    html += f'''
    <form hx-post="/trigger" hx-include="this" class="mt-4">
        <input type="hidden" name="node" value="{node}">
        <label for="plugin" class="block text-sm mb-1">Run plugin:</label>
        <select name="plugin" class="text-black p-1 rounded">
            {plugin_options}
        </select>
        <input type="hidden" name="action" value="run_now">
        <button type="submit" class="ml-2 border px-2 py-1 hover:bg-green-700">Trigger</button>
    </form>
    '''
    return html

@app.post("/trigger")
async def trigger_plugin(request: Request):
    data = await request.form()
    node = data["node"]
    plugin = data["plugin"]
    action = data["action"]

    log_path.touch(exist_ok=True)
    with open(log_path, "r+") as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError:
            existing = {}
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "msg": f"Dashboard triggered {plugin} ({action})",
            "topic": "control"
        }
        existing.setdefault(node, []).append(log_entry)
        f.seek(0)
        json.dump(existing, f, indent=2)
        f.truncate()
    return {"status": "sent", "node": node, "plugin": plugin}

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


app.mount("/", StaticFiles(directory="./aria_dashboard/aria_dashboard_frontend", html=True), name="frontend")

if __name__ == "__main__":
    # Start gRPC server in a separate thread
    import threading
    grpc_thread = threading.Thread(target=serve_grpc, daemon=True)
    grpc_thread.start()
    print("[*] dashboard gRPC server started.")

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8001)