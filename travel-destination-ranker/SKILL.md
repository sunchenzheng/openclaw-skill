---
name: travel-destination-ranker
description: "旅游目的地热度排行工具。通过爬取马蜂窝景点推荐数据（收藏/点评数）结合高德地图实时搜索/导航量，对多个旅游城市进行综合热度排行。当用户需要：（1）比较多个城市的旅游热度；（2）查询某城市的热门景点排名；（3）获取目的地实时交通拥堵情况时使用。数据来源：马蜂窝（景点热度）、高德地图（搜索量/路况）。触发场景：'帮我比较武汉、成都、重庆哪个更值得去' / '给我推荐一个周末游的城市排行' / '查一下各城市的景点热度排名'"
---

# 旅游目的地热度排行技能

通过**马蜂窝景点热度** × **高德地图实时流量**双数据源，计算城市综合旅游热度排行。

---

## 核心算法

```
综合热度得分 = α × log(景点总热度+1) × 景点数量^0.3
             + β × log(高德搜索量+1)

其中：
  景点总热度 = 收藏数×2 + 点评数
  α = 0.5（景点热度权重）
  β = 0.5（高德流量权重）
```

---

## 脚本说明

| 脚本 | 作用 |
|------|------|
| `scripts/mafengwo_scraper.py` | 马蜂窝爬虫（城市搜索 + 景点列表） |
| `scripts/gaode_api.py` | 高德地图 API（POI搜索 + 实时路况 + 天气） |
| `scripts/rank_destinations.py` | 综合排行主程序（整合两个数据源） |

---

## 使用方法

### 前提配置

**1. 高德地图 Key（必需）**
```
申请地址：https://lbs.amap.com/
免费额度：10000次/天 Web服务 API
```
设置环境变量：
```bash
set GAODE_KEY=你的Key
```
或直接用 `--gaode-key` 参数传入。

**2. 马蜂窝爬虫（无需 Key，直接可用）**
- 无需登录/注册
- 有基础反爬限制，控制请求频率（已内置延迟）

---

### 快速开始

```bash
# 多城市排行（示例）
python scripts/rank_destinations.py rank `
    --cities 武汉,成都,重庆,西安,杭州,南京 `
    --gaode-key 你的高德Key `
    --pages 2 `
    --out result.json `
    --report report.md

# 单城市详细分析
python scripts/rank_destinations.py analyze `
    --city 武汉 `
    --gaode-key 你的高德Key

# 仅爬取马蜂窝景点数据
python scripts/mafengwo_scraper.py batch `
    --cities 武汉,成都,重庆 `
    --pages 2 `
    --out attractions.json

# 仅查高德搜索量
python scripts/gaode_api.py batch `
    --key 你的高德Key `
    --cities 武汉,成都,重庆 `
    --keyword 旅游景点 `
    --out gaode_search.json
```

---

### 输出示例

**排行榜输出（JSON）**
```json
{
  "rank": 1,
  "city": "成都",
  "scores": {
    "attraction_heat": 45678,
    "gaode_search_volume": 123456,
    "raw_score": 42.3
  },
  "attraction": {
    "attraction_count": 42,
    "total_heat": 45678,
    "top_attractions": [
      {"name": "宽窄巷子", "score": 4.8, "favs": 2345, "reviews": 890}
    ]
  },
  "gaode": {
    "total_search_volume": 123456,
    "traffic_summary": {"smooth": 12, "slow": 5, "congested": 2}
  }
}
```

**Markdown 报告**
```markdown
| 排名 | 城市 | 综合得分 | 景点热度 | 高德搜索量 | 拥堵道路 |
|------|------|----------|----------|------------|---------|
| 1 | 成都 | 42.3 | 45678 | 123456 | 2/19 |
```

---

## 数据来源说明

### 马蜂窝（景点热度）
- **数据**：城市景点列表 + 收藏数 + 点评数 + 评分
- **覆盖**：全国主要旅游城市
- **更新周期**：每次爬取为实时数据
- **反爬策略**：内置随机延迟，自动重试

### 高德地图（实时流量）
- **搜索量**：用 `旅游景点` 等关键词搜索结果数作为代理指标
- **路况**：实时拥堵道路统计（畅通/缓行/拥堵）
- **注意**：高德不直接提供"导航次数"数据，搜索量是近似替代

---

## 限制与注意事项

1. **高德 API Key**：必须有效 Key 才能调用成功
2. **马蜂窝反爬**：每次请求间隔 1-2 秒，大规模抓取可能被封 IP
3. **数据完整性**：马蜂窝页面结构可能变化，解析逻辑需要定期维护
4. **搜索量代理**：高德搜索结果数 ≠ 实际导航次数，存在偏差
5. **权重可调**：WEIGHT_CONFIG 中 alpha/beta 可根据实际效果调整

---

## 文件结构

```
travel-destination-ranker/
├── SKILL.md
├── scripts/
│   ├── mafengwo_scraper.py      # 马蜂窝爬虫
│   ├── gaode_api.py             # 高德 API 调用
│   └── rank_destinations.py     # 综合排行主程序
└── references/
    └── city_ids.json            # 常用城市 ID 映射（可选）
```
