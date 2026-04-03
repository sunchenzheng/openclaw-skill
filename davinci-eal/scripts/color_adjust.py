import sys
sys.path.insert(0, r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
print("Resolve methods (all):")
resolve_methods = [m for m in dir(resolve) if not m.startswith('__')]
for m in resolve_methods:
    print(f"  {m}")

# Check GalleryStill methods
resolve.OpenPage('color')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()
still = tl.GrabStill()
print("\nGalleryStill methods:")
if still:
    still_methods = [m for m in dir(still) if not m.startswith('__')]
    for m in still_methods:
        print(f"  {m}")
