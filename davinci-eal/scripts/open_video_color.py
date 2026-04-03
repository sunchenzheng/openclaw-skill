#!/usr/bin/env python3
import sys, os
dll_path = r'D:\youyou\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
module_path = r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules'
api_path = r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting'
os.environ['RESOLVE_SCRIPT_LIB'] = dll_path
os.environ['RESOLVE_SCRIPT_API'] = api_path
sys.path.insert(0, module_path)

# Find 16.mov on desktop
desktop = r'C:\Users\123\Desktop'
video_path = None
for item in os.listdir(desktop):
    candidate = os.path.join(desktop, item, '16.mov')
    if os.path.exists(candidate):
        video_path = candidate
        print('Found video at:', video_path)
        break

if not video_path:
    print('ERROR: 16.mov not found on desktop')
    sys.exit(1)

import DaVinciResolveScript as dvr
resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
print('Project:', proj.GetName())

tl = proj.GetCurrentTimeline()
if not tl:
    print('Creating new timeline...')
    tl = proj.CreateTimeline('DR_Color_Test')
    print('Created timeline:', tl.GetName())

# Import media
media_storage = resolve.GetMediaStorage()
if media_storage:
    clips = media_storage.AddItemListToMediaPool(video_path)
    print('Imported clips:', len(clips) if clips else 'None')
    if clips:
        media_pool = proj.GetMediaPool()
        result = media_pool.AppendToTimeline(clips[0])
        print('Append result:', result)
        # Navigate to the clip
        tl.SetCurrentTimelineItemByIndex(0)
        clip_name = tl.GetCurrentTimelineItem().GetName() if tl.GetCurrentTimelineItem() else 'None'
        print('First clip on timeline:', clip_name)
else:
    print('ERROR: Media storage not available')

# Switch to color page
resolve.OpenPage('color')
print('Switched to color page')

# Take a screenshot
import ctypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
width = user32.GetSystemMetrics(0)
height = user32.GetSystemMetrics(1)
print('Screen resolution:', width, 'x', height)

import ctypes
from ctypes import wintypes
import struct

GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
LWA_ALPHA = 0x2

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32

class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', wintypes.DWORD * 3),
    ]

srcdc = user32.GetDC(0)
memdc = gdi32.CreateCompatibleDC(srcdc)
bmp = ctypes.create_string_buffer(width * height * 4)
bith = gdi32.CreateCompatibleBitmap(srcdc, width, height)
gdi32.SelectObject(memdc, bith)
ctypes.windll.gdi32.BitBlt(memdc, 0, 0, width, height, srcdc, 0, 0, 0x00CC0020)
user32.ReleaseDC(0, srcdc)

bmi = BITMAPINFO()
bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
bmi.bmiHeader.biWidth = width
bmi.bmiHeader.biHeight = -height
bmi.bmiHeader.biPlanes = 1
bmi.bmiHeader.biBitCount = 32
bmi.bmiHeader.biCompression = 0

gdi32.GetDIBits(memdc, bith, 0, height, bmp, ctypes.byref(bmi), 0)
gdi32.DeleteObject(bith)
gdi32.DeleteDC(memdc)

# Save as BMP first then convert
import struct
bmp_path = r'C:\Users\123\.openclaw\workspace\desktop_color_page.bmp'
raw_path = r'C:\Users\123\.openclaw\workspace\desktop_color_page.raw'
with open(raw_path, 'wb') as f:
    f.write(bmp.raw)

# Write BMP
file_size = 14 + 40 + width * height * 4
with open(bmp_path, 'wb') as f:
    f.write(b'BM')
    f.write(struct.pack('<I', file_size))
    f.write(struct.pack('<HH', 0, 0))
    f.write(struct.pack('<I', 14 + 40))
    f.write(struct.pack('<I', 40))
    f.write(struct.pack('<i', width))
    f.write(struct.pack('<i', -height))
    f.write(struct.pack('<HH', 1, 32))
    f.write(struct.pack('<I', 0))
    f.write(struct.pack('<I', width * height * 4))
    f.write(struct.pack('<i', 0))
    f.write(struct.pack('<i', 0))
    f.write(struct.pack('<II', 0, 0))
    f.write(bmp.raw)

print('Screenshot saved to:', bmp_path)
