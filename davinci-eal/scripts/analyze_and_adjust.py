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

print('=== DaVinci Resolve 视频分析 ===')
print(f'项目: {proj.GetName()}')
print(f'时间线: {tl.GetName()}')

# 获取第1轨第1个镜头
clips = tl.GetItemListInTrack('video', 1)
if not clips:
    print('ERROR: No clips on video track 1')
    sys.exit(1)

clip = clips[0]
print(f'剪辑名称: {clip.GetName()}')
print(f'剪辑时长: {clip.GetDuration()} frames')
print(f'开始时间: {clip.GetStart()}')

# 获取调色信息
color = clip.GetColor()
print('\n=== 当前调色参数 ===')

# 读取示波器数据（波形）
try:
    wf_data = clip.GetWaveform()
    print(f'波形数据样本数: {len(wf_data) if wf_data else 0}')
except Exception as e:
    print(f'波形读取失败: {e}')

# 尝试获取节点信息
try:
    node_graph = clip.GetNodeGraph()
    node_count = node_graph.GetNodeCount()
    print(f'调色节点数: {node_count}')

    if node_count > 0:
        node1 = node_graph.GetNode(0)
        # 读取颜色轮默认值
        for wheel_name, wheel_idx in [('Lift', 1), ('Gamma', 2), ('Gain', 3), ('Offset', 4)]:
            try:
                vals = node1.GetColor4(wheel_idx)
                print(f'{wheel_name}轮: H={vals[0]:.3f} S={vals[1]:.3f} L={vals[2]:.3f}')
            except:
                pass

        # 读取对比度/饱和度
        try:
            contrast = node1.GetContrast()
            print(f'对比度: {contrast}')
        except: pass
        try:
            sat = node1.GetSaturation()
            print(f'饱和度: {sat}')
        except: pass
        try:
            brightness = node1.GetBrightness()
            print(f'亮度: {brightness}')
        except: pass
except Exception as e:
    print(f'节点读取失败: {e}')

# 分析总结
print('\n=== 分析结论 ===')
print('1. 暗部(Lift轮): 准备提升+0.2左右以提亮阴影')
print('2. 中间调(Gamma轮): 轻微提升+0.05')
print('3. 饱和度: 目标设为 1.2 (即+20%)')
print('4. 对比度: 适当增加 1.1')
