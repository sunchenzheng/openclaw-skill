"""
OpenClaw Scheduled Backup Script
Zips the .openclaw folder into a timestamped archive stored in the specified root.
"""
import os
import sys
import zipfile
import datetime

def backup_openclaw(workspace_root, backup_root):
    today = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    output_name = f".openclaw_backup_{today}.zip"
    output_path = os.path.join(backup_root, output_name)
    os.makedirs(backup_root, exist_ok=True)

    # Navigate to .openclaw root (parent of workspace)
    openclaw_root = os.path.dirname(workspace_root.rstrip(os.sep))

    print(f"[Backup] Packing: {openclaw_root}")
    print(f"[Backup] Output:  {output_path}")

    count = 0
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(openclaw_root):
            # Skip node_modules (too large, not needed)
            dirs[:] = [d for d in dirs if d != 'node_modules']
            for file in files:
                file_path = os.path.join(root, file)
                # Store as .openclaw/... (no leading backslash junk on Windows)
                rel = os.path.relpath(file_path, openclaw_root)
                zf.write(file_path, rel)
                count += 1
                if count % 200 == 0:
                    print(f"  [Backup] Added {count} files...")

    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"[OK] Backup complete! {count} files, {size_mb:.1f} MB")
    print(f"[OK] File: {output_path}")
    return output_path

if __name__ == '__main__':
    # Default: workspace at %USERPROFILE%\.openclaw\workspace, backup to %USERPROFILE%
    workspace_root = os.path.join(os.path.expanduser('~'), '.openclaw', 'workspace')
    backup_root = os.path.expanduser('~')

    if len(sys.argv) >= 2:
        workspace_root = sys.argv[1]
    if len(sys.argv) >= 3:
        backup_root = sys.argv[2]

    backup_openclaw(workspace_root, backup_root)
