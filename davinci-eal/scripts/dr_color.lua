import sys
sys.path.insert(0, [[C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules]])
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
clips = tl.GetItemListInTrack("video", 1)
if clips and len(clips) > 0:
    clip = clips[0]
    print("Clip: " + clip.GetName())
    color = clip.GetColor()
    if color:
        old_contrast = color.GetContrast()
        old_sat = color.GetSaturation()
        print("Before - Contrast: " + str(old_contrast) + ", Saturation: " + str(old_sat))
        color.SetContrast(1.1)
        color.SetSaturation(1.2)
        print("After - Contrast: 1.1, Saturation: 1.2")
        print("OK")
    else:
        print("FAIL: color object is None")
else:
    print("FAIL: no clips found")
