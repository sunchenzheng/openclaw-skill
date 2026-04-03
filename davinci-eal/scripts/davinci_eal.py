"""
DaVinci Resolve EAL (Execution Abstraction Layer)
将结构化 Action 指令转化为 DaVinci Resolve API 调用

用法:
  python davinci_eal.py <action> [param1=value] [param2=value] ...
  python davinci_eal.py color_wheel_adjust wheel=gamma hue=15 saturation=1.2
  python davinci_eal.py node_add node_type=serial
"""

import sys
import os
import json
import argparse

# ── DaVinci Resolve Scripting API 初始化 ──
def init_resolve():
    """初始化 DR API 连接"""
    # 设置 DLL 路径环境变量
    if sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        dll_path = r"D:\youyou\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        module_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Modules"
        api_path = r"C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting"
        os.environ["RESOLVE_SCRIPT_LIB"] = dll_path
        os.environ["RESOLVE_SCRIPT_API"] = api_path
        if module_path not in sys.path:
            sys.path.insert(0, module_path)

    try:
        import DaVinciResolveScript as script
        resolve = script.scriptapp("Resolve")
        if resolve and resolve.GetProjectManager():
            return resolve
    except Exception as e:
        pass

    # Windows DLL 加载（备用方案）
    if sys.platform.startswith("win") or sys.platform.startswith("cygwin"):
        dll_path = r"D:\youyou\Blackmagic Design\DaVinci Resolve\fusionscript.dll"
        if os.path.exists(dll_path):
            import importlib.util
            spec = importlib.util.spec_from_file_location("fusionscript", dll_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                resolve = mod
                if resolve.GetProjectManager():
                    return resolve
    return None


def wheel_adjust(resolve, params):
    """
    颜色轮调整
    wheel: lift | gamma | gain | offset
    hue: -180~180, saturation: 0~10, luminance: -2~2
    """
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    timeline.SetCurrentTimelineItemByIndex(params.get("node_index", 1) - 1)
    item = timeline.GetCurrentTimelineItem()

    node_graph = item.GetNodeGraph()
    node = node_graph.GetNode(params.get("node_index", 1) - 1)

    wheel = params.get("wheel", "gamma")
    hue = params.get("hue", 0)
    sat = params.get("saturation", 1.0)
    lum = params.get("luminance", 0.0)

    # DR API: 颜色轮通过特定方法调整
    # StructureMap: 1=lift, 2=gamma, 3=gain, 4=offset
    wheel_map = {"lift": 1, "gamma": 2, "gain": 3, "offset": 4}
    wheel_idx = wheel_map.get(wheel, 2)

    try:
        # 获取当前颜色轮值
        current = node.GetColor4(wheel_idx)
        new_hue = (current[0] + hue / 360.0 * 2) % 2
        new_sat = max(0, current[1] * sat)
        new_lum = max(-1, min(1, current[2] + lum))
        node.SetColor4(wheel_idx, [new_hue, new_sat, new_lum, 1.0])

        # 同步到控制面板
        node.LuaCall("Resolve:CallColorWheel()")

        return {
            "status": "ok",
            "action": "color_wheel_adjust",
            "wheel": wheel,
            "applied": {"hue": new_hue, "saturation": new_sat, "luminance": new_lum}
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def node_add(resolve, params):
    """添加调色节点"""
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    item = timeline.GetCurrentTimelineItem()
    node_graph = item.GetNodeGraph()
    node_count_before = node_graph.GetNodeCount()

    try:
        node_graph.AddNode()
        node_count_after = node_graph.GetNodeCount()
        new_node_index = node_count_after - 1

        # 连接方式
        conn_type = params.get("node_type", "serial")
        if conn_type == "parallel" and node_count_before > 0:
            prev_node = node_graph.GetNode(node_count_before - 1)
            prev_node.SetOutput("PassThrough", node_graph.GetNode(new_node_index))

        return {
            "status": "ok",
            "action": "node_add",
            "node_type": conn_type,
            "node_index": new_node_index + 1,
            "total_nodes": node_count_after
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def lut_apply(resolve, params):
    """应用 LUT"""
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    item = timeline.GetCurrentTimelineItem()
    node_graph = item.GetNodeGraph()
    node = node_graph.GetNode(params.get("node_index", 1) - 1)

    lut_name = params.get("lut_name", "")

    try:
        lut_list = resolve.GetLUTList()
        lut_path = next((lut for lut in lut_list if lut_name.lower() in lut.lower()), None)

        if not lut_path:
            return {"status": "error", "message": f"LUT not found: {lut_name}"}

        node.SetLUT(1, lut_path)
        return {
            "status": "ok",
            "action": "lut_apply",
            "lut_name": lut_name,
            "lut_path": lut_path,
            "node_index": params.get("node_index", 1)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def lut_remove(resolve, params):
    """移除 LUT"""
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    item = timeline.GetCurrentTimelineItem()
    node_graph = item.GetNodeGraph()
    node = node_graph.GetNode(params.get("node_index", 1) - 1)

    try:
        node.SetLUT(1, "")
        return {
            "status": "ok",
            "action": "lut_remove",
            "node_index": params.get("node_index", 1)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def node_reset(resolve, params):
    """重置节点"""
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    item = timeline.GetCurrentTimelineItem()
    node_graph = item.GetNodeGraph()
    node_index = params.get("node_index", 1) - 1

    try:
        scope = params.get("scope", "all")
        if scope == "all":
            node.ResetDestructive()
        elif scope == "wheels":
            for wheel_idx in [1, 2, 3, 4]:
                node.SetColor4(wheel_idx, [1.0, 1.0, 0.0, 1.0])
        elif scope == "curves":
            node.ResetCurve()

        return {
            "status": "ok",
            "action": "node_reset",
            "node_index": params.get("node_index", 1),
            "scope": scope
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def magic_mask(resolve, params):
    """Magic Mask 操作"""
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    item = timeline.GetCurrentTimelineItem()
    subject = params.get("subject", "face")
    action = params.get("action", "create")

    try:
        if action == "create":
            node_graph = item.GetNodeGraph()
            mask_node = node_graph.AddNode("Masquerade")
            mask_node.SetMaskEnable(1)

            if subject == "face":
                mask_node.SetSetting("MasqueradeNetworkType", "FaceTracking")
            elif subject == "body":
                mask_node.SetSetting("MasqueradeNetworkType", "BodyTracking")

            return {"status": "ok", "action": "magic_mask", "subject": subject, "created": True}

        elif action == "track":
            item.SetMaskEnable(1)
            item.MasqueradeTrackForward()
            return {"status": "ok", "action": "magic_mask", "action": "tracking"}

        elif action == "reset":
            item.SetMaskEnable(0)
            return {"status": "ok", "action": "magic_mask", "action": "reset"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def power_window(resolve, params):
    """Power Window 遮罩"""
    project = resolve.GetProjectManager().GetCurrentProject()
    if not project:
        return {"status": "error", "message": "No active project"}

    timeline = project.GetCurrentTimeline()
    if not timeline:
        return {"status": "error", "message": "No active timeline"}

    item = timeline.GetCurrentTimelineItem()
    shape = params.get("shape", "circle")
    invert = params.get("invert", False)
    feather = params.get("feather", 0)
    points = params.get("points", [])

    try:
        window = item.AddPowerWindow()
        window.SetEnabled(1)
        window.SetInvert(invert)
        window.SetFeather(feather)

        if shape == "circle" and len(points) >= 3:
            cx, cy, r = points[0], points[1], points[2]
            window.SetType("Circle")
            window.SetCenter([cx, cy])
            window.SetRadius(r)
        elif shape == "rectangle" and len(points) >= 4:
            x, y, w, h = points[0], points[1], points[2], points[3]
            window.SetType("Rectangle")
            window.SetPoint([x, y])
            window.SetSize([w, h])

        return {
            "status": "ok",
            "action": "power_window",
            "shape": shape,
            "invert": invert
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def scope_read(resolve, params):
    """读取示波器数据"""
    scope_type = params.get("scope_type", "waveform")

    try:
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            return {"status": "error", "message": "No active project"}

        timeline = project.GetCurrentTimeline()
        if not timeline:
            return {"status": "error", "message": "No active timeline"}

        item = timeline.GetCurrentTimelineItem()

        if scope_type == "waveform":
            data = item.GetWaveform()
        elif scope_type == "rgb_parade":
            data = item.GetRGBParade()
        elif scope_type == "vectorscope":
            data = item.GetVectorscope()
        elif scope_type == "histogram":
            data = item.GetHistogram()

        return {
            "status": "ok",
            "action": "scope_read",
            "scope_type": scope_type,
            "data": str(data)[:500]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def project_load(resolve, params):
    """加载项目/时间线"""
    project_name = params.get("project_name", "")
    timeline_name = params.get("timeline_name", "")

    try:
        pm = resolve.GetProjectManager()
        project = pm.LoadProject(project_name) if project_name else pm.GetCurrentProject()
        if not project:
            return {"status": "error", "message": f"Project not found: {project_name}"}

        if timeline_name:
            timeline = project.GetTimelineByName(timeline_name)
            if timeline:
                project.SetCurrentTimeline(timeline)
            else:
                return {"status": "error", "message": f"Timeline not found: {timeline_name}"}

        return {
            "status": "ok",
            "action": "project_load",
            "project": project.GetName(),
            "timeline": timeline_name or project.GetCurrentTimeline().GetName()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def timeline_nav(resolve, params):
    """时间线导航"""
    action = params.get("action", "")
    timecode = params.get("timecode", "")

    try:
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            return {"status": "error", "message": "No active project"}

        timeline = project.GetCurrentTimeline()
        if not timeline:
            return {"status": "error", "message": "No active timeline"}

        if action == "go_to_start":
            timeline.GoToStart()
        elif action == "go_to_end":
            timeline.GoToEnd()
        elif action == "next_clip":
            timeline.NextClip()
        elif action == "prev_clip":
            timeline.PrevClip()
        elif action == "go_to_timecode" and timecode:
            timeline.SetCurrentTimecode(timecode)

        return {
            "status": "ok",
            "action": "timeline_nav",
            "current_timecode": timeline.GetCurrentTimecode()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── 自动调色 ──
def auto_color(resolve, params):
    """
    自动调色（批量/单镜头）
    参数：
        contrast: 对比度倍数，默认 1.2
        saturation: 饱和度倍数，默认 1.1
        lut_name: LUT 名称，默认 "Rec.709"
        track_index: 视频轨道索引，默认 1
        batch_mode: True=处理整条轨道，False=只处理当前选中镜头
    """
    contrast = params.get("contrast", 1.2)
    saturation = params.get("saturation", 1.1)
    lut_name = params.get("lut_name", "Rec.709")
    track_index = params.get("track_index", 1)
    batch_mode = params.get("batch_mode", True)

    try:
        project = resolve.GetProjectManager().GetCurrentProject()
        if not project:
            return {"status": "error", "message": "No active project"}

        timeline = project.GetCurrentTimeline()
        if not timeline:
            return {"status": "error", "message": "No active timeline"}

        processed = 0
        failed = 0

        if batch_mode:
            # 批量模式：处理整条轨道
            clips = timeline.GetItemListInTrack("video", track_index)
            if not clips:
                return {"status": "error", "message": f"No clips found on video track {track_index}"}
            
            for clip in clips:
                try:
                    color = clip.GetColor()
                    color.SetContrast(contrast)
                    color.SetSaturation(saturation)
                    if lut_name:
                        color.ApplyLUT(lut_name)
                    processed += 1
                except Exception as e:
                    failed += 1
                    continue
        else:
            # 单镜头模式：只处理当前选中镜头
            item = timeline.GetCurrentTimelineItem()
            if not item:
                return {"status": "error", "message": "No clip selected"}
            
            clip_name = item.GetName()
            try:
                color = item.GetColor()
                color.SetContrast(contrast)
                color.SetSaturation(saturation)
                if lut_name:
                    color.ApplyLUT(lut_name)
                processed = 1
            except Exception as e:
                return {"status": "error", "message": f"Failed to color clip '{clip_name}': {str(e)}"}

        return {
            "status": "ok",
            "action": "auto_color",
            "processed": processed,
            "failed": failed,
            "settings": {
                "contrast": contrast,
                "saturation": saturation,
                "lut": lut_name,
                "track": track_index,
                "batch_mode": batch_mode
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# ── Action 分发路由 ──
ACTION_HANDLERS = {
    "color_wheel_adjust": wheel_adjust,
    "node_add": node_add,
    "lut_apply": lut_apply,
    "lut_remove": lut_remove,
    "node_reset": node_reset,
    "magic_mask": magic_mask,
    "power_window": power_window,
    "scope_read": scope_read,
    "project_load": project_load,
    "timeline_nav": timeline_nav,
    "auto_color": auto_color,
}


def parse_params(raw_params):
    """解析 key=value 格式参数"""
    params = {}
    for p in raw_params:
        if "=" in p:
            k, v = p.split("=", 1)
            k = k.strip()
            v = v.strip()
            # 类型推断
            if v.lower() == "true":
                params[k] = True
            elif v.lower() == "false":
                params[k] = False
            elif v.isdigit():
                params[k] = int(v)
            elif v.replace(".", "", 1).isdigit():
                params[k] = float(v)
            elif v.startswith("[") and v.endswith("]"):
                try:
                    params[k] = json.loads(v)
                except:
                    params[k] = v
            else:
                params[k] = v
    return params


def main():
    parser = argparse.ArgumentParser(description="DaVinci Resolve EAL")
    parser.add_argument("action", help="Action name (see action_schema.json)")
    parser.add_argument("params", nargs="*", help="Params in key=value format")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument("--dry-run", action="store_true", help="Validate without executing")

    args = parser.parse_args()

    if args.action not in ACTION_HANDLERS:
        available = list(ACTION_HANDLERS.keys())
        print(f"Unknown action: {args.action}")
        print(f"Available: {', '.join(available)}")
        sys.exit(1)

    params = parse_params(args.params)

    if args.dry_run:
        print(json.dumps({
            "action": args.action,
            "params": params,
            "dry_run": True
        }, indent=2))
        sys.exit(0)

    # 初始化 DR
    resolve = init_resolve()
    if not resolve:
        print(json.dumps({
            "status": "error",
            "message": "Cannot connect to DaVinci Resolve. Is it running with scripting enabled?"
        }, indent=2))
        sys.exit(1)

    handler = ACTION_HANDLERS[args.action]
    result = handler(resolve, params)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result["status"] == "ok":
            print(f"✅ {result['action']}: OK")
            for k, v in result.items():
                if k not in ["status", "action"]:
                    print(f"   {k}: {v}")
        else:
            print(f"❌ Error: {result.get('message', 'Unknown error')}")

    sys.exit(0 if result["status"] == "ok" else 1)


if __name__ == "__main__":
    main()
