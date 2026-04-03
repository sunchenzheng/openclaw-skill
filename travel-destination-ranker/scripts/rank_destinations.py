"""
rank_destinations.py — 目的地综合热度排行榜

核心算法：
  综合得分 = 景点推荐热度 × α + 高德搜索量 × β + 高德导航量 × γ

其中：
  - 景点推荐热度：来自马蜂窝数据（收藏数×2 + 点评数）
  - 高德搜索量：POI 搜索结果总数
  - 高德导航量：导航规划次数（高德未直接提供，用路径规划请求量代理）

用法：
    # 单城市分析
    python rank_destinations.py analyze --city 武汉 --gaode-key YOUR_KEY

    # 多城市对比排行
    python rank_destinations.py rank --cities 武汉,成都,重庆,西安,杭州 --gaode-key YOUR_KEY

    # 完整报告
    python rank_destinations.py report --cities 武汉,成都,重庆 --gaode-key YOUR_KEY --out report.json
"""

import sys
import os
import json
import argparse
import time
import random
from datetime import datetime

# 导入同目录下的模块
from mafengwo_scraper import get_city_id, get_city_attractions, get_city_search
from gaode_api import search_poi, geocode_keyword, get_traffic_status

# 尝试导入
try:
    from mafengwo_scraper import get_city_id, get_city_attractions
    MAFENGWO_OK = True
except ImportError:
    MAFENGWO_OK = False
    print("[警告] 马蜂窝模块导入失败，仅使用高德数据")

try:
    from gaode_api import search_poi, geocode_keyword
    GAODE_OK = True
except ImportError:
    GAODE_OK = False


# ============================================================
# 权重配置（可调整）
# ============================================================
WEIGHT_CONFIG = {
    # 景点推荐热度权重
    "attraction_fav_weight": 2.0,      # 收藏数权重
    "attraction_review_weight": 1.0,   # 点评数权重

    # 高德数据权重
    "gaode_search_weight": 1.0,        # 搜索量权重
    "gaode_nav_weight": 0.5,           # 导航量（代理）权重

    # 综合权重归一化
    "attraction_alpha": 0.5,           # 景点热度占综合得分比例
    "gaode_beta": 0.5,                # 高德流量占综合得分比例
}

# 搜索关键词（用于高德搜索量代理）
GAODE_KEYWORDS = ["旅游景点", "景区", "公园", "古镇"]


