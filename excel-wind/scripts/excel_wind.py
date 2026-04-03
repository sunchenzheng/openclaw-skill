"""
excel_wind.py - Excel+Wind插件自动化数据获取脚本

用法:
    python excel_wind.py <command> [options]

命令:
    wsd         获取日时间序列（历史K线）
    wss         获取日截面数据（当前指标）
    wsi         获取分钟序列
    template    创建空白模板

示例:
    # 获取茅台历史行情
    python excel_wind.py wsd --code 600519.SH --fields close,open,high,low --begin 2026-01-01 --end 2026-04-03 --out茅台_kline.xlsx

    # 获取股票财务指标
    python excel_wind.py wss --code 600519.SH,000001.SZ --fields eps_basic,roe,pb --out财务指标.xlsx

    # 创建空白模板
    python excel_wind.py template --out Wind_Template.xlsx
"""

import sys
import os
import json
import time
import argparse
from pathlib import Path

# 尝试导入win32com
try:
    import win32com.client
    import pythoncom
    WIN32COM_AVAILABLE = True
except ImportError:
    WIN32COM_AVAILABLE = False
    print("[警告] win32com 未安装，将使用备用模式（仅生成公式字符串）")
    print("[提示] 安装方法: pip install pywin32")


# ============================================================
# 核心：Excel COM 操作
# ============================================================

def excel_com(operation, **kwargs):
    """
    通过 COM 操作 Excel。
    operation: init | write_formulas | refresh | read_range | save | close
    """
    if not WIN32COM_AVAILABLE:
        raise RuntimeError("win32com 不可用，请安装 pywin32")

    # 每个线程需要初始化 COM
    pythoncom.CoInitialize()

    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = kwargs.get("visible", False)
        excel.DisplayAlerts = kwargs.get("display_alerts", False)

        wb = None
        ws = None

        if operation == "init":
            template_path = kwargs.get("template")
            if template_path and os.path.exists(template_path):
                wb = excel.Workbooks.Open(os.path.abspath(template_path))
            else:
                wb = excel.Workbooks.Add()
            ws = wb.Worksheets.Add()
            ws.Name = kwargs.get("sheet_name", "Wind数据")
            return {"excel": excel, "wb": wb, "ws": ws, "success": True}

        elif operation == "write_formulas":
            ws = kwargs.get("ws")
            formulas = kwargs.get("formulas", [])  # [{"cell": "A1", "formula": "=WSD(...)"}, ...]
            for item in formulas:
                ws.Range(item["cell"]).Formula = item["formula"]
            return {"success": True, "written": len(formulas)}

        elif operation == "refresh":
            # 触发刷新（Excel 内置刷新）
            wb = kwargs.get("wb")
            ws = kwargs.get("ws")
            # 尝试刷新所有数据连接
            try:
                wb.RefreshAll()
                excel.Calculate()
            except Exception as e:
                print(f"[警告] RefreshAll 失败: {e}")
            # 等待一段时间让 Wind 插件完成取数
            wait_sec = kwargs.get("wait_sec", 15)
            print(f"[*] 等待 Wind 数据返回 ({wait_sec}秒)...")
            time.sleep(wait_sec)
            return {"success": True}

        elif operation == "read_range":
            ws = kwargs.get("ws")
            start_cell = kwargs.get("start_cell", "A1")
            end_cell = kwargs.get("end_cell")
            if end_cell:
                data = ws.Range(f"{start_cell}:{end_cell}").Value
            else:
                # 自动扩展到有数据的区域
                used = ws.UsedRange
                data = used.Value
            return {"success": True, "data": data}

        elif operation == "save":
            wb = kwargs.get("wb")
            output_path = kwargs.get("output_path")
            if output_path:
                wb.SaveAs(os.path.abspath(output_path))
            else:
                wb.Save()
            return {"success": True, "saved_to": output_path}

        elif operation == "close":
            wb = kwargs.get("wb")
            wb.Close(SaveChanges=kwargs.get("save", True))
            excel.Quit()
            return {"success": True}

        return {"success": False, "error": "未知操作"}

    finally:
        pythoncom.CoUninitialize()


# ============================================================
# Wind 公式构建器
# ============================================================

