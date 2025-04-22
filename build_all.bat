@echo off
echo [*] Cleaning old builds...
rmdir /s /q dist
rmdir /s /q build
del deploy_bundle.zip 2>nul

echo [*] Recompiling aria.exe (node.py) with PyInstaller...
pyinstaller --onefile --noconsole --name aria aria_node\node.py

echo [*] Recompiling setup_payload.exe (setup_payload_cli.py) with PyInstaller...
pyinstaller --onefile --noconsole --name setup_payload setup_payload_cli.py

echo [*] Packaging payload...
python zip_payload.py

echo [+] Build and packaging complete! Output: deploy_bundle.zip
pause