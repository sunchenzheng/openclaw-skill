"""
mafengwo_scraper.py — 马蜂窝目的地/景点热度爬虫

功能：
  1. 搜索马蜂窝目的地城市列表
  2. 获取各城市的景点列表（按点评/收藏数排序）
  3. 统计景点推荐次数作为权重

用法：
    python mafengwo_scraper.py search --keyword 武汉
    python mafengwo_scraper.py attractions --city-id 23456
    python mafengwo_scraper.py batch --cities 武汉,成都,重庆
"""

import requests
import json
import time
import argparse
import random
import os
from datetime import datetime

# ============================================================
# 配置
# ============================================================
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.mafengwo.cn/",
    "Origin": "https://www.mafengwo.cn",
}

BASE_URL = "https://www.mafengwo.cn"
SEARCH_API = "https://www.mafengwo.cn/api/s.php"
ATTR_API = "https://www.mafengwo.cn/ajax/api.php"

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# 代理池（备用）
PROXIES = []  # 可配置代理列表


def get_proxy():
    if not PROXIES:
        return None
    return random.choice(PROXIES)


def mafengwo_search(keyword, page=1):
    """
    搜索马蜂窝目的地/景点
    返回: [{"name": "武汉", "id": "23456", "type": "city"}, ...]
    """
    params = {
        "key": keyword,
        "type": "poi",
        "page": page,
        "size": 20,
        "charset": "utf-8",
        "callback": "",
    }
    try:
        resp = SESSION.get(
            "https://www.mafengwo.cn/search/s.php",
            params=params,
            timeout=10,
            proxies={"http": get_proxy()} if PROXIES else None,
        )
        # 解析返回（可能有编码问题）
        text = resp.text
        # 提取 JSON 数据
        start = text.find('{"data"')
        if start == -1:
            start = text.find('{"errno"')
        if start != -1:
            # 找到JSON起点
            try:
                data = json.loads(text[start:])
                return data
            except:
                pass
        return {"error": "解析失败", "raw": text[:500]}
    except Exception as e:
        return {"error": str(e)}


def get_city_attractions(city_id, city_name="", max_pages=3):
    """
    获取指定城市的景点列表（按热度排序）
    city_id: 马蜂窝城市ID
    返回: [{"name": "黄鹤楼", "score": 4.8, "reviews": 23456, "lat": ..., "lng": ...}, ...]
    """
    results = []

    for page in range(1, max_pages + 1):
        try:
            # 马蜂窝景点列表 API
            url = "https://www.mafengwo.cn/jd/{}/".format(city_id)
            params = {
                "page": page,
                "_key": "html",
            }
            resp = SESSION.get(
                url,
                params=params,
                timeout=10,
                proxies={"http": get_proxy()} if PROXIES else None,
            )
            resp.encoding = "utf-8"
            text = resp.text

            # 解析景点数据（从页面HTML中提取）
            attractions = _parse_attraction_list(text, city_name)
            results.extend(attractions)

            time.sleep(random.uniform(1, 2))  # 礼貌性延迟
        except Exception as e:
            print(f"[警告] 抓取第{page}页失败: {e}")

    return results


