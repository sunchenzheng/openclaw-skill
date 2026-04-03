local dr = Resolve()
dr:OpenPage("color")

local pm = dr:GetProjectManager()
local proj = pm:GetCurrentProject()
local tl = proj:GetCurrentTimeline()
print("Project: " .. proj:GetName())
print("Timeline: " .. tl:GetName())

-- Try GetColorPage
local cp = proj:GetColorPage()
print("GetColorPage: " .. tostring(cp) .. " type: " .. type(cp))

-- Try AutoWhiteBalance on project
local ok1, result1 = pcall(function() return proj:AutoWhiteBalance() end)
print("proj:AutoWhiteBalance: " .. tostring(ok1) .. " -> " .. tostring(result1))

-- Try SetLiftGammaGain on project
local ok2, result2 = pcall(function() return proj:SetLiftGammaGain({0,0,0},{0.05,0.05,0.05},{1,1,1}) end)
print("proj:SetLiftGammaGain: " .. tostring(ok2) .. " -> " .. tostring(result2))

-- Check what Timeline offers
local tl_methods = {"GetCurrentTimelineItem", "GetItemListInTrack", "GetCurrentVideoItem", "SetCurrentTimecode", "GrabStill"}
for i, m in ipairs(tl_methods) do
    local ok, result = pcall(function() return tl[m] end)
    print("tl:" .. m .. " = " .. tostring(ok) .. " " .. tostring(result))
end
