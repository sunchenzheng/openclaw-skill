"""
gaode_api.py — 高德地图开放平台 API 调用

前提：需要申请高德开放平台账号，获取 Web服务API Key
申请地址：https://lbs.amap.com/

功能：
  1. 关键词搜索 POI（获取搜索量）
  2. 实时路况（获取拥堵指数）
  3. 天气查询（补充功能）
  4. 地理编码（城市名 → 经纬度）

用法：
    python gaode_api.py search --key YOUR_KEY --keyword 武汉
    python gaode_api.py traffic --key YOUR_KEY --city 武汉
    python gaode_api.py weather --key YOUR_KEY --city 武汉
"""

import requests
import json
import argparse
from datetime import datetime

# ============================================================
# 高德 API 配置
# ============================================================
GAODE_API_BASE = "https://restapi.amap.com/v3"

# 用户配置的高德 Key（从环境变量或配置文件读取）
GAODE_KEY = os.environ.get("GAODE_KEY", "")

# 常用城市行政区划编码
CITY_CODES = {
    "武汉": "420100", "重庆": "500100", "成都": "510100",
    "西安": "610100", "杭州": "330100", "南京": "320100",
    "苏州": "320500", "长沙": "430100", "厦门": "350200",
    "青岛": "370200", "大连": "210200", "哈尔滨": "230100",
    "广州": "440100", "深圳": "440300", "北京": "110000",
    "上海": "310000", "天津": "120000", "郑州": "410100",
    "济南": "370100", "太原": "140100", "合肥": "340100",
    "昆明": "530100", "贵阳": "520100", "拉萨": "540100",
    "兰州": "620100", "西宁": "630100", "银川": "640100",
    "乌鲁木齐": "650100", "呼和浩特": "150100",
}

import os


def geocode_keyword(keyword, key):
    """
    地理编码：将城市/地点名称转为经纬度
    """
    url = f"{GAODE_API_BASE}/geocode/geo"
    params = {"key": key, "address": keyword}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    if data.get("status") == "1" and data.get("geocodes"):
        g = data["geocodes"][0]
        return {
            "province": g.get("province", ""),
            "city": g.get("city", ""),
            "district": g.get("district", ""),
            "lng": float(g.get("location", ",").split(",")[0]),
            "lat": float(g.get("location", ",").split(",")[1]),
            "adcode": g.get("adcode", ""),
        }
    return {"error": data.get("info", "未知错误"), "raw": data}


def search_poi(keyword, city=None, citycode=None, key=None, offset=20, page=1):
    """
    关键词搜索 POI
    返回：POI点列表（名称、地址、经纬度、类型）
    """
    url = f"{GAODE_API_BASE}/place/text"
    params = {
        "key": key,
        "keywords": keyword,
        "offset": offset,
        "page": page,
        "extensions": "all",
    }
    if citycode:
        params["citycode"] = citycode
    elif city:
        params["city"] = city

    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    results = []
    if data.get("status") == "1":
        pois = data.get("pois", [])
        total = int(data.get("count", 0))
        for poi in pois:
            results.append({
                "id": poi.get("id", ""),
                "name": poi.get("name", ""),
                "address": poi.get("address", ""),
                "location": poi.get("location", ""),
                "type": poi.get("type", ""),
                "typecode": poi.get("typecode", ""),
                "city": poi.get("cityname", ""),
                "district": poi.get("adname", ""),
            })
        return {"total": total, "pois": results, "page": page}
    return {"error": data.get("info", "未知错误"), "raw": data}


