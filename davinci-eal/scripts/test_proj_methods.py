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
print('Project:', proj.GetName())

# Check all methods on project
proj_methods = [m for m in dir(proj) if not m.startswith('_')]
print('Project methods:')
for m in proj_methods:
    print(f'  {m}')
