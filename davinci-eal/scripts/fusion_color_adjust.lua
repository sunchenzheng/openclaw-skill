local dr = Resolve()
dr:OpenPage("fusion")

local pm = dr:GetProjectManager()
local proj = pm:GetCurrentProject()
local tl = proj:GetCurrentTimeline()
local cv = tl:GetCurrentVideoItem()

print("Current clip: " .. cv:GetName())
print("Fusion comp count: " .. cv:GetFusionCompCount())

-- 已有1个Fusion comp，尝试获取它
local fusion = cv:GetFusionCompByIndex(1)
print("GetFusionCompByIndex(1): " .. tostring(fusion))

if not fusion then
    -- 尝试按名称
    local names = cv:GetFusionCompNameList()
    print("Fusion comp names: " .. tostring(names))
    if names and #names > 0 then
        fusion = cv:GetFusionCompByName(names[1])
        print("GetFusionCompByName: " .. tostring(fusion))
    end
end

if fusion then
    print("Fusion comp node count: " .. fusion:GetNodeCount())
    
    -- 查看已有的节点
    for i = 1, fusion:GetNodeCount() do
        local node = fusion:GetNode(i)
        if node then
            local attrs = node:GetAttrs()
            print("  Node " .. i .. ": " .. (attrs.TOOLS_Name or "unnamed"))
        end
    end
    
    -- 添加 ColorCorrector 节点
    -- syntax: AddTool(ToolName, x, y) - position doesn't matter much
    local cc = fusion:AddTool("ColorCorrector", 100, 100)
    if cc then
        print("ColorCorrector added: " .. cc:GetAttrs().TOOLS_Name)
        
        -- 调色参数
        cc.LiftRed = 0.05
        cc.LiftGreen = 0.05
        cc.LiftBlue = 0.05
        cc.GammaRed = 1.03
        cc.GammaGreen = 1.03
        cc.GammaBlue = 1.03
        cc.Contrast = 1.1
        cc.Saturation = 1.15
        
        print("调色完成!")
        print("  Lift: +0.05 (暗部提亮)")
        print("  Gamma: +3% (中间调)")
        print("  Contrast: +10%")
        print("  Saturation: +15%")
    else
        print("ERROR: Could not add ColorCorrector")
    end
else
    print("ERROR: Could not access Fusion comp")
end
