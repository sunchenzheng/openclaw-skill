# AkShare 工具集

> 免费开源金融数据库，覆盖 A股/港股/美股/基金/期货/宏观 等全品类数据

**官方文档**：https://akshare.akfamily.xyz/

## 快速使用

```python
import akshare as ak

# 实时行情
ak.stock_zh_a_spot_em()

# 历史K线
ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20230101", end_date="20231231", adjust="qfq")

# 分红数据
ak.stock_history_dividend_detail(symbol="000001", indicator="分红", date="")
```

## 脚本工具

### stock_query.py - 综合查询
```bash
python stock_query.py 000988 --type all      # 查询所有数据
python stock_query.py 000988 --type div      # 仅查分红
python stock_query.py 000988 --type hist --start 20240101 --end 20241231
```

### dividend_query.py - 分红查询
```bash
python dividend_query.py                          # 默认列表
python dividend_query.py 000988,600519,600006    # 指定股票
```

## 数据分类速查

| 类别 | 常用函数 |
|------|---------|
| 实时行情 | `stock_zh_a_spot_em`, `stock_zh_a_spot` |
| 日K历史 | `stock_zh_a_hist` |
| 分红数据 | `stock_history_dividend`, `stock_history_dividend_detail` |
| 股东数据 | `stock_shareholder_change_ths`, `stock_shareholder_num` |
| 财务指标 | `stock_financial_indicator_dfcf` |
| 财务报表 | `stock_financial_report_sina` |
| 港股 | `stock_hk_spot_em`, `stock_hk_hist` |
| 美股 | `stock_us_spot_em`, `stock_us_hist` |
| 基金净值 | `fund_etf_hist_em`, `fund_open_fund_nav_em` |
| 宏观数据 | `macro_china_cpi`, `macro_china_gdp_yearly`, `macro_china_money_supply` |
| 北向资金 | `stock_hsgt_north_netflow_in`, `stock_hsgt_hold_stock` |
| 龙虎榜 | `stock_lhb_detail_daily` |
| 融资融券 | `stock_margin_detail_szse` |
| 新股/打新 | `stock_new_em`, `stock_ipo_summary_cninfo` |
