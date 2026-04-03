# -*- coding: utf-8 -*-
"""
差旅报销数据处理 - 主程序
整合流水导入、发票匹配、垫款标记、报表生成

使用方式:
    python main.py import --source wechat --file 微信账单.csv
    python main.py import --source alipay --file 支付宝账单.csv
    python main.py import --source cmb --file 招行账单.csv
    python main.py scan               # 扫描发票目录
    python main.py match              # 匹配发票与流水
    python main.py mark               # 交互式标记垫款
    python main.py report             # 生成报销报表
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd

# 导入各模块
from config import (
    DATA_ROOT, STATEMENTS_DIR, INVOICE_DIR, OUTPUT_DIR,
    PAYMENT_SOURCES, EXPENSE_STATUS, ensure_dirs
)
from import_statements import import_statement, WeChatImporter, AlipayImporter, CMBImporter
from match_invoices import scan_invoices, match_invoices_with_statements
from mark_expenses import (
    mark_interactive, auto_mark_by_threshold, 
    get_expense_summary, set_reimburse_status
)


# 全局变量：存储当前加载的流水数据
_current_statements = None
_statements_file = None


def get_statements_file():
    """获取当前流水数据文件路径"""
    return DATA_ROOT / "statements" / "combined_statements.csv"


def load_statements():
    """加载已保存的流水数据"""
    global _current_statements, _statements_file
    _statements_file = get_statements_file()
    
    if _statements_file.exists():
        _current_statements = pd.read_csv(_statements_file)
        print(f"📂 已加载流水数据: {len(_current_statements)} 条记录")
        return _current_statements
    else:
        print("📂 尚未导入流水数据，请先使用 import 命令")
        return None


def save_statements(df):
    """保存流水数据"""
    global _statements_file
    if _statements_file is None:
        _statements_file = get_statements_file()
    
    ensure_dirs()
    _statements_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(_statements_file, index=False, encoding='utf-8-sig')
    print(f"💾 流水数据已保存: {_statements_file}")


def cmd_import(args):
    """导入流水命令"""
    global _current_statements
    
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 导入数据
    df = import_statement(args.source, file_path)
    
    # 加载已有数据并合并
    existing = load_statements() if _current_statements is not None else None
    
    if existing is not None:
        # 合并（去重）
        combined = pd.concat([existing, df], ignore_index=True)
        combined = combined.drop_duplicates(subset=['date', 'amount', 'merchant'], keep='last')
        _current_statements = combined
        print(f"📊 合并后共 {len(combined)} 条记录")
    else:
        _current_statements = df
    
    save_statements(_current_statements)
    
    # 自动按阈值标记
    _current_statements = auto_mark_by_threshold(_current_statements)
    save_statements(_current_statements)


def cmd_scan(args):
    """扫描发票目录"""
    invoices = scan_invoices(INVOICE_DIR)
    
    if not invoices:
        print(f"\n📂 发票目录为空: {INVOICE_DIR}")
        print("   请将数电发票(XML/PDF)放入此目录")
    
    return invoices


def cmd_match(args):
    """匹配发票与流水"""
    global _current_statements
    
    df = load_statements()
    if df is None or len(df) == 0:
        print("❌ 没有可匹配的流水数据")
        return
    
    # 扫描发票
    invoices = scan_invoices(INVOICE_DIR)
    
    if not invoices:
        print("❌ 发票目录为空，无法匹配")
        return
    
    # 转换日期列
    if 'date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # 匹配
    matches, unmatched_inv, unmatched_stmt = match_invoices_with_statements(invoices, df)
    
    # 更新流水数据中的发票关联
    for match in matches:
        stmt_idx = df[
            (df['date'] == match['statement']['date']) & 
            (abs(df['amount'] - match['invoice'].amount) < 0.01)
        ].index
        
        if len(stmt_idx) > 0:
            df.loc[stmt_idx[0], 'invoice_id'] = match['invoice'].invoice_id
            df.loc[stmt_idx[0], 'reimburse_status'] = 'invoiced'
    
    _current_statements = df
    save_statements(df)
    
    return matches, unmatched_inv, unmatched_stmt


def cmd_mark(args):
    """交互式标记垫款"""
    global _current_statements
    
    df = load_statements()
    if df is None or len(df) == 0:
        print("❌ 没有可标记的流水数据")
        return
    
    # 如果指定了自动模式
    if args.auto:
        _current_statements = auto_mark_by_threshold(df, args.auto)
    else:
        # 交互式标记
        _current_statements = mark_interactive(df)
    
    save_statements(_current_statements)
    get_expense_summary(_current_statements)


def cmd_report(args):
    """生成报销报表"""
    global _current_statements
    
    df = load_statements()
    if df is None or len(df) == 0:
        print("❌ 没有可生成报表的数据")
        return
    
    ensure_dirs()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # 筛选公司垫款
    company_expenses = df[df['is_company_expense'] == '是'].copy()
    
    # 按状态分组
    pending = company_expenses[company_expenses['reimburse_status'] == 'pending']
    invoiced = company_expenses[company_expenses['reimburse_status'] == 'invoiced']
    reimbursed = company_expenses[company_expenses['reimburse_status'] == 'reimbursed']
    
    # 生成报表文件名
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_file = OUTPUT_DIR / f"报销核对清单_{date_str}.xlsx"
    
    # 写入Excel
    with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
        # 汇总
        summary_data = {
            '项目': ['总垫款金额', '未提交', '已开发票', '已报销'],
            '笔数': [len(company_expenses), len(pending), len(invoiced), len(reimbursed)],
            '金额': [
                company_expenses['amount'].sum(),
                pending['amount'].sum(),
                invoiced['amount'].sum(),
                reimbursed['amount'].sum()
            ]
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='汇总', index=False)
        
        # 未提交明细
        if len(pending) > 0:
            pending.to_excel(writer, sheet_name='待提交', index=False)
        
        # 已开发票明细
        if len(invoiced) > 0:
            invoiced.to_excel(writer, sheet_name='已开发票', index=False)
        
        # 已报销明细
        if len(reimbursed) > 0:
            reimbursed.to_excel(writer, sheet_name='已报销', index=False)
        
        # 全部记录
        company_expenses.to_excel(writer, sheet_name='全部垫款', index=False)
    
    print(f"\n✅ 报表已生成: {report_file}")
    print(f"   工作表: 汇总、待提交、已开发票、已报销、全部垫款")
    
    # 打印摘要
    get_expense_summary(df)
    
    return report_file


def cmd_status(args):
    """查看当前状态"""
    df = load_statements()
    
    if df is None or len(df) == 0:
        print("❌ 尚未导入流水数据")
        return
    
    print("\n" + "=" * 50)
    print("📊 当前数据状态")
    print("=" * 50)
    print(f"总记录数: {len(df)}")
    print(f"数据来源分布:")
    print(df['source'].value_counts().to_string())
    print()
    get_expense_summary(df)


def main():
    parser = argparse.ArgumentParser(
        description='差旅报销数据处理工具',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='子命令')
    
    # import 命令
    import_parser = subparsers.add_parser('import', help='导入银行流水')
    import_parser.add_argument('--source', required=True, 
                               choices=['wechat', 'alipay', 'cmb'],
                               help='流水来源')
    import_parser.add_argument('--file', required=True,
                               help='CSV文件路径')
    import_parser.set_defaults(func=cmd_import)
    
    # scan 命令
    scan_parser = subparsers.add_parser('scan', help='扫描发票目录')
    scan_parser.set_defaults(func=cmd_scan)
    
    # match 命令
    match_parser = subparsers.add_parser('match', help='匹配发票与流水')
    match_parser.set_defaults(func=cmd_match)
    
    # mark 命令
    mark_parser = subparsers.add_parser('mark', help='标记垫款')
    mark_parser.add_argument('--auto', type=float, metavar='阈值',
                            help='自动标记超过此金额的消费为垫款')
    mark_parser.set_defaults(func=cmd_mark)
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='生成报销报表')
    report_parser.set_defaults(func=cmd_report)
    
    # status 命令
    status_parser = subparsers.add_parser('status', help='查看当前状态')
    status_parser.set_defaults(func=cmd_status)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print("\n" + "=" * 50)
        print("📖 使用示例:")
        print("=" * 50)
        print("# 1. 导入流水")
        print("python main.py import --source wechat --file 微信账单.csv")
        print("python main.py import --source alipay --file 支付宝账单.csv")
        print("python main.py import --source cmb --file 招行账单.csv")
        print()
        print("# 2. 扫描发票")
        print("python main.py scan")
        print()
        print("# 3. 匹配发票与流水")
        print("python main.py match")
        print()
        print("# 4. 标记垫款")
        print("python main.py mark          # 交互式")
        print("python main.py mark --auto 500  # 自动标记500元以上")
        print()
        print("# 5. 生成报表")
        print("python main.py report")
        print()
        print("# 6. 查看状态")
        print("python main.py status")
        return
    
    # 确保目录存在
    ensure_dirs()
    
    # 执行命令
    args.func(args)


if __name__ == "__main__":
    print("=" * 50)
    print("🏆 差旅报销数据处理工具 v1.0")
    print("=" * 50)
    main()
