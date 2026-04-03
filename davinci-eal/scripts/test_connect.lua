-- Test DaVinci Resolve connection
local dr = fuse.scriptapp("Resolve")
if dr then
    local pm = dr.GetProjectManager()
    local proj = pm.GetCurrentProject()
    local tl = proj and proj.GetCurrentTimeline()
    print("OK: Connected")
    print("Project: " .. (proj and proj.GetName() or "None"))
    print("Timeline: " .. (tl and tl.GetName() or "None"))
else
    print("FAIL: Cannot connect")
end