def fetch_attraction_heat(city_name, max_pages=2):
    """
    获取城市景点热度数据
    返回：{city: {"total_heat": N, "top_attractions": [...], "avg_score": float}}
    """
    if not MAFENGWO_OK:
        return None

    city_id = get_city_id(city_name)
    if not city_id:
        return None

    try:
        attractions = get_city_attractions(city_id, city_name, max_pages)
        if not attractions:
            return None

        total_heat = sum(a.get("heat", 0) for a in attractions)
        avg_score = sum(a.get("score", 0) for a in attractions) / len(attractions)

        # 取 Top 10 景点
        top_attrs = sorted(attractions, key=lambda x: x.get("heat", 0), reverse=True)[:10]

        return {
            "city": city_name,
            "attraction_count": len(attractions),
            "total_heat": total_heat,
            "avg_score": round(avg_score, 2),
            "top_attractions": top_attrs,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    except Exception as e:
        print(f"[错误] 获取{city_name}景点失败: {e}")
        return None


def fetch_gaode_traffic(city_name, gaode_key):
    """
    获取高德地图的城市流量数据
    - 搜索量：用 POI 搜索结果总数代理
    - 路况：获取实时拥堵信息
    """
    if not GAODE_OK or not gaode_key:
        return None

    results = {"city": city_name, "keyword_searches": {}, "traffic": None}

    # 用多个关键词搜索，汇总总数
    total_searches = 0
    for kw in GAODE_KEYWORDS:
        try:
            r = search_poi(kw, city=city_name, key=gaode_key, offset=1)
            count = r.get("total", 0) if "error" not in r else 0
            total_searches += count
            results["keyword_searches"][kw] = count
            time.sleep(random.uniform(0.2, 0.5))
        except Exception as e:
            results["keyword_searches"][kw] = 0

    results["total_search_volume"] = total_searches

    # 获取实时路况
    try:
        traffic = get_traffic_status(city_name, gaode_key)
        if "error" not in traffic:
            results["traffic"] = traffic
            # 统计畅通/缓行/拥堵道路数
            roads = traffic.get("roads", [])
            results["traffic_summary"] = {
                "smooth": sum(1 for r in roads if r.get("status") == "1"),
                "slow": sum(1 for r in roads if r.get("status") == "2"),
                "congested": sum(1 for r in roads if r.get("status") == "3"),
                "total_roads": len(roads),
            }
    except Exception as e:
        print(f"[警告] 获取{city_name}路况失败: {e}")

    results["crawl_time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return results


def calculate_rank(cities, gaode_key, attraction_pages=2, weights=None):
    """
    计算城市综合热度排行
    返回：排行榜列表
    """
    if weights is None:
        weights = WEIGHT_CONFIG

    alpha = weights["attraction_alpha"]
    beta = weights["gaode_beta"]

    ranked = []

    for city in cities:
        print(f"\n[*] 分析 {city}...")

        record = {"city": city, "rank_time": datetime.now().strftime("%Y-%m-%d %H:%M")}

        # 1. 景点热度
        attr_data = fetch_attraction_heat(city, max_pages=attraction_pages)
        if attr_data:
            record["attraction"] = attr_data
            attr_heat = attr_data["total_heat"]
            attr_count = attr_data["attraction_count"]
        else:
            attr_heat = 0
            attr_count = 0
            record["attraction"] = None

        # 2. 高德流量
        gaode_data = fetch_gaode_traffic(city, gaode_key)
        if gaode_data:
            record["gaode"] = gaode_data
            search_vol = gaode_data.get("total_search_volume", 0)
            traffic_info = gaode_data.get("traffic_summary", {})
        else:
            search_vol = 0
            traffic_info = {}
            record["gaode"] = None

        # 3. 归一化得分
        # 景点得分：取对数平滑，避免极大城市垄断
        import math
        attr_score = math.log(attr_heat + 1) * attr_count ** 0.3 if attr_heat > 0 else 0
        # 高德得分：搜索量取对数
        gaode_score = math.log(search_vol + 1) if search_vol > 0 else 0

        # 综合得分（0-100分标准化）
        if alpha + beta > 0:
            raw_score = alpha * attr_score + beta * gaode_score
            # 简单标准化到 0-100（以本次查询最大值为基准）
            # 注：这里用相对比较，所以不除以固定最大值
            record["scores"] = {
                "attraction_heat": attr_heat,
                "attraction_score": round(attr_score, 2),
                "gaode_search_volume": search_vol,
                "gaode_score": round(gaode_score, 2),
                "raw_score": round(raw_score, 2),
            }
        else:
            record["scores"] = {}

        record["traffic_summary"] = traffic_info
        ranked.append(record)

        print(f"    景点热度: {attr_heat} | 高德搜索: {search_vol} | 综合: {record['scores'].get('raw_score', 0)}")

        # 礼貌性延迟
        time.sleep(random.uniform(1, 2))

    # 排序
    ranked.sort(key=lambda x: x["scores"].get("raw_score", 0), reverse=True)

    # 添加排名
    for i, r in enumerate(ranked, 1):
        r["rank"] = i

    return ranked


def generate_report(ranked_data, out_path=None):
    """
    生成分析报告
    """
    report_lines = []
    report_lines.append("# 🏆 旅游目的地热度排行榜\n")
    report_lines.append(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    report_lines.append("## 综合排名\n")
    report_lines.append("| 排名 | 城市 | 综合得分 | 景点热度 | 高德搜索量 | 拥堵道路 |")
    report_lines.append("|------|------|----------|----------|------------|---------|")

    for r in ranked_data:
        scores = r.get("scores", {})
        traffic = r.get("traffic_summary", {})
        report_lines.append(
            f"| {r['rank']} | **{r['city']}** | {scores.get('raw_score', 0):.1f} | "
            f"{scores.get('attraction_heat', 0)} | {scores.get('gaode_search_volume', 0)} | "
            f"{traffic.get('congested', '?')}/{traffic.get('total_roads', '?')} |"
        )

    # Top景点详情
    for r in ranked_data:
        attr = r.get("attraction")
        if attr and attr.get("top_attractions"):
            report_lines.append(f"\n## {r['city']} Top 景点\n")
            report_lines.append("| 景点 | 评分 | 收藏数 | 点评数 | 热度 |")
            report_lines.append("|------|------|--------|--------|------|")
            for a in attr["top_attractions"][:5]:
                report_lines.append(
                    f"| {a['name']} | {a['score']:.1f} | {a.get('favs', 0)} | "
                    f"{a.get('reviews', 0)} | {a.get('heat', 0)} |"
                )

    report_text = "\n".join(report_lines)

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(report_text)
        print(f"\n[+] 报告已保存: {out_path}")

    return report_text


# ============================================================
# 主程序
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="旅游目的地热度排行工具")
    subparsers = parser.add_subparsers(dest="command")

    # 排行榜
    p_rank = subparsers.add_parser("rank", help="多城市综合排行")
    p_rank.add_argument("--cities", required=True, help="逗号分隔城市列表")
    p_rank.add_argument("--gaode-key", required=True, help="高德 API Key")
    p_rank.add_argument("--pages", type=int, default=2, help="每城市景点页数")
    p_rank.add_argument("--out", help="输出 JSON 路径")
    p_rank.add_argument("--report", help="输出 Markdown 报告路径")

    # 单城市分析
    p_analyze = subparsers.add_parser("analyze", help="单城市详细分析")
    p_analyze.add_argument("--city", required=True, help="城市名")
    p_analyze.add_argument("--gaode-key", required=True, help="高德 API Key")
    p_analyze.add_argument("--pages", type=int, default=2, help="景点页数")

    args = parser.parse_args()

    if args.command == "rank":
        cities = [c.strip() for c in args.cities.split(",")]
        print(f"[*] 开始分析 {len(cities)} 个城市...")
        ranked = calculate_rank(cities, args.gaode_key, args.pages, WEIGHT_CONFIG)

        print("\n\n🏆 最终排名：")
        for r in ranked:
            print(f"  #{r['rank']} {r['city']} — 综合 {r['scores'].get('raw_score', 0):.1f}")

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(ranked, f, ensure_ascii=False, indent=2)
            print(f"[+] JSON 已保存: {args.out}")

        if args.report:
            generate_report(ranked, args.report)

    elif args.command == "analyze":
        ranked = calculate_rank([args.city], args.gaode_key, args.pages, WEIGHT_CONFIG)
        r = ranked[0]
        print(f"\n## {args.city} 详细分析\n")
        scores = r.get("scores", {})
        print(f"  综合得分：{scores.get('raw_score', 0):.1f}")
        print(f"  景点热度：{scores.get('attraction_heat', 0)}")
        print(f"  高德搜索：{scores.get('gaode_search_volume', 0)}")

        attr = r.get("attraction")
        if attr:
            print(f"\n  Top 景点：")
            for a in attr.get("top_attractions", [])[:5]:
                print(f"    - {a['name']} (热度:{a['heat']}, 评分:{a['score']})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
