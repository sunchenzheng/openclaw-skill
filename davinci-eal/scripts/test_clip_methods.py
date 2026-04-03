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

clips = tl.GetItemListInTrack('video', 1)
clip = clips[0]
print('Clip name:', clip.GetName())
print('Clip type:', type(clip))

# Try calling methods on clip to see what works
test_methods = ['GetColor', 'GetNodeGraph', 'GetName', 'GetDuration', 'GetStart', 
                'GetPage', 'SetColor', 'GetBrightness', 'SetLiftGammaGain',
                'SetContrast', 'SetSaturation', 'GetContrast', 'GetSaturation']

for m in test_methods:
    try:
        method = getattr(clip, m, None)
        print(f'{m}: attr_type={type(method)}', end=' ')
        if callable(method):
            result = method()
            print(f'call={result}')
        else:
            print(f'non-callable={method}')
    except Exception as e:
        print(f'error={e}')
