import base64
import os

PLUGIN_DIR = "plugins"

def receive_plugin(encoded, filename, sender="unknown"):
    os.makedirs(PLUGIN_DIR, exist_ok=True)
    path = os.path.join(PLUGIN_DIR, filename)
    try:
        code = base64.b64decode(encoded.encode()).decode()
        with open(path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[📦] Plugin '{filename}' received from {sender} and saved.")
    except Exception as e:
        print(f"[!] Failed to install plugin from {sender}: {e}")
