# Wind Excel 插件公式参考

> 本文件列出 Wind Excel 插件（WENDEZHI）支持的常用公式及其语法。
> 数据刷新：按 `Ctrl+Alt+F5` 或点击「Wind」选项卡 → 「刷新数据」

---

## 1. WSD — 日时间序列（历史K线）

**用途**：获取证券的历史日线数据（行情序列）

**语法**：
```
=WSD("Code", "Field", "BeginTime", "EndTime", "Options")
```

**参数说明**：
| 参数 | 含义 | 示例 |
|------|------|------|
| Code | 证券代码 | "600519.SH" |
| Field | 数据字段 | "close;open;high;low;volume" |
| BeginTime | 开始日期 | "2026-01-01" |
| EndTime | 结束日期 | "2026-04-03" |
| Options | 选项字符串 | "PriceAdj=F" |

**常用字段**：
| 字段 | 含义 |
|------|------|
| open | 开盘价 |
| high | 最高价 |
| low | 最低价 |
| close | 收盘价 |
| volume | 成交量 |
| amount | 成交额 |
| chg | 涨跌额 |
| pct_chg | 涨跌幅 |

**常用选项**：
| 选项 | 含义 |
|------|------|
| PriceAdj=F | 前复权 |
| PriceAdj=B | 后复权 |
| PriceAdj=U | 不复权 |
| Period=D | 日线（默认） |
| Period=W | 周线 |
| Period=M | 月线 |

**示例**：
```
=WSD("600519.SH", "close", "2026-01-01", "2026-04-03", "PriceAdj=F")
=WSD("000001.SZ", "open;high;low;close;volume", "2026-01-01", "2026-04-03", "")
```

---

## 2. WSS — 日截面数据（当前指标）

**用途**：获取某一时点的截面数据（财务指标/估值等）

**语法**：
```
=WSS("Code", "Field", "Options")
```

**常用字段**：
| 字段 | 含义 |
|------|------|
| eps_basic | 每股收益（基本） |
| eps_cut | 每股收益（扣除） |
| profittogr | 净利润同比 |
| roe_avg | 净资产收益率（平均） |
| roe_cut | 净资产收益率（扣非） |
| netproinfo | 净利润 |
| pb | 市净率 |
| pe_ttm | 市盈率（TTM） |
| ps_ttm | 市销率（TTM） |
| pcfttm | 市现率（TTM） |
| dividendyield | 股息率 |
| close | 最新价 |
| mkt_cap | 总市值 |

**Options 常用选项**：
| 选项 | 含义 |
|------|------|
| rptDate=YYYYMMDD | 报表日期 |
| beginDate=YYYYMMDD | 起始日期 |
| endDate=YYYYMMDD | 截止日期 |

**示例**：
```
=WSS("600519.SH", "eps_basic;roe_avg;pb;pe_ttm;dividendyield", "")
=WSS("600519.SH,000001.SZ", "close;volume;amount;mkt_cap", "")
```

---

## 3. WSI — 分钟序列

**用途**：获取分钟级K线数据

**语法**：
```
=WSI("Code", "Field", "BeginTime", "EndTime", "Options")
```

**常用选项**：
| 选项 | 含义 |
|------|------|
| BarSize=1 | 1分钟 |
| BarSize=5 | 5分钟 |
| BarSize=15 | 15分钟 |
| BarSize=30 | 30分钟 |
| BarSize=60 | 60分钟 |
| DataType=1 | 成交明细 |

**示例**：
```
=WSI("600519.SH", "open;high;low;close", "2026-04-03 09:30:00", "2026-04-03 15:00:00", "BarSize=5")
```

---

## 4. WST — 日内Tick数据

**语法**：
```
=WST("Code", "Field", "BeginTime", "EndTime", "Options")
```

---

## 5. EDIB — EDB宏观数据（新版）

**语法**：
```
=EDIB("IndicatorCode", "BeginTime", "EndTime", "Options")
```

---

## 6. EDI — EDB宏观数据（旧版兼容）

**语法**：
```
=EDI("IndicatorCode", "BeginTime", "EndTime", "Options")
```

---

## 7. WSET — 数据集（板块/成分股）

**用途**：获取板块成分股、指数成分股等

**语法**：
```
=WSET("DataSet", "Field", "Options")
```

**示例**：
```
# 获取沪深300成分股
=WSET(" CurSectorHS300", "wind_code", "")
# 获取申万行业成分股
=WSET("SWIndustryConstituent", "wind_code", "industry=801010")
```

---

## 8. TDays — 交易日历

**语法**：
```
=TDays("BeginTime", "EndTime", "Options")
```

---

## 常用证券代码速查

| 类型 | 代码 | 说明 |
|------|------|------|
| 上证股票 | 600519.SH | 贵州茅台 |
| 深证股票 | 000001.SZ | 平安银行 |
| 上证指数 | 000001.SH | 上证指数 |
| 沪深300 | 000300.SH | 沪深300指数 |
| 上证50 | 000016.SH | 上证50指数 |
| 创业板指 | 399006.SZ | 创业板指 |
| 科创50 | 000688.SH | 科创50指数 |
| 股指期货 | IF00.CFE | 沪深300期货 |
| 国债期货 | T00.CFE | 10年期国债期货 |

---

## 日期格式说明

- 标准格式：`YYYY-MM-DD`（如 `2026-04-03`）
- Wind宏：
  - `-5D` = 前5个交易日
  - `-1M` = 前1个月
  - `ED` = 今日（End Day）
  - `RMF` = 本月初
  - `LME` = 上月末

---

## Excel 中使用技巧

### 多代码查询
用分号分隔多个代码：
```
=WSS("600519.SH;000001.SZ;000002.SZ", "close;pe_ttm", "")
```

### 参数单元格化
将代码/日期做成参数单元格，便于 AI 修改：
|  | A | B |
|--|---|---|
| 1 | 600519.SH | =WSD(A1,"close","2026-01-01","2026-04-03","") |

### 批量刷新
在 VBA 中：
```vba
Sub RefreshWind()
    Application.CalculateFull
    ThisWorkbook.RefreshAll
End Sub
```
