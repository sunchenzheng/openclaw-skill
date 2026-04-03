---
name: openclaw-backup
description: OpenClaw scheduled backup automation. Creates a timestamped ZIP archive of the entire .openclaw configuration folder and stores it in the user's home directory. Use when the user wants to: (1) set up a scheduled backup of OpenClaw data, (2) manually trigger a backup, (3) configure Windows Task Scheduler to run backups automatically, (4) restore from a backup archive.
---

# OpenClaw Backup Skill

## Backup Script

**Script location:** `skills/openclaw-backup/scripts/backup.py`

Run manually:
```
python skills/openclaw-backup/scripts/backup.py
```

Optional arguments:
```bash
python skills/openclaw-backup/scripts/backup.py <workspace_root> <backup_root>
# Example:
python skills/openclaw-backup/scripts/backup.py C:\Users\123\.openclaw\workspace C:\Users\123
```

**What it backs up:** The entire `.openclaw` folder (config, agents, sessions, workspace, etc.)
**What it skips:** `node_modules` directories
**Output:** `.openclaw_backup_YYYY-MM-DD_HHMMSS.zip` in the backup root
**Default backup root:** User's home directory (`%USERPROFILE%`)

---

## Setting Up a Scheduled Backup (Windows Task Scheduler)

Create a scheduled task to run the backup automatically.

### Option 1: Use schtasks via command line

```powershell
# Daily at 2:00 AM
schtasks /create /tn "OpenClaw Daily Backup" `
  /tr "python.exe C:\Users\123\.openclaw\workspace\skills\openclaw-backup\scripts\backup.py" `
  /sc daily /st 02:00

# Every 6 hours
schtasks /create /tn "OpenClaw 6hour Backup" `
  /tr "python.exe C:\Users\123\.openclaw\workspace\skills\openclaw-backup\scripts\backup.py" `
  /sc hourly /mo 6

# On logon
schtasks /create /tn "OpenClaw Logon Backup" `
  /tr "python.exe C:\Users\123\.openclaw\workspace\skills\openclaw-backup\scripts\backup.py" `
  /sc onlogon
```

### Option 2: Create via Task Scheduler GUI

1. Open **Task Scheduler** (`taskschd.msc`)
2. **Action** → **Create Basic Task**
3. Name: `OpenClaw Daily Backup`
4. Trigger: Daily / Weekly / On logon (choose)
5. Action: **Start a program**
   - Program: `python.exe`
   - Arguments: `C:\Users\123\.openclaw\workspace\skills\openclaw-backup\scripts\backup.py`
6. Finish

---

## Restore from Backup

Extract the ZIP to restore:
```powershell
# Extract to a temp location first to inspect
Expand-Archive -Path "C:\Users\123\.openclaw_backup_2026-03-25_231940.zip" -DestinationPath "C:\Users\123\restore_temp"

# Then copy desired folders back over your .openclaw directory
# Be careful not to overwrite your current data without backing it up first
```

Or use 7-Zip / WinRAR to extract interactively.

---

## Backup Retention

Older backups accumulate over time. To auto-delete backups older than N days, add a cleanup step:

```powershell
# Delete .openclaw_backup zip files older than 30 days
Get-ChildItem "C:\Users\123\*.zip" -Filter ".openclaw_backup_*.zip" |
  Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
  Remove-Item -WhatIf
```

Remove `-WhatIf` to execute the deletion.
