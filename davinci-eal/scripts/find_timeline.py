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

# List all projects and their timelines
projects = pm.GetProjectsInCurrentFolder()
print('All projects:')
for idx, name in projects.items():
    proj = pm.LoadProject(name)
    if proj:
        print(f'  [{idx}] {name} -> {proj.GetTimelineCount()} timelines')
        for i in range(1, proj.GetTimelineCount() + 1):
            tl = proj.GetTimelineByIndex(i)
            print(f'      Timeline[{i}]: {tl.GetName()}')
