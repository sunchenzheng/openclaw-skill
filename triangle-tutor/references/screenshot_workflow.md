# 题目截图收集工作流

> 更新时间：2026-04-01
> 策略：网上优先 → 视频截图次之

---

## 一、截图收集优先级

| 优先级 | 来源 | 说明 |
|--------|------|------|
| **P1** | 网络图片搜索 | 直接搜题目的现成图片（百度/Google/小红书/微信公众号） |
| **P2** | 视频截图-题目帧 | 视频中题目完整展示的那一帧 |
| **P3** | 视频截图-解答帧 | 解答完整展示的那一帧（翻页则多帧）|

---

## 二、文件夹结构

```
triangle-tutor/
├── questions/
│   ├── images/                  # 已有图片（img001.png 等）
│   ├── q001-q017/              # ⭐题目（每题一个文件夹）
│   │   ├── q001_question.png   # 题目截图
│   │   ├── q001_answer_1.png   # 解答截图（第一帧/页）
│   │   ├── q001_answer_2.png   # 解答截图（第二帧/页，如翻页）
│   │   └── q001_meta.json      # 元数据（来源视频BV号/时间戳/来源链接）
│   ├── q018-q056/              # ⭐⭐题目
│   ├── q057-q090/              # ⭐⭐⭐题目
│   ├── q091-q117/              # ⭐⭐⭐⭐题目
│   ├── q118-q150/              # ⭐⭐⭐⭐⭐题目
│   └── screenshot_log.json     # 截图收集日志
└── scripts/
    ├── screenshot_from_video.py  # 视频截图脚本（ffmpeg）
    └── screenshot_workflow.py    # 截图工作流自动化
```

---

## 三、元数据格式（qXXX_meta.json）

```json
{
  "question_id": "Q091",
  "difficulty": "⭐⭐⭐⭐",
  "title": "△ABC，AB=AC，∠A=20°，D在AB上，∠ACD=30°...",
  "source": {
    "primary": {
      "type": "video",
      "bv_id": "BV16VVnz3EsU",
      "timestamp_question": "00:12:34",
      "timestamp_answer": "00:15:20",
      "url": "https://www.bilibili.com/video/BV16VVnz3EsU"
    },
    "fallback": {
      "type": "image_search",
      "query": "BV16VVnz3EsU Q091 三角形 AB=AC ∠A=20°",
      "url_found": "https://xxx.com/xxx.jpg"
    }
  },
  "screenshots": {
    "question": "q091_question.png",
    "answers": ["q091_answer_1.png"]
  },
  "status": "collected",  // pending / collected / failed
  "collected_at": "2026-04-01",
  "notes": "题目帧在视频00:12:34，解答在00:15:20"
}
```

---

## 四、截图工作流（手动/半自动）

### Step 1：网络图片搜索（首选）

```
搜索关键词格式：
"{BV号} {题目关键词}" 或 "{题号} {知识点关键词}"
例如：BV16VVnz3EsU 全等三角形 20° 等腰

图片来源优先级：
1. 百度图片搜索
2. 小红书（很多学生分享题目截图）
3. 微信公众号文章
4. 学科网/万唯中考等教辅官网
```

### Step 2：视频截图（次选）

**工具**：ffmpeg（从视频中截取指定时间戳的帧）

```bash
# 安装确认
ffmpeg -version

# 截取单个帧（题目帧）
ffmpeg -ss 00:12:34 -i "video.mp4" -frames:v 1 -q:v 2 q091_question.png

# 截取多个解答帧（如翻页）
ffmpeg -ss 00:15:20 -i "video.mp4" -frames:v 1 -q:v 2 q091_answer_1.png
ffmpeg -ss 00:16:45 -i "video.mp4" -frames:v 1 -q:v 2 q091_answer_2.png

# 参数说明：
# -ss: 时间位置（时分秒）
# -i: 输入视频
# -frames:v 1: 只截取1帧
# -q:v 2: 输出质量（2为高质量）
```

### Step 3：记录元数据

每收集完一道题的截图，更新 `qXXX_meta.json` 和 `screenshot_log.json`

---

## 五、收集状态追踪

```json
// screenshot_log.json
{
  "update_date": "2026-04-01",
  "total_questions": 180,
  "collected": {
    "questions_with_screenshot": 0,
    "questions_with_answer_screenshot": 0,
    "by_difficulty": {
      "*": {"total": 17, "screenshots": 0},
      "**": {"total": 39, "screenshots": 0},
      "***": {"total": 54, "screenshots": 0},
      "****": {"total": 35, "screenshots": 0},
      "*****": {"total": 35, "screenshots": 0}
    }
  },
  "pending": 180,
  "failed": []
}
```

---

## 六、注意事项

1. **截图质量**：题目和解答图片文字必须清晰可读，分辨率不低于 1280x720
2. **完整性**：题目截图需包含完整题目条件；解答截图需包含完整解题步骤
3. **翻页处理**：解答过程跨多页/多帧时，每页/每帧都需截图
4. **命名规范**：`q{编号}_{类型}_{序号}.png`，例如 `q091_answer_2.png`
5. **来源标注**：每张截图的元数据必须记录来源（视频BV号+时间戳 或 图片URL）

---

*本文件定义了题目截图收集的规范和流程*
