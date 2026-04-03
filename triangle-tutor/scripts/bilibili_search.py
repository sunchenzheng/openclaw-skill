"""
哔哩哔哩视频搜索
用法：
  python bilibili_search.py <关键词>
  python bilibili_search.py "初中数学 三角形 全等"
输出格式：JSON（便于 OpenClaw 调用）
"""

import sys
import os
import json
import re
import urllib.parse
import http.client
import html
import io

def search_bilibili(query, max_results=10):
    """
    通过 B站 搜索 API 获取视频结果
    B站搜索 API 是公开的，不需要登录
    """
    encoded_query = urllib.parse.quote(query)
    url = f"/x/web-interface/search/type?search_type=video&keyword={encoded_query}&page=1&pagesize={max_results}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com",
        "Accept": "application/json",
    }

    try:
        conn = http.client.HTTPSConnection("api.bilibili.com", timeout=10)
        conn.request("GET", url, headers=headers)
        resp = conn.getresponse()
        raw_data = resp.read()
        conn.close()

        try:
            data = json.loads(raw_data.decode("utf-8"))
        except UnicodeDecodeError:
            data = json.loads(raw_data.decode("gbk", errors="replace"))

        if data.get("code") != 0:
            return {"status": "error", "code": data.get("code"), "message": f"B站API错误: code={data.get('code')}"}

        results = []
        for item in data.get("data", {}).get("result", []):
            results.append({
                "title": html.unescape(item.get("title", "").replace("<em class=\"keyword\">", "**").replace("</em>", "**")),
                "bvid": item.get("bvid", ""),
                "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}",
                "author": item.get("author", ""),
                "play_count": format_number(item.get("play", 0)),
                "like_count": format_number(item.get("like", 0)),
                "duration": item.get("duration", ""),
                "description": html.unescape(item.get("description", ""))[:100],
                "pubdate": item.get("pubdate", ""),
            })

        return {
            "status": "ok",
            "query": query,
            "count": len(results),
            "results": results
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def format_number(n):
    """格式化数字：10000 -> 1.0万"""
    n = int(n)
    if n >= 10000:
        return f"{n/10000:.1f}万"
    return str(n)


def main():
    # 修复 Windows GBK 控制台编码问题
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "用法: python bilibili_search.py <关键词> [最大结果数]"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    output_json = "--json" in sys.argv

    result = search_bilibili(query, max_results)

    if output_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["status"] == "error":
            print(f"ERROR: {result['message']}", file=sys.stderr)
            sys.exit(1)

        print(f"Search: {query}")
        print(f"Count: {result['count']}")
        for i, v in enumerate(result["results"], 1):
            print(f"{i}. [{v['author']}] {v['title']} ({v['play_count']}播放) {v['url']}")


if __name__ == "__main__":
    main()