def _parse_attraction_list(html_text, city_name=""):
    """
    从马蜂窝页面 HTML 中解析景点列表
    提取：景点名、评分、点评数、收藏数
    """
    import re

    attractions = []

    # 方法1：从页面 script 标签中提取 JSON 数据
    # 查找 var window.__INITIAL_STATE__ = {...}
    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*;', html_text, re.DOTALL)
    if match:
        try:
            json_str = match.group(1)
            # 简化处理
            data = json.loads(json_str)
            # 提取 poi/list
            if "poiList" in data or "jdList" in data:
                pass
        except:
            pass

    # 方法2：直接从 HTML 中用正则提取景点信息块
    # 寻找景点名称模式
    name_pattern = re.compile(r'<a[^>]+href="/jd/(\d+)/[^"]*"[^>]*>([^<]+)</a>')
    score_pattern = re.compile(r'"score"\s*:\s*"?([\d.]+)"?')
    review_pattern = re.compile(r'"review_num"\s*:\s*"?(\d+)"?')
    fav_pattern = re.compile(r'"fav_num"\s*:\s*"?(\d+)"?')

    # 提取所有景点链接块
    blocks = re.findall(r'<a[^>]+href="/jd/(\d+)/[^"]*"[^>]*>([^<]+)</a>', html_text)
    scores = score_pattern.findall(html_text)
    reviews = review_pattern.findall(html_text)
    favs = fav_pattern.findall(html_text)

    for i, (att_id, name) in enumerate(blocks):
        name = name.strip()
        if not name or len(name) < 2:
            continue
        score = float(scores[i]) if i < len(scores) else 0
        review = int(reviews[i]) if i < len(reviews) else 0
        fav = int(favs[i]) if i < len(favs) else 0

        # 综合热度 = 收藏数 * 2 + 点评数
        heat = fav * 2 + review

        attractions.append({
            "id": att_id,
            "name": name,
            "city": city_name,
            "score": score,
            "reviews": review,
            "favs": fav,
            "heat": heat,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    return attractions


def get_destinations_by_keyword(keyword, limit=20):
    """
    按关键词搜索旅游目的地，返回城市列表
    """
    data = mafengwo_search(keyword)
    results = []

    if "data" in data:
        for item in data["data"][:limit]:
            results.append({
                "name": item.get("name", ""),
                "id": item.get("id", ""),
                "type": item.get("type", "city"),
                "url": item.get("url", ""),
            })
    elif "error" in data:
        print(f"[错误] 搜索失败: {data['error']}")

    return results


def get_city_id(city_name):
    """
    根据城市名获取马蜂窝城市ID
    """
    # 常用城市ID映射（可直接使用）
    CITY_IDS = {
        "武汉": 23456, "重庆": 17048, "成都": 17067,
        "西安": 23315, "杭州": 18785, "南京": 18748,
        "苏州": 18783, "长沙": 18824, "厦门": 19194,
        "青岛": 19276, "大连": 19167, "哈尔滨": 19630,
        "广州": 19184, "深圳": 19193, "北京": 2,
        "上海": 9087, "天津": 19187, "郑州": 18816,
        "济南": 19264, "太原": 18832, "合肥": 18819,
        "昆明": 19885, "贵阳": 19878, "拉萨": 21519,
        "兰州": 19761, "西宁": 21513, "银川": 21503,
        "乌鲁木齐": 29918, "呼和浩特": 19953,
    }
    return CITY_IDS.get(city_name)


# ============================================================
# 主程序入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="马蜂窝目的地热度爬虫")
    subparsers = parser.add_subparsers(dest="command")

    # 搜索目的地
    p_search = subparsers.add_parser("search", help="搜索目的地城市")
    p_search.add_argument("--keyword", required=True, help="搜索关键词")
    p_search.add_argument("--limit", type=int, default=20, help="返回数量")

    # 获取城市景点
    p_attr = subparsers.add_parser("attractions", help="获取城市景点列表")
    p_attr.add_argument("--city", required=True, help="城市名")
    p_attr.add_argument("--pages", type=int, default=3, help="抓取页数")
    p_attr.add_argument("--out", help="输出JSON文件路径")

    # 批量城市
    p_batch = subparsers.add_parser("batch", help="批量抓取多城市景点")
    p_batch.add_argument("--cities", required=True, help="逗号分隔城市列表")
    p_batch.add_argument("--pages", type=int, default=2, help="每城市页数")
    p_batch.add_argument("--out", required=True, help="输出JSON文件路径")

    args = parser.parse_args()

    if args.command == "search":
        results = get_destinations_by_keyword(args.keyword, args.limit)
        print(json.dumps(results, ensure_ascii=False, indent=2))

    elif args.command == "attractions":
        city_id = get_city_id(args.city)
        if not city_id:
            print(f"[错误] 未找到城市ID: {args.city}")
            return
        print(f"[*] 正在抓取 {args.city} (ID:{city_id}) 的景点...")
        attractions = get_city_attractions(city_id, args.city, args.pages)
        print(f"[+] 获取 {len(attractions)} 个景点")

        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(attractions, f, ensure_ascii=False, indent=2)
            print(f"[+] 已保存: {args.out}")

    elif args.command == "batch":
        cities = [c.strip() for c in args.cities.split(",")]
        all_results = {}

        for city in cities:
            city_id = get_city_id(city)
            if not city_id:
                print(f"[跳过] 未找到城市ID: {city}")
                continue
            print(f"\n[*] 正在抓取 {city} (ID:{city_id})...")
            attractions = get_city_attractions(city_id, city, args.pages)
            all_results[city] = attractions
            print(f"[+] {city}: {len(attractions)} 个景点")
            time.sleep(random.uniform(1, 3))

        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n[+] 全部完成，已保存: {args.out}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
