# Wind Excel插件 & VBA插件 技能手册

> 来源：Wind官方 Excel插件手册 + VBA插件手册
> 更新：2026-04-03
> 适用：Windows + Excel + Wind金融终端

---

## 一、Excel插件（直接在单元格中使用）

### 1.1 启用条件
- 登录 Wind 金融终端
- 打开 Excel，顶层菜单出现「Wind」菜单项
- 如未出现：Wind终端 → "工具"菜单 → "修复Excel" → 自动安装

### 1.2 函数表达式结构

```
=函数名(代码, 日期, 报告期, 类型参数, 指标编码)
```

**命名逻辑：** `品种*指标类*指标名称`

| 品种前缀 | 证券类型 |
|---------|---------|
| S | 股票 |
| W | 权证 |
| B | 债券 |
| CB | 可转债 |
| F | 基金 |
| I | 指数 |

**示例：**
- 股票>>财务分析>>每股收益 → `S_Ratio_EPS(600000.SH, 20051231, 1)`
- 指数>>行情>>收盘价 → `I_DQ_Close(000001.SH, 20061231)`

### 1.3 参数说明

| 参数 | 说明 | 格式 |
|------|------|------|
| Code | 证券代码 | 交易代码（整型）或 Wind代码（字符串加双引号） |
| Date | 日期 | `YYYYMMDD`（整型直接引用）或 `YYYY-MM-DD`（字符串加双引号） |
| ReportDate | 报告期 | 只识别4个截止日：1231/630/331/930 |
| Type | 类型参数 | 参考函数备注 |
| ItemsCode | 指标编码 | 用于报表科目 |

**日期格式示例：**
```
整型：=S_DQ_Close(600000, 20061231)      ✓ 可直接引用
字符串：=S_DQ_Close(600000, "2006/12/31")  ✓ 需双引号
```

> WindCode、ItemsCode、ReportDate 必须设置；Date 默认为当前机器日期，Type 默认为1

### 1.4 多值函数（核心！）

Excel插件支持 WSD/WSI/WST/WSS 等多值函数，专门解决批量数据提取性能问题。

#### WSD — 日时间序列（历史K线，最常用）
```
=WSD("600519.SH", "close;volume", "2024-01-01", "2024-12-31", "PriceAdj=F")
```
- 支持单品种多指标或多品种单指标
- Options：`PriceAdj=F/B/T`（前复权/后复权/定点复权）

#### WSS — 日截面数据（某时点多个指标）
```
=WSS("600519.SH,000001.SZ", "eps_basic;roe;pb", "rptDate=20241231")
```

#### WSI — 分钟序列
```
=WSI("600519.SH", "open;high;low;close", "2024-01-01 09:30:00", "2024-01-01 15:00:00", "BarSize=1")
```

#### WSQ — 实时行情
```
=WSQ("600519.SH", "rt_last;rt_vol;rt_chg")
```

#### WSET — 数据集报表
```
=WSET("sectorconstituent", "date=20240101;sectorid=1000000090000000")
```
用于获取板块成分、指数成分、ETF申赎成分等。

#### EDB — 宏观经济数据
```
=EDB("S0031550", "2016-01-01", "2016-02-29", "Fill=Previous")
```

### 1.5 其他功能模块

| 模块 | 功能 |
|------|------|
| 插入行情图 | 全球品种，日线/周线/月线 |
| PE/PB Bands | A股、港股、指数 PE/PB 计算 |
| 财务报表 | 中国/香港/全球股票 |
| 经济数据库EDB | 宏观、行业、商品、利率数据 |
| 商品数据 | 现货、宏观、行业、指数 |
| 利率数据 | 债券、货币、外汇、利率互换 |
| 财务预测 | 报表分析、预测未来、估值 |
| 模板库 | 股票/债券/基金/衍生品/宏观研究模板 |

### 1.6 实用工具

- **格式设置** — 预设色彩面板，快速设置文字颜色/填充色/边框
- **自动着色** — 根据内容自动识别并着色单元格
- **函数追踪** 🔥🔥 — 追踪公式引用/从属关系
- **截图识别** 🔥🔥🔥 — AI识别截图中的文本和表格

### 1.7 Excel插件常见问题

