from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from pathlib import Path
from datetime import datetime

app = FastAPI()
log_path = Path("peer_logs.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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

@app.post("/sync")
def sync_logs(sync: PeerSync):
    log_path.touch(exist_ok=True)
    with open(log_path, "r+") as f:
        try:
            existing = json.load(f)
        except json.JSONDecodeError:
            existing = {}
        new_logs = [entry.dict() for entry in sync.entries]
        existing.setdefault(sync.ip, []).extend(new_logs)
        f.seek(0)
        json.dump(existing, f, indent=2)
        f.truncate()
    return {"status": "ok", "peer": sync.ip, "count": len(sync.entries)}


# Serve static HTML UI
app.mount("/", StaticFiles(directory="aria_dashboard_frontend", html=True), name="frontend")