import os
from net.plugin_manager import discover_plugins

def run_plugins_by_trigger(trigger):
    plugins = discover_plugins()
    for plugin in plugins:
        if plugin.__name__ == trigger:
            try:
                plugin.run()
                print(f"[⚡] Triggered plugin: {trigger}")
            except Exception as e:
                print(f"[!] Plugin {trigger} failed: {e}")
