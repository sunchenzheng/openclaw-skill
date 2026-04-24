---
name: windows-ui-automation
description: Automate Windows GUI interactions using Python (pyautogui) + AI vision for applications with custom-drawn UI (like DaVinci Resolve). Use when asked to control a Windows application UI, automate mouse/keyboard actions, or find UI element coordinates.
author: sunchenzheng
version: 1.1
tags: [windows, automation, pyautogui, ui-automation, mouse, keyboard]
---

# Windows UI Automation Skill

Automate Windows GUI interactions when standard Windows UI Automation (pywinauto) fails on custom-drawn applications.

## When to Use

- User asks to control a Windows application UI programmatically
- Application has a **custom-drawn UI** (no standard Windows controls — pywinauto's `child_window()` won't find elements)
- Need to find UI element coordinates to click/type
- Example tasks: automate DaVinci Resolve, Adobe Premiere, or any non-standard Windows app

## Core Method: pyautogui + AI Vision

### Step 1: Screenshot

```python
import pyautogui
pyautogui.screenshot("screen.png")                              # Full screen
pyautogui.screenshot(region=(x, y, width, height))                # Region crop
```

### Step 2: AI Vision → Find Coordinates

```python
image(
    prompt="Find the exact pixel position of the 'Saturation' slider. Give coordinates relative to full screen (WxH).",
    image="screen.png"
)
```

### Step 3: Operate

```python
pyautogui.click(x, y)           # Click
pyautogui.drag(dx, dy, duration=0.5)  # Drag
pyautogui.type_keys("60")        # Type text
pyautogui.moveTo(x, y, duration=0.3)   # Move mouse
```

## Architecture Decision Tree

```
Is the app standard Windows UI (buttons, menus)?
├── YES → Use pywinauto child_window() — reliable
└── NO  → Use pyautogui + AI vision
    ├── Can you see the element on screen? → AI vision coordinates
    ├── No standard controls → pyautogui pixel scan
    └── Fixed-position UI → Hardcode coordinates after first discovery
```

## pyautogui Quick Reference

```python
import pyautogui
pyautogui.FAILSAFE = False     # Disable fail-safe (for unattended scripts)
pyautogui.PAUSE = 0.1          # Delay between actions (seconds)

pyautogui.click(x, y, clicks=2, interval=0.2)   # Double-click
pyautogui.rightClick(x, y)
pyautogui.drag(startX, startY, offsetX, offsetY, duration=0.5)
pyautogui.moveTo(x, y, duration=0.3)
pyautogui.type_keys("{UP}")     # Arrow keys
pyautogui.type_keys("^a")       # Ctrl+A
pyautogui.type_keys("%{F4}")    # Alt+F4

# Locate by image (template matching)
location = pyautogui.locateOnScreen("button.png", confidence=0.8)
if location:
    center = pyautogui.center(location)
    pyautogui.click(center)
```

## Keyboard Modifiers (pywinauto notation)

| Key | pywinauto | pyautogui |
|-----|-----------|-----------|
| Ctrl | `^` | `^` |
| Alt | `%` | `%` |
| Shift | `+` | `+` |
| Escape | `{ESC}` | `{ESC}` |
| Tab | `{TAB}` | `{TAB}` |
| Enter | `{ENTER}` | `{ENTER}` |
| Delete | `{DELETE}` | `{DELETE}` |
| Home | `{HOME}` | `{HOME}` |
| End | `{END}` | `{END}` |
| Up/Down arrows | `{UP}` / `{DOWN}` | `{UP}` / `{DOWN}` |

## Finding Windows Handle (HWND)

```python
import ctypes
user32 = ctypes.windll.user32

windows = []
def enum_callback(hwnd, lParam):
    length = user32.GetWindowTextLengthW(hwnd)
    if length > 0:
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value
        if "TargetApp" in title:
            windows.append((hwnd, title))
    return True

EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

if windows:
    hwnd, title = windows[0]  # First match
    user32.SetForegroundWindow(hwnd)  # Bring to front
```

## Focus and Stability

```python
from pywinauto import Application
app = Application(backend='uia')
app.connect(handle=hwnd)
dlg = app.window(handle=hwnd)
dlg.set_focus()
time.sleep(0.3)  # Wait for window to stabilize
```

## Emergency Stop Protocol

**CRITICAL**: When user says "停" (stop):

```bash
# Immediately kill all related processes
taskkill /F /IM python.exe
taskkill /F /IM node.exe
```

Do NOT finish the current loop. Stop immediately.

## Known Limitations

- **DR20 Fusion API**: PowerWindow creation is blocked — must use UI automation instead
- **Saturation sliders**: Direct value input (Ctrl+A → type → Enter) is more reliable than drag
- **Coordinate drift**: When a window moves, all hardcoded coordinates become invalid
- **Multi-monitor**: Coordinates are absolute across all monitors

## Scripts

| Script | Purpose |
|--------|---------|
| `mouse_control.ps1` | Native PowerShell mouse control (fallback) |
| `keyboard_control.ps1` | Native PowerShell keyboard control |
| `explore_ui.py` | Scan screen for UI elements using pixel analysis |

## Example: DaVinci Resolve 20 Workflow

```python
# 1. Find DR window
hwnd = 1905922  # DaVinci Resolve Studio main window
user32.SetForegroundWindow(hwnd)
time.sleep(0.5)

# 2. Create new node (Alt+C)
app = Application(backend='uia').connect(handle=hwnd)
app.window(handle=hwnd).set_focus()
app.window(handle=hwnd).type_keys('%c')  # Alt+C
time.sleep(0.5)

# 3. Take screenshot
img = pyautogui.screenshot()

# 4. Ask AI where the Curves button is
# → AI responds: "Curves tab at approximately (240, 874)"

# 5. Click Curves tab
pyautogui.click(240, 874)
time.sleep(0.8)

# 6. Trace curve line (scan for white diagonal)
curve_pts = []
for y in range(900, 1400, 5):
    for x in range(1000, 2600, 3):
        pixel = img.getpixel((x, y))
        if pixel[0] > 200 and pixel[1] > 200 and pixel[2] > 200:
            if max(pixel) - min(pixel) < 40:  # Nearly white = curve
                curve_pts.append((x, y))
                break

# 7. Add contrast S-curve by dragging points
# ... (see actual implementation in workspace)
```

## Installation

```bash
pip install pyautogui pywin32
```

No additional drivers required — uses Windows native `user32.dll`.
