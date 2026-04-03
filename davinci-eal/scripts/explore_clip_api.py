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

# Get the color page API
color_page = proj.GetColorPage()
print('ColorPage:', color_page)
print('ColorPage methods:', [m for m in dir(color_page) if not m.startswith('_')][:30])

# Get current timeline item
item = tl.GetCurrentTimelineItem()
print('\nTimelineItem:', item)
print('TimelineItem type:', type(item))
print('TimelineItem methods:', [m for m in dir(item) if not m.startswith('_')][:30])
