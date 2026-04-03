#!/usr/bin/env python3
import sys, os
dll_path = r'D:\youyou\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
module_path = r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules'
api_path = r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting'
os.environ['RESOLVE_SCRIPT_LIB'] = dll_path
os.environ['RESOLVE_SCRIPT_API'] = api_path
sys.path.insert(0, module_path)

import DaVinciResolveScript as dvr
resolve = dvr.scriptapp('Resolve')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()

# Use fuscript Python interpreter approach
# Execute via fuscript
import subprocess
script_content = '''
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
clips = tl.GetItemListInTrack("video", 1)
if clips:
    clip = clips[0]
    color = clip.GetColor()
    if color:
        color.SetContrast(1.1)
        color.SetSaturation(1.2)
        print("OK: Adjusted", clip.GetName())
        print("Contrast:", color.GetContrast())
        print("Saturation:", color.GetSaturation())
    else:
        print("FAIL: color object is None")
else:
    print("FAIL: no clips")
'''
# Write script to temp file
script_path = r'C:\Users\123\.openclaw\workspace\skills\davinci-eal\scripts\dr_color.py'
with open(script_path, 'w', encoding='utf-8') as f:
    f.write(script_content)

print("Script written to:", script_path)
print("Ready to execute via fuscript")
