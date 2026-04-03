# Wind Python API 手册

> 来源：用户提供的 Wind 官方 Python 接口文档
> 更新：2026-04-02

---

## 系统要求

- Windows 系统（支持32位和64位）
- Python 2.6, 2.7, 3.3+
- Wind 终端最新版
- 安装时需要系统管理员权限

---

## 安装流程

1. 打开 Wind 金融终端
2. 点击"开始/插件修复" → "修复Python接口"
3. Wind 自动检测 Python 并配置（需管理员权限）

**手动安装（备用）：**
```bash
C:\Python28\python.exe C:\Wind\Wind.NET.Client\WindNET\bin\installWindPy.py C:\wind\wind.net.client\windnet
```

---

## 基础使用

```python
from WindPy import w

w.start()              # 启动API（默认超时120秒）
w.start(waitTime=60)  # 设置超时60秒
w.isconnected()        # 判断是否登录成功
w.stop()              # 停止API（程序退出时自动调用）
w.menu()              # 显示导航界面（帮助创建命令）
```

---

## 核心函数速查

### 数据查询类

| 函数 | 用途 | 频率 |
|------|------|------|
| `w.wsd()` | 日时间序列（历史K线） | 日线 |
| `w.wss()` | 日截面数据（当前指标） | 快照 |
| `w.wsi()` | 分钟序列数据 | 分钟 |
| `w.wsq()` | 实时行情（支持订阅推送） | 实时 |
| `w.wst()` | 日内Tick数据 | Tick |
| `w.edb()` | 宏观经济数据（EDB） | - |
| `w.wset()` | 数据集报表（板块/成分股等） | - |

### 交易日历类

| 函数 | 用途 |
|------|------|
| `w.tdays()` | 获取区间内日期序列 |
| `w.tdaysoffset()` | 日期偏移 |
| `w.tdayscount()` | 统计日期数量 |

### 交易类（需开通权限）

| 函数 | 用途 |
|------|------|
| `w.tlogon()` | 交易登录 |
| `w.tlogout()` | 交易登出 |
| `w.torder()` | 委托下单 |
| `w.tcancel()` | 撤销委托 |
| `w.tquery()` | 查询（资金/持仓/委托/成交） |

### 组合管理类

| 函数 | 用途 |
|------|------|
| `w.wpf()` | 组合报表 |
| `w.wps()` | 组合截面数据 |
| `w.wpd()` | 组合序列数据 |
| `w.wupf()` | 组合上传调仓 |

---

## WSD - 日时间序列（最常用）

```python
w.wsd(codes, fields, beginTime, endTime, options)

# 示例：获取贵州茅台近期行情
data = w.wsd('600519.SH', 'open;high;low;close;volume', 
             '2024-01-01', '2024-12-31', 
             'PriceAdj=F', usedf=True)
# 返回 DataFrame，ErrorCode=0 表示成功
```

**常用 options：**
- `PriceAdj=F/B/T` — 复权方式（前复权/后复权/定点复权）
- `Period=D/W/M/Q/S/Y` — 周期（天/周/月/季/半年/年）
- `Days=Trading/Weekdays/Alldays` — 日期类型

---

## WSS - 日截面数据

```python
w.wss(codes, fields, options)

# 示例：获取多只股票的财务指标
data = w.wss('600519.SH,000001.SZ', 
             'eps_basic,profittogr,roe,pb', 
             'rptDate=20241231', usedf=True)
```

---

## WSI - 分钟序列

```python
w.wsi(codes, fields, beginTime, endTime, options)

# 示例：获取1分钟K线
data = w.wsi('600519.SH', 'open;high;low;close', 
             '2024-01-01 09:30:00', '2024-01-01 15:00:00',
             'BarSize=1', usedf=True)
```

---

## WSQ - 实时行情

```python
# 快照模式
data = w.wsq('600519.SH', 'rt_last;rt_vol;rt_chg')

# 订阅模式（行情变化时推送）
def my_callback(data):
    print(data)
w.wsq('600519.SH', 'rt_last', func=my_callback)
```

---

## 日期宏

| 宏 | 含义 | 示例 |
|----|------|------|
| `-5D` | 前5个交易日 | beginTime='-5D' |
| `-1M` | 前1个月 | beginTime='-1M' |
| `ED` | 截止日期 | endTime='ED' |
| `IPO` | 上市首日 | beginTime='IPO' |
| `RMF` | 本月初 | beginTime='RMF' |
| `LME` | 上月末 | endTime='LME' |

---

## 常见证券代码

| 类型 | 代码示例 | 说明 |
|------|---------|------|
| A股 | `600519.SH` | 上证股票 |
| A股 | `000001.SZ` | 深证股票 |
| 指数 | `000001.SH` | 上证指数 |
| 期货 | `IF00.CFE` | 股指期货 |
| 基金 | `510300.SH` | ETF基金 |

---

## 错误码

| ErrorCode | 含义 |
|-----------|------|
| 0 | 成功 |
| -2 | Wind终端未连接 |
| -40520005 | 无Python API权限（需开通） |
| 其他 | 详见Wind官方文档 |

---

## 权限说明

- **数据权限**：基础账号通常包含主要行情数据
- **Python API权限**：需要单独开通（联系Wind客服或管理员）
- **交易权限**：需要开通模拟/实盘交易账号
