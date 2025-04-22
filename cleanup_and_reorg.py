import shutil
import os
from pathlib import Path

# Define folders to create
folders = {

}

# Delete targets
delete_targets = [
    "__pycache__",

]

def move_files():
    for folder, patterns in folders.items():
        os.makedirs(folder, exist_ok=True)
        for pattern in patterns:
            for path in Path().glob(pattern):
                
                if path.is_dir():
                    shutil.move(str(path), folder)

def delete_items():
    for target in delete_targets:
        path = Path(target)
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path, ignore_errors=True)

def main():
    #move_files()
    delete_items()
    print("[+] Cleanup and reorganization complete.")

if __name__ == "__main__":
    main()