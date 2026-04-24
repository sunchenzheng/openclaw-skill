---
name: akshare-tools
description: "利用 AkShare 获取A股/港股/美股/基金/期货/宏观数据。结合 Wind Python API 做实时行情补充。用于：股票筛选、财务分析、量化选股、板块分类、估值对比等场景。触发：用户要求获取A股数据、财务指标、板块成分，或要求量化筛选。"
author: sunchenzheng
tags: [akshare, finance, stock, china-a-share, financial-data, screening]
---

# AKShare 金融数据工具包

> **官方文档**：https://akshare.akfamily.xyz/
> **安装**：`pip install akshare`
> **版本**：`1.18.54`（2026-04 测试可用）

---

## 核心数据接口（已验证可用）

### 1. stock_financial_abstract — 利润表/ROE/净利率（宽格式）

**用途**：获取净利润、营收、ROE、净利润率等指标（2024/2023/2022 年报）

**注意**：数据格式为**宽格式**（列为日期，行指标），需要按行匹配指标名

```python
import akshare as ak
import pandas as pd

def yuan_to_yi(v):
    """元->亿元（阈值1亿）；万元->亿元（阈值<1亿）"""
    if v is None: return None
    try:
        if isinstance(v, str):
            v = v.replace(',', '')
            if '亿' in v: return float(v.replace('亿', ''))
            if '万' in v: return round(float(v.replace('万', '')) / 1e4, 2)
            return float(v)
        vf = float(v)
        if abs(vf) > 1e8:   # >1亿，按元处理(÷1e8)
            return round(vf / 1e8, 2)
        else:               # <1亿，按万元处理(÷1e4)
            return round(vf / 1e4, 2)
    except: return None

# 获取单只股票财务摘要
ab = ak.stock_financial_abstract(symbol='000001')  # 去掉交易所后缀
# ab: 行=指标名(列[1])，列[2+]=各期数据

# 找到2024年报列
cols = list(ab.columns)
c24 = next((c for c in cols if str(c) == '20241231'), None)
c23 = next((c for c in cols if str(c) == '20231231'), None)

for _, row in ab.iterrows():
    if len(row) < 2: continue
    name = str(row.iloc[1]).strip()  # 指标名在第2列

    v24 = yuan_to_yi(row.get(c24)) if c24 else None
    v23 = yuan_to_yi(row.get(c23)) if c23 else None

    if name == '归属净利润':
        profit_2024 = v24
        profit_2023 = v23
    elif name == '营业总收入':
        revenue_2024 = v24
        revenue_2023 = v23
    elif '净资产收益率' in name:    # ROE
        roe_2024 = row.get(c24)
    elif '销售净利率' in name:        # 净利润率
        npm_2024 = row.get(c24)
```

**关键指标对应关系**：
| 指标名（AkShare） | 说明 |
|---|---|
| `归属净利润` | 归母净利润（最准确） |
| `净利润` | 兜底用，可能重复 |
| `营业总收入` | 营收（优先） |
| `营业收入` | 营收（兜底） |
| `净资产收益率` | ROE（百分比，如 15.3 表示 15.3%） |
| `销售净利率` | 净利润率（百分比） |

---

### 2. stock_financial_cash_new_ths — 经营现金流（长格式）

**用途**：获取经营活动现金流量净额

**重要**：返回数据是**长格式**（metric_name / value），不是宽格式！

```python
# 获取现金流数据
cash = ak.stock_financial_cash_new_ths(symbol='300124')

# 找 2024-12-31 和 2023-12-31 的数据
df24 = cash[cash['report_date'] == '2024-12-31']
df23 = cash[cash['report_date'] == '2023-12-31']

# 关键字段名：indirect_act_cash_flow_net（间接法经营现金流净额）
if len(df24) > 0:
    ocf_row = df24[df24['metric_name'] == 'indirect_act_cash_flow_net']
    if len(ocf_row) > 0:
        val = ocf_row.iloc[0]['value']
        ocf_2024 = yuan_to_yi(val)
```