| 问题 | 解决方案 |
|------|---------|
| Mac上实时行情函数 | Windows用WRTD替代RTD |
| RTD取不到数据 | 重装Office365 / 退出杀毒软件 / 检查禁用项 |
| PE/PB模板"没有数据" | 区域设置 → 日期格式改为 `yyyy/MM/dd` |
| VBA项目ActiveX控件丢失 | Office2013+：信任中心 → 启用所有宏 |
| 无注册表权限 | 联系IT确保 `HKEYLOCAL_MACHINE\SOFTWARE\Microsoft\Office\Excel\Addins\WDF.Addin` 可读 |
| WPS兼容性问题 | 保存为 .xlsx / 检查公式路径 / 更改源地址到 WindFunc.xla |

---

## 二、VBA插件（程序化调用）

### 2.1 安装

1. 关闭 Excel
2. Wind终端 → "我的"菜单 → "修复插件" → "修复VBA插件"
3. 需管理员权限
4. Wind终端必须安装在无中文路径下

### 2.2 启用VBA

1. Excel → ALT+F11 进入VBE
2. 插入 → 模块
3. 工具 → 引用 → 勾选「WindVBA」
4. 如未找到，浏览添加：`C:\Wind\Wind.NET.Client\WindNET\DataBrowse\XLA\WindVBA.xla`

### 2.3 连接与断开

```vba
' 建立连接（必须先调用）
Call vba_start
' 返回0表示成功，非0为错误码

' 判断连接状态
vba_IsConnected  ' 返回 True/False

' 根据错误码查错误信息
vba_getErrorMsg(errcode)

' 停止使用（建议调用）
Call vba_end
```

### 2.4 VBA函数速查

| VBA函数 | 对应Python | 功能 |
|---------|-----------|------|
| `vba_wsd()` | `w.wsd()` | 日时间序列 |
| `vba_wss()` | `w.wss()` | 日截面数据 |
| `vba_wsi()` | `w.wsi()` | 分钟序列 |
| `vba_wst()` | `w.wst()` | 日内Tick数据 |
| `vba_wsq()` | `w.wsq()` | 实时行情（支持订阅） |
| `vba_wsqSubscribe()` | `w.wsq(..., func=cb)` | 实时行情订阅模式 |
| `vba_wses()` | `w.wses()` | 板块日序列 |
| `vba_wsee()` | `w.wsee()` | 板块日截面 |
| `vba_wset()` | `w.wset()` | 数据集报表 |
| `vba_edb()` | `w.edb()` | 宏观数据EDB |
| `vba_tlogon()` | `w.tlogon()` | 交易登录 |
| `vba_tlogout()` | `w.tlogout()` | 交易登出 |
| `vba_tSendOrder()` | `w.torder()` | 委托下单 |
| `vba_tCancelOrder()` | `w.tcancel()` | 撤销委托 |
| `vba_tQuery()` | `w.tquery()` | 交易查询 |
| `vba_wpf()` | `w.wpf()` | 组合报表 |
| `vba_wps()` | `w.wps()` | 组合截面数据 |
| `vba_wpd()` | `w.wpd()` | 组合序列数据 |
| `vba_wupf()` | `w.wupf()` | 组合上传调仓 |
| `vba_tdays()` | `w.tdays()` | 日期序列 |
| `vba_tdaysoffset()` | `w.tdaysoffset()` | 日期偏移 |
| `vba_tdayscount()` | `w.tdayscount()` | 日期计数 |
| `vba_cancelSubscribe()` | `w.cancel()` | 取消订阅 |

### 2.5 VBA代码模板

#### WSD（日序列）
```vba
Dim w_wsd_data As Variant
Dim w_wsd_codes As Variant, w_wsd_fields As Variant, w_wsd_times As Variant
Dim w_wsd_errorid As Long

w_wsd_data = vba_wsd("600000.SH", "close,volume", _
    "2013-07-31", "2013-08-30", _
    "TradingCalendar=LSE", _
    w_wsd_codes, w_wsd_fields, w_wsd_times, w_wsd_errorid)
```
> 返回三维数组：第一维=指标，第二维=windcode，第三维=时间

#### WSS（截面数据）
```vba
Dim w_wss_data As Variant
Dim w_wss_codes As Variant, w_wss_fields As Variant, w_wss_times As Variant
Dim w_wss_errorid As Long

w_wss_data = vba_wss("000001.SZ,000002.SZ", _
    "regcapital,founddate,close", _
    "unit=1;tradeDate=20130902;priceAdj=U;cycle=D", _
    w_wss_codes, w_wss_fields, w_wss_times, w_wss_errorid)
```

