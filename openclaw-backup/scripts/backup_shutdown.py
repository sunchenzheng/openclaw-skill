"""
Backup + Shutdown Script for Windows
1. Run OpenClaw backup
2. Shutdown PC
"""
import os
import sys
import zipfile
import datetime
import subprocess

def backup_and_shutdown(workspace_root, backup_root):
    # === Part 1: Backup ===
    today = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_name = f".openclaw_backup_{today}.zip"
    output_path = os.path.join(backup_root, output_name)
    os.makedirs(backup_root, exist_ok=True)

    openclaw_root = os.path.dirname(workspace_root.rstrip(os.sep))
    print(f"[Backup] Packing: {openclaw_root}")

    count = 0
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(openclaw_root):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            for file in files:
                file_path = os.path.join(root, file)
                rel = os.path.relpath(file_path, openclaw_root)
                zf.write(file_path, rel)
                count += 1

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[Backup] Done. {count} files, {size_mb:.1f} MB -> {output_path}")

    # === Part 2: Shutdown ===
    print("[Shutdown] Initiating system shutdown in 60 seconds...")
    subprocess.run(['shutdown', '/s', '/t', '60', '/c', 'OpenClaw scheduled backup complete. PC shutting down.'])
    print("[Shutdown] Shutdown scheduled. To cancel: shutdown /a")

if __name__ == '__main__':
    workspace_root = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace')
    backup_root = os.path.expanduser('~')
    backup_and_shutdown(workspace_root, backup_root)