**常见 metric_name 值**：
| metric_name | 说明 |
|---|---|
| `indirect_act_cash_flow_net` | 间接法经营现金流净额 ✅ |
| `act_cash_flow_net` | 现金净增加额 |
| `cash_net_profit` | 现金净收益 |

**注意**：部分股票（如浪潮信息）的间接法数据可能与直接法差距较大，需交叉验证。

---

### 3. 与 Wind API 配合使用

AkShare 财务数据权威，Wind API 实时行情准确。两者配合：

```python
import sys
sys.path.insert(0, r'C:\Wind\Wind.NET.Client\WindNET\x64')
import WindPy as w

w.w.start()

# Wind wss — 实时估值（必须加 tradeDate 参数！）
r = w.w.wss('600519.SH,000001.SZ', 'sec_name,close,pe_ttm,pb_lf,ps_ttm',
            'tradeDate=20260410')  # ← 必须加，否则数据过期

if r.ErrorCode == 0:
    for j, code in enumerate(r.Codes):
        pe = r.Data[2][j]  # pe_ttm
        pb = r.Data[3][j]  # pb_lf
        price = r.Data[1][j]  # close

# AkShare — 财务数据（非实时，但完整）
# 在 stock_financial_abstract 里拿净利润/营收
# 在 stock_financial_cash_new_ths 里拿经营现金流
```

**Wind tradeDate 参数**：不加则返回最近可用日期，非当日数据。

---

## 常用选股接口

### 实时行情（全市场）
```python
df = ak.stock_zh_a_spot_em()  # 全A股实时行情
df = ak.stock_zh_a_hist(symbol='000001', period='daily',
                         start_date='20230101', end_date='20231231', adjust='qfq')
```

### 财务筛选
```python
# 东方财富财务指标（需年份参数）
df = ak.stock_financial_indicator_dfcf(symbol='000001',
                                        start_date='20230101', end_date='20241231')

# 分红数据
df = ak.stock_history_dividend_detail(symbol='000001', indicator='分红', date='')

# 股东变动
df = ak.stock_shareholder_change_ths(symbol='000001')
```

### 宏观数据
```python
df = ak.macro_china_cpi()  # CPI
df = ak.macro_china_ppi()  # PPI
```

---

## 完整筛选流程示例

参见脚本：`scripts/quant_final_v4.py`

```python
# 流程
# 1. Wind wss 获取：PE/PB/PS（加 tradeDate）
# 2. AkShare stock_financial_abstract：净利润/营收/ROE
# 3. AkShare stock_financial_cash_new_ths：经营现金流
# 4. 合并 DataFrame → 应用筛选条件 → 综合打分

STOCKS = {
    "688981.SH": "中芯国际",
    "688256.SH": "寒武纪",
    "300124.SZ": "汇川技术",
    # ...
}

# 筛选条件
c1 = df["净利润亿"] > 0           # 净利润为正
c2 = df["经营现金流亿"] > 0       # 现金流为正
c3 = (df["PE_TTM"] > 0) & (df["PE_TTM"] < 50)   # PE合理
c4 = (df["PB_LF"] > 0) & (df["PB_LF"] < 6)       # PB合理
```

---

## 已知限制

| 问题 | 说明 | 解决方案 |
|------|------|---------|
| 非经常性损益 | 无直接接口 | Wind 终端 F9 财务附表 |
| 资产减值损失 | 无直接接口 | Wind 终端 F9 财务附表 |
| 国资背景 | 无直接接口 | Wind 终端 F9 股东页 |
| 间接法现金流异常 | 部分股票数据不准确 | 交叉验证直接法数据 |
| 数据延迟 | 年报通常滞后 3-4 个月 | Q3/半年报替代 |

---

## 安装

```bash
pip install akshare
# 可选：更新到最新版
pip install --upgrade akshare
```