def build_wsd_formula(code, fields, begin_time, end_time, options=""):
    """构建 WSD 日时间序列公式"""
    fields_str = ";".join(fields) if isinstance(fields, list) else fields
    options_str = f'"{options}"' if options else '""'
    return f'=WSD("{code}", "{fields_str}", "{begin_time}", "{end_time}", {options_str})'


def build_wss_formula(code, fields, options=""):
    """构建 WSS 日截面数据公式"""
    fields_str = ";".join(fields) if isinstance(fields, list) else fields
    options_str = f'"{options}"' if options else '""'
    return f'=WSS("{code}", "{fields_str}", {options_str})'


def build_wsi_formula(code, fields, begin_time, end_time, options=""):
    """构建 WSI 分钟序列公式"""
    fields_str = ";".join(fields) if isinstance(fields, list) else fields
    options_str = f'"{options}"' if options else '""'
    return f'=WSI("{code}", "{fields_str}", "{begin_time}", "{end_time}", {options_str})'


def build_edi_formula(codes, indicator, begin_time, end_time, options=""):
    """构建 EDI 公式（宏观/行业数据）"""
    options_str = f'"{options}"' if options else '""'
    codes_str = ";".join(codes) if isinstance(codes, list) else codes
    return f'=EDI("{codes_str}", "{indicator}", "{begin_time}", "{end_time}", {options_str})'


# ============================================================
# 命令处理器
# ============================================================

def cmd_wsd(args):
    """获取日时间序列"""
    print(f"[*] 正在获取 WSD 数据: {args.code}")
    print(f"[*] 字段: {args.fields}")
    print(f"[*] 区间: {args.begin} ~ {args.end}")

    if WIN32COM_AVAILABLE:
        # 初始化 Excel
        init_result = excel_com("init", visible=args.visible, sheet_name="WSD_K线")
        ws = init_result["ws"]

        # 写入表头
        fields_list = args.fields.split(",")
        ws.Range("A1").Value = "日期"
        for i, field in enumerate(fields_list, start=2):
            ws.Cells(1, i).Value = field

        # 写入公式（A2 开始）
        formula = build_wsd_formula(args.code, fields_list, args.begin, args.end, args.options)
        ws.Range("B2").Formula = formula

        # 刷新
        excel_com("refresh", wb=init_result["wb"], ws=ws, wait_sec=args.wait)

        # 读取数据
        result = excel_com("read_range", ws=ws, start_cell="A1")
        data = result["data"]

        # 保存
        if args.out:
            excel_com("save", wb=init_result["wb"], output_path=args.out)
        excel_com("close", wb=init_result["wb"], save=bool(args.out))

        print(f"[+] 数据获取完成，行数: {len(data) if data else 0}")
        return data
    else:
        # 纯公式模式（无 COM）
        formula = build_wsd_formula(args.code, fields_list, args.begin, args.end, args.options)
        print(f"[公式] 复制以下内容到 Excel 单元格中:")
        print(formula)
        return None


def cmd_wss(args):
    """获取日截面数据"""
    print(f"[*] 正在获取 WSS 数据: {args.code}")
    print(f"[*] 字段: {args.fields}")

    fields_list = args.fields.split(",")

    if WIN32COM_AVAILABLE:
        init_result = excel_com("init", visible=args.visible, sheet_name="WSS_指标")
        ws = init_result["ws"]

        # 写入表头
        codes_list = args.code.split(",")
        ws.Range("A1").Value = "股票代码"
        for i, field in enumerate(fields_list, start=2):
            ws.Cells(1, i).Value = field

        # 写入公式
        for row_idx, code in enumerate(codes_list, start=2):
            ws.Cells(row_idx, 1).Value = code
            formula = build_wss_formula(code.strip(), fields_list, args.options)
            ws.Cells(row_idx, 2).Formula = formula

        # 刷新
        excel_com("refresh", wb=init_result["wb"], ws=ws, wait_sec=args.wait)

        # 读取数据
        result = excel_com("read_range", ws=ws, start_cell="A1")

        # 保存
        if args.out:
            excel_com("save", wb=init_result["wb"], output_path=args.out)
        excel_com("close", wb=init_result["wb"], save=bool(args.out))

        print(f"[+] 数据获取完成")
        return result["data"]
    else:
        for code in codes_list:
            formula = build_wss_formula(code.strip(), fields_list, args.options)
            print(f"[公式] {code}: {formula}")
        return None


