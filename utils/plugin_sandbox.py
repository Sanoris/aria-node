import os
import importlib.util
from multiprocessing import Process
from pathlib import Path


def _exec_plugin(plugin_path: str, env_vars: dict, work_dir: str | None) -> None:
    """Helper to run the plugin code in a separate process."""
    if env_vars is not None:
        os.environ.clear()
        os.environ.update(env_vars)
    if work_dir:
        os.chdir(work_dir)

    spec = importlib.util.spec_from_file_location("sandboxed_plugin", plugin_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    if hasattr(mod, "run"):
        mod.run()


def run_in_sandbox(plugin_path: str | Path, env_vars: dict | None = None,
                   work_dir: str | None = None, wait: bool = True):
    """Execute a plugin module in an isolated process.

    Parameters
    ----------
    plugin_path : str or Path
        Path to the plugin file.
    env_vars : dict, optional
        Environment variables for the sandboxed process. If ``None`` the current
        environment is cleared and no variables are passed through.
    work_dir : str, optional
        Working directory for the sandboxed process.
    wait : bool, default ``True``
        If ``True`` the call will block until the plugin process exits.
    """
    path = str(plugin_path)
    env = env_vars if env_vars is not None else {}
    proc = Process(target=_exec_plugin, args=(path, env, work_dir))
    proc.start()
    if wait:
        proc.join()
    return proc
