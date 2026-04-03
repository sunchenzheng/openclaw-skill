#!/usr/bin/env python3
import sys, os
dll_path = r'D:\youyou\Blackmagic Design\DaVinci Resolve\fusionscript.dll'
module_path = r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules'
api_path = r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting'
os.environ['RESOLVE_SCRIPT_LIB'] = dll_path
os.environ['RESOLVE_SCRIPT_API'] = api_path
sys.path.insert(0, module_path)

import DaVinciResolveScript as dvr

# Try both approaches
print('=== Testing DaVinciResolveScript API ===')
print('Module:', dvr)
print('Module attrs:', [a for a in dir(dvr) if not a.startswith('__')])

# Approach 1: scriptapp
resolve1 = getattr(dvr, 'scriptapp', None)
print('scriptapp attr:', resolve1)
if resolve1:
    r1 = resolve1('Resolve')
    print('resolve1:', r1)
    print('resolve1 type:', type(r1))

# Approach 2: Resolve()
resolve2 = getattr(dvr, 'Resolve', None)
print('Resolve attr:', resolve2)
if resolve2:
    r2 = resolve2()
    print('resolve2:', r2)
