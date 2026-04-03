"""
Wind Python API 常用示例速查
基于官方手册整理
"""

from WindPy import w
import pandas as pd

# ====================
# 初始化连接
# ====================
w.start()  # 默认120秒超时


# ====================
# 1. WSD - 日时间序列（最常用）
# ====================

# 获取单只股票日线数据（前复权）
data = w.wsd('600519.SH', 'open;high;low;close;volume;amount',
             '2024-01-01', '2024-12-31',
             'PriceAdj=F')
print(data.Data)  # 返回list格式

# 返回DataFrame格式
data_df = w.wsd('600519.SH', 'close', '2024-01-01', '2024-12-31', usedf=True)[1]
print(data_df.head())

# 多只股票同时获取
data = w.wsd(['600519.SH', '000858.SZ'], 'close', '-10D', '')
print(data.Data)

# 日期宏使用
data = w.wsd('600519.SH', 'close', '-5D', 'ED')  # 前5个交易日到今天


# ====================
# 2. WSS - 截面数据（当前指标）
# ====================

# 获取财务/估值指标
data = w.wss('600519.SH', 'eps_basic,roe,pb,pe_ttm,ps,pcf', usedf=True)[1]
print(data)

# 多只股票
data = w.wss('600519.SH;000001.SZ;600000.SH',
             'sec_name,open,high,low,close,volume,amount',
             'tradeDate=20250103')


# ====================
# 3. WSI - 分钟序列
# ====================

# 5分钟K线
data = w.wsi('600519.SH', 'open;high;low;close;volume',
             '2024-01-01 09:30:00', '2024-01-01 15:00:00',
             'BarSize=5', usedf=True)[1]
print(data)


# ====================
# 4. WST - Tick数据
# ====================

from datetime import datetime
beg = datetime.now().strftime('%Y-%m-%d 09:30:00')
end = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
data = w.wst('000001.SZ', 'last,bid1,ask1,bidvol1,askvol1',
             beg, end, usedf=True)[1]
print(data)


# ====================
# 5. WSQ - 实时行情
# ====================

# 快照
data = w.wsq('600519.SH', 'rt_last,rt_vol,rt_chg,rt_pct_chg,rt_open')
print(data.Data)

# 订阅（需回调函数）
def on_tick(data):
    print(data.Codes, data.Fields, data.Data)

req_id = w.wsq('600519.SH', 'rt_last', func=on_tick)
# w.cancelRequest(req_id)  # 取消订阅


# ====================
# 6. WSET - 数据集（板块成分等）
# ====================

# 申万一级行业成分股
sw = w.wset('sectorconstituent',
            'date=20250103;sectorid=a39901011g000000',
            usedf=True)[1]
print(sw.head())

# 沪深300成分股
hs300 = w.wset('sectorconstituent',
               'date=20250103;sectorId=001004',
               usedf=True)[1]
print(hs300.head())


# ====================
# 7. EDB - 宏观数据
# ====================

# GDP数据
data = w.edb('M0001395,M0001396,M0001397',
             '2020-01-01', '2024-12-31', usedf=True)[1]
print(data)


# ====================
# 8. 交易日历
# ====================

# 获取区间内所有交易日
dates = w.tdays('2024-01-01', '2024-12-31').Data[0]
print(f'共{len(dates)}个交易日')

# 统计天数
count = w.tdayscount('2024-01-01', '2024-12-31').Data[0][0]
print(f'共{count}个交易日')


# ====================
# 9. 交易函数（需开通权限）
# ====================

# 登录模拟交易
logon_id = w.tlogon('0000', 0, 'w081263801', '000000', 'SHSZ')
print(logon_id.Data)

# 查询资金
capital = w.tquery('Capital').Data
print(capital)

# 下单
order_id = w.torder('600519.SH', 'Buy', '1800.00', '100',
                    'OrderType=LMT;LogonID=0')
print(order_id.Data)

# 撤单
w.tcancel(order_id.Data[0][0])  # 委托编号

# 登出
w.tlogout(0)


# ====================
# 常用证券代码速查
# ====================
# 沪深股票：  600519.SH（茅台）、000001.SZ（平安银行）
# 沪深指数：  000001.SH（上证）、399001.SZ（深证）
# 沪深300：   000300.SH
# 中证500：   000905.SH
# 创业板：    399006.SZ
# 上证50：    000016.SH
# 期货：      IF00.CFE（沪深300期货）、IC00.CFE（中证500期货）
# ETF：       510300.SH（沪深300ETF）
# 基金：      000001.OF（开放式基金）
