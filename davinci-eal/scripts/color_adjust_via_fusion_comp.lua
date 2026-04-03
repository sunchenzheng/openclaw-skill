local dr = Resolve()
dr:OpenPage("fusion")

local pm = dr:GetProjectManager()
local proj = pm:GetCurrentProject()
local tl = proj:GetCurrentTimeline()
local cv = tl:GetCurrentVideoItem()

local fusion = cv:GetFusionCompByIndex(1)
print("Fusion comp: " .. tostring(fusion))

-- 测试 Fusion API
local methods = {"GetNodeCount", "GetToolCount", "GetNodes", "AddTool"}
for _, m in ipairs(methods) do
    local fn = fusion[m]
    print(m .. ": " .. (fn and "found" or "NOT FOUND"))
    if fn then
        local ok, result = pcall(function() return fn() end)
        print("  -> " .. tostring(ok) .. " " .. tostring(result))
    end
end
