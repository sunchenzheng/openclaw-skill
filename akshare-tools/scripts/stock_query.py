"""
AkShare 股票数据综合查询工具
支持：实时行情/历史K线/分红/股东/财务指标
"""
import akshare as ak
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

def query_spot(codes=None):
    """实时行情"""
    print("\n【实时行情】")
    spot = ak.stock_zh_a_spot_em()
    if codes:
        spot = spot[spot['代码'].isin(codes)]
    cols = ['代码','名称','最新价','涨跌幅','成交量','成交额','市盈率-动态','市净率','总市值','流通市值']
    available = [c for c in cols if c in spot.columns]
    print(spot[available].to_string(index=False))
    return spot

def query_hist(code, start="20230101", end="20231231", adjust="qfq"):
    """历史K线"""
    print(f"\n【K线 {code} {start}~{end}】")
    df = ak.stock_zh_a_hist(symbol=code, period="daily",
                              start_date=start, end_date=end, adjust=adjust)
    print(df.head(5).to_string(index=False))
    print(f"共 {len(df)} 条记录")
    return df

def query_dividend(code):
    """分红数据"""
    print(f"\n【分红 {code}】")
    # 摘要
    df_all = ak.stock_history_dividend()
    row = df_all[df_all['代码'] == code]
    if len(row) > 0:
        print(f"名称: {row['名称'].values[0]}")
        print(f"累计股息: {row['累计股息'].values[0]:.2f}元")
        print(f"年均股息: {row['年均股息'].values[0]:.2f}元")
        print(f"分红次数: {row['分红次数'].values[0]}次")
    
    # 明细
    df_div = ak.stock_history_dividend_detail(symbol=code, indicator='分红', date='')
    if df_div is not None and len(df_div) > 0:
        print(f"\n近{len(df_div)}条分红明细:")
        print(df_div[['公告日期','派息','送股','转增','除权除息日']].head(5).to_string(index=False))
    return df_div

def query_shareholder(code):
    """股东数据"""
    print(f"\n【股东 {code}】")
    try:
        df = ak.stock_shareholder_change_ths(symbol=code)
        if df is not None and len(df) > 0:
            print(f"近{len(df)}期股东变动:")
            print(df.head(5).to_string(index=False))
    except Exception as e:
        print(f"股东变动获取失败: {e}")
    
    # 股东户数
    try:
        num_df = ak.stock_shareholder_num()
        row = num_df[num_df['代码'].astype(str).str.zfill(6) == code.zfill(6)]
        if len(row) > 0:
            print(f"\n股东户数: {row['股东户数'].values[0]}")
    except Exception as e:
        print(f"股东户数获取失败: {e}")

def query_financial(code, start="20230101", end="20241231"):
    """财务指标"""
    print(f"\n【财务指标 {code}】")
    try:
        df = ak.stock_financial_indicator_dfcf(symbol=code, start_date=start, end_date=end)
        if df is not None and len(df) > 0:
            print(df.head(5).to_string(index=False))
    except Exception as e:
        print(f"财务指标获取失败: {e}")

def query_info(code):
    """公司基本信息"""
    print(f"\n【公司信息 {code}】")
    try:
        info = ak.stock_individual_info_em(symbol=code)
        print(info.to_string(index=False))
    except Exception as e:
        print(f"公司信息获取失败: {e}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AkShare 股票数据查询")
    parser.add_argument("code", help="股票代码，如 000988")
    parser.add_argument("--type", "-t", default="all",
                       choices=["all","spot","hist","div","sh","fin","info"],
                       help="查询类型")
    parser.add_argument("--start", default="20230101", help="开始日期 YYYYMMDD")
    parser.add_argument("--end", default="20231231", help="结束日期 YYYYMMDD")
    parser.add_argument("--adjust", default="qfq", help="复权方式: qfq/hfq/空")
    
    args = parser.parse_args()
    code = args.code.zfill(6)
    
    if args.type in ["all","spot"]:
        query_spot([code])
    if args.type in ["all","hist"]:
        query_hist(code, args.start, args.end, args.adjust)
    if args.type in ["all","div"]:
        query_dividend(code)
    if args.type in ["all","sh"]:
        query_shareholder(code)
    if args.type in ["all","fin"]:
        query_financial(code)
    if args.type in ["all","info"]:
        query_info(code)
