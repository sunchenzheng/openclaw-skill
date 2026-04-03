---
name: davinci-eal
description: "DaVinci Resolve 调色自动化 EAL（Execution Abstraction Layer）。当用户描述调色意图（如'降低高光'、'给暗部加暖色'、'应用某个LUT'），使用本技能将自然语言转化为 DR API Action 并执行。触发场景：NL 调色指令、截图诊断后执行、批量调色任务。"
---

# DaVinci Resolve EAL 技能

将自然语言调色指令转化为 DaVinci Resolve API 操作并执行。

## 前置条件

1. DaVinci Resolve **必须正在运行**
2. DR 已开启 **Scripting API**：
   - macOS: `Preferences → Scripts → Enable Scripting and Assistant`
   - Windows: `Preferences → Script → Enable Scripting`

> Remote API (port 8080) 不需要开启，本 EAL 使用原生 Python Scripting API。

## 核心文件

| 文件 | 作用 |
|------|------|
| `scripts/davinci_eal.py` | EAL 执行器（Action 分发 → DR API）|
| `references/action_schema.json` | 原子动作定义（输入/输出规范）|

## 使用方式

### 直接调用（命令行）

```bash
python skills/davinci-eal/scripts/davinci_eal.py <action> key=value [key=value...]

# 示例：调整 gamma 轮，降低饱和度
python skills/davinci-eal/scripts/davinci_eal.py color_wheel_adjust wheel=gamma saturation=0.8

# 示例：添加一个串行节点
python skills/davinci-eal/scripts/davinci_eal.py node_add node_type=serial

# 示例：应用 LUT
python skills/davinci-eal/scripts/davinci_eal.py lut_apply lut_name=Filmgrade node_index=1

# 示例：重置节点
python skills/davinci-eal/scripts/davinci_eal.py node_reset node_index=1 scope=all

# 示例：Magic Mask 创建
python skills/davinci-eal/scripts/davinci_eal.py magic_mask action=create subject=face

# 示例：读取波形示波器
python skills/davinci-eal/scripts/davinci_eal.py scope_read scope_type=waveform --json
```

### 通过 OpenClaw 自然语言调用

用户说："把画面高光降低一点"
→ EAL 执行 `color_wheel_adjust wheel=gain luminance=-0.3`

用户说："给暗部加暖色"
→ EAL 执行 `color_wheel_adjust wheel=lift hue=30 saturation=1.1`

用户说："应用 Filmgrade LUT"
→ EAL 执行 `lut_apply lut_name=Filmgrade`

用户说："Magic Mask 跟踪人脸"
→ EAL 执行 `magic_mask action=create subject=face`

## 可用 Action

### 调色类

| Action | 说明 | 关键参数 |
|--------|------|---------|
| `color_wheel_adjust` | 颜色轮调整 | `wheel` (lift/gamma/gain/offset), `hue`, `saturation`, `luminance` |
| `curve_adjust` | 曲线编辑 | `curve_type`, `points` |
| `lut_apply` | 应用 LUT | `lut_name`, `node_index` |
| `lut_remove` | 移除 LUT | `node_index` |
| `node_reset` | 重置节点 | `node_index`, `scope` |
| `node_add` | 添加节点 | `node_type` (serial/parallel/layer/compound) |

### 遮罩类

| Action | 说明 | 关键参数 |
|--------|------|---------|
| `power_window` | Power Window 遮罩 | `shape`, `points`, `invert`, `feather` |
| `auto_color` | 自动调色（批量/单镜头） | `contrast`, `saturation`, `lut_name`, `track_index`, `batch_mode` |
| `magic_mask` | Magic Mask 跟踪 | `action` (create/track/refine/reset), `subject` |

### 导航/信息类

| Action | 说明 | 关键参数 |
|--------|------|---------|
| `scope_read` | 读取示波器数据 | `scope_type` (waveform/rgb_parade/vectorscope/histogram) |
| `timeline_nav` | 时间线导航 | `action`, `timecode` |
| `project_load` | 加载项目/时间线 | `project_name`, `timeline_name` |

## 自然语言 → Action 映射规则

OpenClaw 收到 NL 指令后，按以下规则映射：

```
高光过曝 / 降低高光 / 亮部太亮
  → color_wheel_adjust wheel=gain luminance=-0.2~-0.5

暗部不足 / 提亮暗部 / 阴影太暗
  → color_wheel_adjust wheel=lift luminance=+0.1~+0.3

中间调偏冷 / 暖色化
  → color_wheel_adjust wheel=gamma hue=+15~+45 (偏黄/暖)

饱和度太高 / 色彩太浓
  → color_wheel_adjust wheel=[any] saturation=0.7~0.9

饱和度太低 / 色彩太淡
  → color_wheel_adjust wheel=[any] saturation=1.1~1.3

应用 [LUT名]
  → lut_apply lut_name=[LUT名]

新建调色节点 / 添加节点
  → node_add node_type=serial

重置当前调色
  → node_reset scope=all

跟踪人脸 / Magic Mask 人脸
  → magic_mask action=create subject=face

跟踪人体 / Magic Mask 身体
  → magic_mask action=create subject=body

批量自动调色 / 给所有镜头套 LUT
  → auto_color batch_mode=true lut_name=Rec.709

只调当前镜头 / 选中镜头加对比度
  → auto_color batch_mode=false contrast=1.2 saturation=1.1

圆形遮罩 / 圆形 Power Window
  → power_window shape=circle points=[cx,cy,r]

读取波形示波器
  → scope_read scope_type=waveform
```

## 执行流程

```
用户 NL 指令
    ↓
OpenClaw 解析意图 → Action + Params
    ↓
OpenClaw 执行: exec python davinci_eal.py <action> ...
    ↓
DR Scripting API 调用
    ↓
返回 JSON 结果 {status, action, ...}
    ↓
OpenClaw 反馈用户（自然语言）
```

## DR 未运行 / 连接失败

如果 EAL 报错 `Cannot connect to DaVinci Resolve`：
1. 确认 DR 正在运行
2. 确认已开启 Scripting API（Preferences → Script）
3. 尝试重启 DR 后重新执行

## EAL 扩展

如需新增 Action：
1. 在 `action_schema.json` 添加 action 定义
2. 在 `davinci_eal.py` 实现 handler 函数
3. 注册到 `ACTION_HANDLERS` 字典
