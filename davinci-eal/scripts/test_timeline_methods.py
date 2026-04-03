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
print('Timeline:', tl.GetName())

# Try to get color page via timeline
# Timeline methods
tl_methods = ['GetCurrentTimelineItem', 'GetItemListInTrack', 'GetName', 'GetTrackCount',
               'SetCurrentTimelineItem', 'SetCurrentTimelineItemByIndex', 'NextClip', 'PrevClip',
               'GetCurrentTimecode', 'GetColorPage', 'GetNodeGraph', 'DeleteAllNodes', 'AddNode']

for m in tl_methods:
    try:
        method = getattr(tl, m, None)
        if method is None:
            print(f'{m}: None')
        elif callable(method):
            result = method()
            print(f'{m}() = {result}')
        else:
            print(f'{m} = {method}')
    except Exception as e:
        print(f'{m}: error={e}')
