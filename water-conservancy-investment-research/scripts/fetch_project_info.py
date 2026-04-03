#!/usr/bin/env python3
"""
水利工程项目信息获取脚本
用法：python fetch_project_info.py <项目名称>
"""

import sys
import json
import urllib.request
import urllib.parse

def fetch_project_info(project_name: str) -> dict:
    """获取水利工程项目信息"""
    
    # 构建搜索查询
    encoded_name = urllib.parse.quote(project_name)
    
    # 尝试多个信息源
    sources = [
        {
            'name': '百度搜索',
            'url': f'https://www.baidu.com/s?wd={encoded_name}+项目+投资+进展',
        },
        {
            'name': '水利部官网',
            'url': f'https://www.mwr.gov.cn/zyzt/sslm/slgc/{encoded_name}/',
        },
        {
            'name': '湖北省水利厅',
            'url': f'http://slt.hubei.gov.cn/search?searchword={encoded_name}',
        }
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    results = []
    
    for source in sources:
        try:
            req = urllib.request.Request(source['url'], headers=headers)
            response = urllib.request.urlopen(req, timeout=10)
            html = response.read().decode('utf-8', errors='ignore')
            
            # 简单解析 - 提取标题和摘要
            results.append({
                'source': source['name'],
                'url': source['url'],
                'status': 'accessible',
                'raw_length': len(html)
            })
        except Exception as e:
            results.append({
                'source': source['name'],
                'url': source['url'],
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'project_name': project_name,
        'sources_checked': len(sources),
        'results': results
    }

def main():
    if len(sys.argv) < 2:
        print("用法: python fetch_project_info.py <项目名称>")
        print("示例: python fetch_project_info.py 鄂北水资源配置工程")
        print("      python fetch_project_info.py 南水北调中线工程")
        sys.exit(1)
    
    project_name = ' '.join(sys.argv[1:])
    
    print(f"正在获取项目信息: {project_name}")
    print("=" * 50)
    
    result = fetch_project_info(project_name)
    
    print(f"\n项目名称: {result['project_name']}")
    print(f"检查了 {result['sources_checked']} 个信息来源:\n")
    
    for r in result['results']:
        print(f"【{r['source']}】")
        print(f"  URL: {r['url']}")
        if r['status'] == 'accessible':
            print(f"  状态: 可访问 (页面长度: {r['raw_length']} 字节)")
        else:
            print(f"  状态: 错误 - {r.get('error', '未知')}")
        print()
    
    print("-" * 50)
    print("建议: 使用 web_fetch 工具直接访问相关网页获取详细信息")

if __name__ == '__main__':
    main()
