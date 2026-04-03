#!/usr/bin/env python3
"""
水利政策搜索脚本
用法：python search_water_policy.py <关键词>
"""

import sys
import json
import urllib.request
import urllib.parse

def search_water_policy(keyword: str) -> dict:
    """搜索水利相关政策文件"""
    
    # 构建百度搜索URL
    encoded_keyword = urllib.parse.quote(f"水利 {keyword} 政策")
    search_url = f"https://www.baidu.com/s?wd={encoded_keyword}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    }
    
    req = urllib.request.Request(search_url, headers=headers)
    
    try:
        response = urllib.request.urlopen(req, timeout=15)
        html = response.read().decode('utf-8', errors='ignore')
        
        return {
            'status': 'success',
            'keyword': keyword,
            'search_url': search_url,
            'result_count': 'unknown',
            'note': '建议直接访问水利部官网或北大法宝等政策数据库获取更精确结果'
        }
    except Exception as e:
        return {
            'status': 'error',
            'keyword': keyword,
            'error': str(e)
        }

def main():
    if len(sys.argv) < 2:
        print("用法: python search_water_policy.py <关键词>")
        print("示例: python search_water_policy.py PPP 融资")
        sys.exit(1)
    
    keyword = ' '.join(sys.argv[1:])
    
    print(f"正在搜索: {keyword}")
    print("-" * 50)
    
    result = search_water_policy(keyword)
    
    if result['status'] == 'success':
        print(f"搜索成功!")
        print(f"关键词: {result['keyword']}")
        print(f"搜索URL: {result['search_url']}")
        print(f"提示: {result['note']}")
    else:
        print(f"搜索失败: {result.get('error', '未知错误')}")

if __name__ == '__main__':
    main()
