import sys
sys.path.insert(0, r'C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules')
import DaVinciResolveScript as dvr
resolve = dvr.scriptapp("Resolve")
resolve.OpenPage('color')
pm = resolve.GetProjectManager()
proj = pm.GetCurrentProject()
tl = proj.GetCurrentTimeline()

# Try GetCurrentTimelineItem via the project
print("Trying project approach...")
proj_methods = [m for m in dir(proj) if not m.startswith('__')]
print("Project methods:", proj_methods)

# Try to find Color page API through ExecuteEval or similar
resolve_eval = getattr(resolve, 'Evaluate/start', None)
print("Evaluate/start:", resolve_eval)

# Try MediaStorage approach - maybe add to media pool then get color page from pool item
media_storage = resolve.GetMediaStorage()
print("MediaStorage:", media_storage)
if media_storage:
    ms_methods = [m for m in dir(media_storage) if not m.startswith('__')]
    print("MediaStorage methods:", ms_methods[:20])

# Try Gallery approach - grab still and analyze
gallery = proj.GetGallery()
print("Gallery:", gallery)
if gallery:
    # Get still albums
    albums = gallery.GetGalleryStillAlbums()
    print("Still albums:", albums)
    if albums:
        album = gallery.GetCurrentStillAlbum()
        print("Current album:", album)
        if album:
            album_methods = [m for m in dir(album) if not m.startswith('__')]
            print("Album methods:", album_methods[:20])
