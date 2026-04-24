"""
AkShare 股票分红数据批量查询
用法: python dividend_query.py [股票代码列表]
示例: python dividend_query.py 000988,600519,600006
"""
import akshare as ak
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_dividend(code):
    """获取单只股票分红数据"""
    result = {'code': code, 'name': '', 'records': 0, 'recent_divs': []}
    try:
        df_all = ak.stock_history_dividend()
        row = df_all[df_all['代码'] == code]
        if len(row) > 0:
            result['name'] = row['名称'].values[0]
            result['total_div'] = row['累计股息'].values[0]
            result['avg_div'] = row['年均股息'].values[0]
            result['div_count'] = row['分红次数'].values[0]
    except Exception as e:
        result['error'] = str(e)
    
    try:
        df_detail = ak.stock_history_dividend_detail(symbol=code, indicator='分红', date='')
        if df_detail is not None and len(df_detail) > 0:
            result['records'] = len(df_detail)
            # 近3年
            df_detail['公告日期_dt'] = pd.to_datetime(df_detail['公告日期'], errors='coerce')
            recent = df_detail.nlargest(3, '公告日期_dt')
            result['recent_divs'] = [
                f"{row['公告日期']}: 派息{row['派息']}元/股"
                for _, row in recent.iterrows()
            ]
    except Exception as e:
        result['detail_error'] = str(e)
    
    return result


if __name__ == "__main__":
    default_codes = ["000988", "600519", "600006", "600035", "600498", "002194"]
    
    if len(sys.argv) > 1:
        codes = sys.argv[1].split(",")
    else:
        codes = default_codes
    
    print(f"查询 {len(codes)} 只股票分红数据...\n")
    
    results = []
    for code in codes:
        r = get_dividend(code)
        results.append(r)
        name = r.get('name', '未知')
        total = r.get('total_div', 0)
        avg = r.get('avg_div', 0)
        cnt = r.get('div_count', 0)
        recent = r.get('recent_divs', [])
        
        print(f"{code} {name}")
        print(f"  累计股息: {total:.2f}元 | 年均: {avg:.2f}元 | 分红{cnt}次")
        if recent:
            for d in recent:
                print(f"  {d}")
        if 'error' in r:
            print(f"  错误: {r['error']}")
        print()
    
    print(f"结果已记录，可保存到CSV。")