#### WSQ（实时快照）
```vba
Dim w_wsq_data As Variant
Dim w_wsq_codes As Variant, w_wsq_fields As Variant, w_wsq_times As Variant
Dim w_wsq_errorid As Long

w_wsq_data = vba_wsq("000001.SZ,000002.SZ", "rt_time,rt_last,rt_latest", _
    "", w_wsq_codes, w_wsq_fields, w_wsq_times, w_wsq_errorid)
```

#### WSQ（订阅模式）
```vba
' 回调函数定义
Sub wsqcallback(vret, codes, indics, times As Variant, _
    ByVal reqid As Long, ByVal errcode As Long)
    ' 处理实时数据
End Sub

w_wsq_data = vba_wsqSubscribe("000001.SZ,000002.SZ", "rt_time,rt_last", _
    AddressOf wsqcallback, w_wsq_errorid)

' 取消订阅
vba_cancelSubscribe(subID)
```

#### WSET（板块成分）
```vba
Dim w_wset_data As Variant
Dim w_wset_codes As Variant, w_wset_fields As Variant, w_wset_times As Variant
Dim w_wset_errorid As Long

w_wset_data = vba_wset("sectorconstituent", _
    "date=2017-07-16;sectorid=1000000090000000", _
    w_wset_codes, w_wset_fields, w_wset_times, w_wset_errorid)
```

#### EDB（宏观数据）
```vba
Dim w_edb_data As Variant
Dim w_edb_codes As Variant, w_edb_fields As Variant, w_edb_times As Variant
Dim w_edb_errorid As Long

w_edb_data = vba_edb("S0031550", "2016-01-01", "2016-02-29", _
    "Fill=Previous", w_edb_codes, w_edb_fields, w_edb_times, w_edb_errorid)
```

#### 交易登录
```vba
Dim Data As Variant
Dim Fields As Variant
Dim ErrorCode As Long

Data = vba_tlogon("0000", "", "W081757301", "******", "SHSZ", "", Fields, ErrorCode)
```

### 2.6 VBA常见问题

| 问题 | 解决方案 |
|------|---------|
| 引用里没有WindVBA | 关闭Excel重装VBA插件 / 用浏览添加WindVBA.xla |
| WSQ报错timeout | 品种数×指标数太多，缩减字段 |
| ActiveX部件不能创建对象 | 代码生成器能运行→Excel版本不完整，需重装完整版 |
| 不建议在VBA里调用单值函数 | 会导致不稳定；如需调用，用 `Cell(1,1).Formula = "..."` 格式 |

---

## 三、日期宏说明

### 通用日期宏
| 宏 | 含义 |
|----|------|
| `-5D` | 前5个日历日 |
| `-1M` | 前1个月 |
| `ED` | 当前日期（截至日） |
| `TD` | 截至当前交易日 |

### 特殊日期宏
| 宏 | 含义 |
|----|------|
| `IPO` | 上市首日 |
| `RMF` | 本月初 |
| `LME` | 上月末 |

### 日期运算
```
ED-10d        （当前最新日期前推10天）
-10TD        （前推10个交易日）
StartDate='-1M'; EndDate=''   （起始1个月前，截至今天）
```

---

## 四、证券代码参考

| 类型 | 代码示例 | 说明 |
|------|---------|------|
| 上证股票 | `600519.SH` | 6位数字+.SH |
| 深证股票 | `000001.SZ` | 6位数字+.SZ |
| 上证指数 | `000001.SH` | 6位数字+.SH |
| 沪深300 | `000300.SH` | |
| 股指期货 | `IF00.CFE` | |
| 基金ETF | `510300.SH` | |
| 港股 | `00700.HK` | |

---

## 五、Excel插件 vs VBA插件 对比

| 对比项 | Excel插件 | VBA插件 |
|--------|----------|---------|
| 使用方式 | 单元格直接输入函数 | VBA代码调用 |
| 适用场景 | 日常报表、快速取数 | 批量处理、自动化交易 |
| 编程要求 | 低 | 中 |
| 支持函数 | WSD/WSS/WSQ/WST/WSET/EDB等 | 与Excel插件几乎一致 |
| 实时订阅 | 有限 | 支持回调函数订阅 |
| 交易功能 | 无 | 完整支持（登录/下单/查询） |
