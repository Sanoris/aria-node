import zipfile
from pathlib import Path

output_zip = "deploy_bundle.zip"

# Files and folders to include
targets = [
    "aria.exe",
    "setup_payload.exe",
    "dropper/",
    "plugins/",
    "proto/",
    "crypto/",
    "memory/tagger.py",  # Keep core memory logging
    "net/dashboard_sync.py",
]

def package():
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for target in targets:
            path = Path(target)
            if path.is_file():
                zipf.write(path, path)
            elif path.is_dir():
                for file in path.rglob("*"):
                    if file.is_file():
                        zipf.write(file, file)
    print(f"[+] Payload packaged to {output_zip}")

if __name__ == "__main__":
    package()