def get_traffic_status(district_name, key=None):
    """
    获取区域实时交通态势
    返回：拥堵指数、道路状况
    """
    # 先地理编码获取 adcode
    geo = geocode_keyword(district_name, key)
    if "error" in geo:
        return geo

    adcode = geo.get("adcode", "")
    if not adcode:
        return {"error": "无法获取区域编码"}

    # 实时路况
    url = f"{GAODE_API_BASE}/traffic/status/district"
    params = {"key": key, "adcode": adcode}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    if data.get("status") == "1":
        traffic = data.get("traffic", [])
        roads = []
        for r in traffic:
            roads.append({
                "name": r.get("road_name", ""),
                "status": r.get("status", ""),  #畅通(1) / 缓行(2) / 拥堵(3)
                "speed": r.get("speed", ""),
                "congestion": r.get("congestion_index", ""),
            })
        return {
            "district": district_name,
            "adcode": adcode,
            "roads": roads,
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    return {"error": data.get("info", "未知错误"), "raw": data}


def get_weather(keyword, key=None):
    """
    获取城市天气预报（Live + Forecast）
    """
    geo = geocode_keyword(keyword, key)
    if "error" in geo:
        return geo

    citycode = geo.get("adcode", "")[:4] + "00"  # 转为省份/城市码

    url = f"{GAODE_API_BASE}/weather/weatherInfo"
    params = {"key": key, "city": geo.get("adcode", ""), "extensions": "all"}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()

    if data.get("status") == "1":
        lives = data.get("lives", [])
        forecasts = data.get("forecasts", [])
        return {
            "city": keyword,
            "live": lives[0] if lives else {},
            "forecast": forecasts[0] if forecasts else {},
            "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
    return {"error": data.get("info", "未知错误"), "raw": data}


def batch_city_search(cities, key, poi_keyword="旅游攻略"):
    """
    批量查询多个城市的 POI 热度（搜索结果数作为热度代理）
    返回：{城市名: {"poi_count": N, "top_pois": [...]}}
    """
    results = {}
    for city in cities:
        print(f"[*] 查询 {city}...", end=" ")
        r = search_poi(poi_keyword, city=city, key=key, offset=1)
        if "error" not in r:
            print(f"共 {r.get('total', 0)} 条")
            results[city] = {
                "total": r.get("total", 0),
                "keyword": poi_keyword,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        else:
            print(f"失败: {r.get('error')}")
            results[city] = {"error": r.get("error")}
    return results


# ============================================================
# 主程序入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="高德地图 API 调用工具")
    subparsers = parser.add_subparsers(dest="command")

    p_key = argparse.ArgumentParser(add_help=False)
    p_key.add_argument("--key", required=True, help="高德 API Key")

    # 地理编码
    p_geo = subparsers.add_parser("geocode", parents=[p_key], help="地理编码")
    p_geo.add_argument("--keyword", required=True, help="地址/城市名")

    # POI搜索
    p_search = subparsers.add_parser("search", parents=[p_key], help="POI搜索")
    p_search.add_argument("--keyword", required=True, help="搜索关键词")
    p_search.add_argument("--city", help="城市名")
    p_search.add_argument("--limit", type=int, default=20, help="返回数量")

    # 实时路况
    p_traffic = subparsers.add_parser("traffic", parents=[p_key], help="实时路况")
    p_traffic.add_argument("--city", required=True, help="城市名")

    # 天气
    p_weather = subparsers.add_parser("weather", parents=[p_key], help="天气预报")
    p_weather.add_argument("--city", required=True, help="城市名")

    # 批量搜索热度
    p_batch = subparsers.add_parser("batch", parents=[p_key], help="批量城市POI热度")
    p_batch.add_argument("--cities", required=True, help="逗号分隔城市列表")
    p_batch.add_argument("--keyword", default="旅游攻略", help="搜索关键词")
    p_batch.add_argument("--out", help="输出JSON文件")

    args = parser.parse_args()

    if not hasattr(args, "key") or not args.key:
        print("[错误] 需要提供 --key 参数")
        print("[提示] 申请地址: https://lbs.amap.com/")
        return

    if args.command == "geocode":
        result = geocode_keyword(args.keyword, args.key)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "search":
        result = search_poi(args.keyword, city=args.city, key=args.key, offset=args.limit)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "traffic":
        result = get_traffic_status(args.city, key=args.key)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "weather":
        result = get_weather(args.city, key=args.key)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "batch":
        cities = [c.strip() for c in args.cities.split(",")]
        results = batch_city_search(cities, args.key, args.keyword)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
