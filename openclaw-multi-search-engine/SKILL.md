---
name: "multi-search-engine"
description: "多引擎搜索 — 聚合国内可用搜索引擎（百度/必应国内版/360/搜狗/头条），无需 API Key，不依赖 Brave Search，直接调用 web_fetch。自动排除不稳定/不可访问的网站（知乎等）。
---

# 多引擎搜索 v2.0.2

纯国内可用搜索引擎集成，不依赖任何境外服务或 API Key。

## 使用限制说明

**本 Skill 优先级最高**：凡涉及网页搜索的场景，一律使用本 Skill，不得调用 `web_search`（需 Brave API Key）。
- `web_search` 在本环境下不可用（未配置 Brave API Key）
- 所有搜索任务均通过本 Skill 的 `web_fetch` 调用国内搜索引擎完成

## 搜索引警（国内·稳定可用）

| 引擎 | URL 模板 | 备注 |
|------|----------|------|
| **百度** | `https://www.baidu.com/s?wd={keyword}` | 综合首选 |
| **必应（国内）** | `https://cn.bing.com/search?q={keyword}&ensearch=0` | 备选，广告少 |
| **360 搜索** | `https://www.so.com/s?q={keyword}` | 备选 |
| **搜狗** | `https://www.sogou.com/web?query={keyword}` | 支持中文分词 |
| **头条搜索** | `https://so.toutiao.com/search?keyword={keyword}` | 资讯类优先 |

## 示例

```javascript
// 基础搜索（百度）
web_fetch({"url": "https://www.baidu.com/s?wd=伊朗+美国+战争+最新"})

// 必应收索（近一天）
web_fetch({"url": "https://cn.bing.com/search?q=伊朗+美国+战争+最新&tbs=qdr:d"})

// 360 搜索
web_fetch({"url": "https://www.so.com/s?q=伊朗+战争+新闻"})

// 搜狗搜索
web_fetch({"url": "https://www.sogou.com/web?query=伊朗+美国+最新战况"})

// 头条搜索（资讯类）
web_fetch({"url": "https://so.toutiao.com/search?keyword=中东局势+伊朗+战争"})
```

## 排除站点

搜索结果中自动排除以下不稳定/不可访问网站：
- **知乎**（zhihu.com）— 反爬严格，经常 403
- **微信公众号搜一搜**（部分内容无法抓取）
- **境外网站**（Google、BuckDuckGo、Yahoo 等均不可用）

如需指定站内搜索，使用 `site:baidu.com` 等国内可访问站点。

## 高级搜索语法（百度/360/搜狗）

| 语法 | 示例 | 说明 |
|------|------|------|
| `"{关键词}"` | `"人工智能"` | 精确匹配 |
| `-关键词` | `人工智能 -机器学习` | 排除含该词的结果 |
| `关键词1 OR 关键词2` | `伊朗 OR 美军` | 任一包含即可 |
| `site:站点` | `site:sina.com.cn 新闻` | 指定站点（限国内可访问） |
| `filetype:pdf` | `filetype:pdf 报告` | 指定文件类型 |

## 时间筛选

在 URL 后追加时间参数：

| 参数 | 时间范围 |
|------|----------|
| `&tbs=qdr:d` | 最近一天 |
| `&tbs=qdr:w` | 最近一周 |
| `&tbs=qdr:m` | 最近一月 |
| `&tbs=qdr:y` | 最近一年 |

**百度格式**：`&fr=tabtime`（附加时间筛选）

## 推荐搜索策略

1. **综合新闻**：优先百度 + 必应，追加 `&tbs=qdr:d` 限定一天内
2. **深度资讯**：头条搜索（资讯聚合能力强）
3. **技术/专业内容**：搜狗（中文分词优）
4. **多引擎交叉验证**：同一关键词用2-3个引擎分别搜索，对比结果

## 注意事项

- 百度搜索结果含广告标记（"广告"），可忽略或用 `-广告` 部分过滤
- 360 搜索结果与百度类似，择一使用即可
- 搜狗支持微信搜索但不稳定，结果缺失属正常现象
-头条搜索侧重资讯，内容更新快但深度文章不如传统搜索引擎

## 文档

- `references/advanced-search.md` — 国内搜索进阶技巧
- `CHANGELOG.md` — 版本历史

## License

MIT
