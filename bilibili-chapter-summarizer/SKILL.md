---
name: "bilibili-chapter-summarizer"
description: "B站视频 AI 章节总结。对 B站视频进行下载，按时间均匀分段截图，用 AI 分析每段内容，识别章节边界，生成每章节的摘要。触发场景：用户发来 B站视频链接，希望了解视频内容结构和各章节重点。"
---

# B站视频 AI 章节总结

## 核心流程

```
① 传入 B站 URL
② 提取视频元信息（标题/时长/封面）
③ 下载视频（yt-dlp）
④ 按 N 段均匀截帧
⑤ AI 分析每段截图 → 识别内容主题
⑥ 识别章节切换点 → 生成章节边界
⑦ 输出章节列表（含时间戳 + 内容摘要）
```

## 工具依赖

| 工具 | 路径 |
|------|------|
| yt-dlp | `C:\Users\123\AppData\Local\Microsoft\WinGet\Packages\yt-dlp.yt-dlp_Microsoft.Winget.Source_8wekyb3d8bbwe\yt-dlp.exe` |
| FFmpeg | `C:\Users\123\AppData\Local\Microsoft\WinGet\Packages\yt-dlp.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-N-123074-g4e32fb4c2a-win64-gpl\bin\ffmpeg.exe` |

## 参数说明

- **输入**：B站视频 URL（如 `https://www.bilibili.com/video/BVxxxxxx`）
- **输出章节数**：默认 5 段（可调整）
- **截帧间隔**：总时长 / 段数

## 执行示例

```bash
# Step 1: 获取视频信息
yt-dlp --dump-json <url>

# Step 2: 下载 1080P
yt-dlp -f 30080 --no-playlist -o video.mp4 <url>

# Step 3: 截帧（每30秒截一帧）
for sec in 30 60 90 120 150 180 210 240 270 300; do
    ffmpeg -ss $sec -i video.mp4 -vframes 1 -update 1 frame_$sec.jpg
done
```

## AI 分析指令

发送给 AI 的分析提示词：

```
你是视频内容分析专家。以下是该视频在各个时间点截取的帧描述。

请完成两项任务：
1. 【章节划分】根据内容变化，将视频划分为 N 个逻辑章节，给出每个章节的【开始时间】和【结束时间】
2. 【章节摘要】对每个章节，用 1-2 句话总结该部分的核心内容

时间帧格式：
- 0:30 → [帧描述]
- 1:00 → [帧描述]
...

输出格式：
## 章节概览
| 章节 | 时间范围 | 内容摘要 |
|------|----------|----------|

## 详细章节
### 章节1：[章节主题]
- 时间：0:30 - 1:45
- 要点：...
```

## 注意事项

- B站视频需要字幕必须登录，大部分视频无字幕可用
- 优先选择讲解类视频（数学/物理/英语等学科），画面内容稳定，AI 识别效果更好
- 截帧数量建议：5分钟以内视频截 8-10 帧；5-15 分钟截 15-20 帧；15分钟以上截 20-30 帧
- 几何/数学题目类视频不适合此方法（黑板/白板内容文字多，AI 识别困难），建议用题目图片直接讲解
