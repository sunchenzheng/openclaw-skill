#!/usr/bin/env python3
# Test DaVinci Resolve API connection
import sys, os

# Set DLL path
dll = r"D:\youyou\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
os.environ["RESOLVE_SCRIPT_LIB"] = dll

# Add module path
module_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
sys.path.insert(0, module_path)

try:
    import DaVinciResolveScript as dvr
    resolve = dvr.scriptapp("Resolve")
    if resolve:
        pm = resolve.GetProjectManager()
        proj = pm.GetCurrentProject()
        tl = proj.GetCurrentTimeline() if proj else None
        print("OK: Connected to DaVinci Resolve")
        print("Project: " + str(proj.GetName() if proj else "None"))
        print("Timeline: " + str(tl.GetName() if tl else "None"))
        
        # Test auto_color
        if tl:
            clips = tl.GetItemListInTrack("video", 1)
            print("Clips on track 1: " + str(len(clips)))
            if clips:
                clip = clips[0]
                color = clip.GetColor()
                color.SetContrast(1.2)
                color.SetSaturation(1.1)
                print("OK: auto_color test passed")
    else:
        print("FAIL: resolve object is None")
except Exception as e:
    print("FAIL: " + str(e))
