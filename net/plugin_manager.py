import os
import importlib.util

PLUGIN_DIR = "plugins"

def discover_plugins():
    plugins = []
    for filename in os.listdir(PLUGIN_DIR):
        if filename.endswith(".py") and not filename.startswith("_"):
            path = os.path.join(PLUGIN_DIR, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], path)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
                if hasattr(module, "run"):
                    plugins.append(module)
            except Exception as e:
                print(f"[!] Failed to load {filename}: {e}")
    return plugins

def run_plugins():
    plugins = discover_plugins()
    print(f"[🔌] Running {len(plugins)} plugin(s)...")
    for plugin in plugins:
        try:
            print(f"[→] {plugin.__name__}")
            plugin.run()
        except Exception as e:
            print(f"[!] Plugin {plugin.__name__} failed: {e}")

if __name__ == "__main__":
    run_plugins()