def cmd_template(args):
    """创建空白模板"""
    print(f"[*] 创建 Wind 数据模板...")

    if WIN32COM_AVAILABLE:
        init_result = excel_com("init", visible=args.visible, sheet_name="Wind公式")
        ws = init_result["ws"]

        # 预填示例公式
        ws.Range("A1").Value = "证券代码"
        ws.Range("B1").Value = "=WSD(A2,\"close\",\"2026-01-01\",\"2026-04-03\",\"\")"
        ws.Range("A2").Value = "000001.SH"

        ws.Range("D1").Value = "WSS示例"
        ws.Range("D2").Value = "=WSS(A2,\"open;high;low;close\",\"\")"

        excel_com("save", wb=init_result["wb"], output_path=args.out)
        excel_com("close", wb=init_result["wb"], save=True)

        print(f"[+] 模板已保存: {args.out}")
        return True
    else:
        print("[错误] 需要 win32com 支持才能创建模板")
        return False


def cmd_query(args):
    """通用查询：支持混合 WSD/WSS"""
    print(f"[*] 执行通用 Wind 查询...")

    if WIN32COM_AVAILABLE:
        init_result = excel_com("init", visible=args.visible, sheet_name="Wind查询")
        ws = init_result["ws"]

        # 解析 JSON 公式文件
        if args.formulas:
            with open(args.formulas, "r", encoding="utf-8") as f:
                formula_config = json.load(f)

            row = 1
            for item in formula_config.get("formulas", []):
                ws.Cells(row, 1).Value = item.get("name", f"公式{row}")
                ws.Cells(row, 2).Formula = item["formula"]
                row += 1

        # 刷新
        excel_com("refresh", wb=init_result["wb"], ws=ws, wait_sec=args.wait)

        # 保存
        if args.out:
            excel_com("save", wb=init_result["wb"], output_path=args.out)
        excel_com("close", wb=init_result["wb"], save=bool(args.out))

        print(f"[+] 查询完成")
        return True
    else:
        print("[错误] 需要 win32com 支持")
        return False


# ============================================================
# 主入口
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Excel+Wind插件自动化工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # WSD 命令
    p_wsd = subparsers.add_parser("wsd", help="获取日时间序列（历史K线）")
    p_wsd.add_argument("--code", required=True, help="证券代码，如 600519.SH")
    p_wsd.add_argument("--fields", required=True, help="字段列表，如 close,open,high")
    p_wsd.add_argument("--begin", required=True, help="开始日期，如 2026-01-01")
    p_wsd.add_argument("--end", required=True, help="结束日期，如 2026-04-03")
    p_wsd.add_argument("--options", default="", help="Wind选项，如 PriceAdj=F")
    p_wsd.add_argument("--out", help="输出文件路径")
    p_wsd.add_argument("--wait", type=int, default=15, help="等待秒数（默认15秒）")
    p_wsd.add_argument("--visible", action="store_true", help="显示Excel窗口")

    # WSS 命令
    p_wss = subparsers.add_parser("wss", help="获取日截面数据（指标）")
    p_wss.add_argument("--code", required=True, help="证券代码，多个用逗号分隔")
    p_wss.add_argument("--fields", required=True, help="字段列表")
    p_wss.add_argument("--options", default="", help="Wind选项")
    p_wss.add_argument("--out", help="输出文件路径")
    p_wss.add_argument("--wait", type=int, default=15, help="等待秒数")
    p_wss.add_argument("--visible", action="store_true", help="显示Excel窗口")

    # Template 命令
    p_tpl = subparsers.add_parser("template", help="创建空白模板")
    p_tpl.add_argument("--out", required=True, help="输出文件路径")
    p_tpl.add_argument("--visible", action="store_true", help="显示Excel窗口")

    # Query 命令
    p_q = subparsers.add_parser("query", help="通用查询（JSON配置）")
    p_q.add_argument("--formulas", required=True, help="JSON公式配置文件路径")
    p_q.add_argument("--out", help="输出文件路径")
    p_q.add_argument("--wait", type=int, default=15, help="等待秒数")
    p_q.add_argument("--visible", action="store_true", help="显示Excel窗口")

    args = parser.parse_args()

    if args.command == "wsd":
        cmd_wsd(args)
    elif args.command == "wss":
        cmd_wss(args)
    elif args.command == "template":
        cmd_template(args)
    elif args.command == "query":
        cmd_query(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
