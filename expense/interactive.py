# -*- coding: utf-8 -*-
"""
差旅报销 - 交互式菜单程序
运行方式：python interactive.py
"""

import os
import sys
from pathlib import Path

# 添加 skills/expense 目录到 sys.path，以便导入同目录下的模块
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

import pandas as pd
from datetime import datetime
import config
from import_statements import import_statement
from match_invoices import scan_invoices, match_invoices_with_statements
from mark_expenses import auto_mark_by_threshold, get_expense_summary


# ─────────────────────────────────────────────
# 颜色定义
# ─────────────────────────────────────────────
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'


def c(text, color):
    return f"{color}{text}{Colors.END}"


# ─────────────────────────────────────────────
# 工具函数
# ─────────────────────────────────────────────
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def pause():
    input(c("\n按 Enter 继续...", Colors.YELLOW))


def print_banner():
    clear()
    print(c("""
╔══════════════════════════════════════════════╗
║     🏆 差旅报销数据处理工具  v1.0            ║
║     Travel Expense Manager                   ║
╚══════════════════════════════════════════════╝
""", Colors.CYAN + Colors.BOLD))


def print_menu(options, title="请选择操作:"):
    print(c(f"\n{title}", Colors.BOLD))
    print("-" * 40)
    for i, opt in enumerate(options, 1):
        label = opt['label']
        desc = opt.get('desc', '')
        print(f"  {c(f'[{i}]', Colors.GREEN)} {label}")
        if desc:
            print(f"      {c(desc, Colors.YELLOW)}")
    print("-" * 40)
    print(f"  {c('[0]', Colors.RED)} 退出程序")
    print()


def get_choice(max_choice):
    while True:
        try:
            choice = input(c("→ 请输入选项: ", Colors.CYAN)).strip()
            if choice == '0':
                return 0
            n = int(choice)
            if 1 <= n <= max_choice:
                return n
            print(c("⚠️  无效选项，请重试", Colors.RED))
        except ValueError:
            print(c("⚠️  请输入数字", Colors.RED))


def ensure_data_dirs():
    """确保数据目录存在"""
    config.ensure_dirs()
    print(c(f"  📁 流水目录: {config.STATEMENTS_DIR}", Colors.BLUE))
    print(c(f"  📁 发票目录: {config.INVOICE_DIR}", Colors.BLUE))
    print(c(f"  📁 输出目录: {config.OUTPUT_DIR}", Colors.BLUE))


def get_statements_file():
    return config.DATA_ROOT / "statements" / "combined_statements.csv"


def load_combined_statements():
    """加载已合并的流水数据"""
    f = get_statements_file()
    if f.exists():
        df = pd.read_csv(f)
        return df
    return None


def save_combined_statements(df):
    """保存合并后的流水数据"""
    f = get_statements_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(f, index=False, encoding='utf-8-sig')
    print(c(f"  💾 已保存: {f}", Colors.GREEN))


def list_csv_files(directory):
    """列出目录下的CSV文件"""
    d = Path(directory)
    if not d.exists():
        return []
    return list(d.glob("*.csv"))


# ─────────────────────────────────────────────
# 菜单操作函数
# ─────────────────────────────────────────────

def op_import_statements():
    """导入银行流水"""
    print_banner()
    print(c("📥 导入银行流水\n", Colors.BOLD))

    sources = [
        {"id": "wechat", "name": "微信支付", "desc": "微信 → 我 → 服务 → 钱包 → 账单 → 账单下载"},
        {"id": "alipay", "name": "支付宝", "desc": "支付宝 → 我的 → 账单 → 导出账单"},
        {"id": "cmb", "name": "招商银行商务卡(8651)", "desc": "掌上生活 → 账单 → 导出"},
    ]

    print("支持的流水来源:\n")
    for i, s in enumerate(sources, 1):
        print(f"  {c(f'[{i}]', Colors.GREEN)} {s['name']}")
        print(f"      {c(s['desc'], Colors.YELLOW)}\n")

    # 选择来源
    src_choice = input(c("请选择来源 [1-3](默认1微信): ", Colors.CYAN)).strip()
    if not src_choice:
        src_choice = '1'
    try:
        source_id = sources[int(src_choice) - 1]['id']
        source_name = sources[int(src_choice) - 1]['name']
    except (ValueError, IndexError):
        print(c("⚠️ 无效选项，使用微信支付", Colors.RED))
        source_id = 'wechat'
        source_name = '微信支付'

    # 选择文件
    csv_files = list_csv_files(config.STATEMENTS_DIR)
    if not csv_files:
        print(c(f"\n❌ statements 目录为空: {config.STATEMENTS_DIR}", Colors.RED))
        print(c("   请先将 CSV 文件放入该目录", Colors.YELLOW))
        pause()
        return

    print(c(f"\n找到 {len(csv_files)} 个 CSV 文件:\n", Colors.BOLD))
    for i, f in enumerate(csv_files, 1):
        print(f"  {c(f'[{i}]', Colors.GREEN)} {f.name}")
    print()

    file_choice = input(c("请选择文件编号: ", Colors.CYAN)).strip()
    try:
        selected_file = csv_files[int(file_choice) - 1]
    except (ValueError, IndexError):
        print(c("⚠️ 无效选项", Colors.RED))
        pause()
        return

    # 导入
    print(c(f"\n📥 正在导入 {source_name} 账单...", Colors.BOLD))
    try:
        df_new = import_statement(source_id, selected_file)

        # 合并
        df_existing = load_combined_statements()
        if df_existing is not None:
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            # 去重
            df_combined = df_combined.drop_duplicates(
                subset=['date', 'amount', 'merchant'], keep='last'
            )
            print(c(f"  合并后共 {len(df_combined)} 条记录", Colors.GREEN))
        else:
            df_combined = df_new

        # 自动按阈值标记
        df_combined = auto_mark_by_threshold(df_combined)
        save_combined_statements(df_combined)

        print(c(f"\n✅ 导入成功! 共 {len(df_combined)} 条流水记录", Colors.GREEN))
    except Exception as e:
        print(c(f"\n❌ 导入失败: {e}", Colors.RED))

    pause()


def op_scan_invoices():
    """扫描发票目录"""
    print_banner()
    print(c("📋 扫描发票目录\n", Colors.BOLD))
    print(c(f"  📁 {config.INVOICE_DIR}\n", Colors.BLUE))

    invoices = scan_invoices(config.INVOICE_DIR)

    if not invoices:
        print(c("  ⚠️ 未找到任何发票文件(XML/PDF)", Colors.YELLOW))
        print(c("  请将数电发票放入发票目录", Colors.YELLOW))
    else:
        print(c(f"\n  ✅ 共找到 {len(invoices)} 张发票\n", Colors.GREEN))
        for inv in invoices:
            print(f"    {inv.invoice_id} | ¥{inv.amount:.2f} | {inv.date} | {inv.seller_name}")

    pause()


def op_match():
    """匹配发票与流水"""
    print_banner()
    print(c("🔍 匹配发票与流水\n", Colors.BOLD))

    df = load_combined_statements()
    if df is None or len(df) == 0:
        print(c("❌ 尚未导入流水数据，请先导入", Colors.RED))
        pause()
        return

    print(f"  当前流水: {len(df)} 条")

    invoices = scan_invoices(config.INVOICE_DIR)
    if not invoices:
        print(c("❌ 发票目录为空，无法匹配", Colors.RED))
        pause()
        return

    print(c(f"\n  正在匹配 {len(invoices)} 张发票与 {len(df)} 条流水...", Colors.YELLOW))

    # 转换日期
    if 'date' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # 匹配
    matches, unmatched_inv, unmatched_stmt = match_invoices_with_statements(invoices, df)

    # 更新 DataFrame
    for match in matches:
        mask = (
            (df['date'] == match['statement']['date']) &
            (abs(df['amount'] - match['invoice'].amount) < 0.01)
        )
        if mask.any():
            idx = df[mask].index[0]
            df.loc[idx, 'invoice_id'] = match['invoice'].invoice_id
            df.loc[idx, 'reimburse_status'] = 'invoiced'

    save_combined_statements(df)

    # 结果
    print(c("\n📊 匹配结果:\n", Colors.BOLD))
    print(f"  ✅ 高置信匹配: {len([m for m in matches if m['confidence'] >= 80])} 条")
    print(f"  ⚠️  中置信匹配: {len([m for m in matches if m['confidence'] < 80])} 条")
    print(f"  ❌ 未匹配发票: {len(unmatched_inv)} 张")
    print(f"  ⚠️  未匹配流水: {len(unmatched_stmt)} 条")

    if unmatched_inv:
        print(c("\n  未匹配发票(请检查是否需要手动关联):", Colors.YELLOW))
        for inv in unmatched_inv[:10]:
            print(f"    {inv.invoice_id} | ¥{inv.amount:.2f} | {inv.date}")
        if len(unmatched_inv) > 10:
            print(f"    ... 还有 {len(unmatched_inv) - 10} 张")

    if unmatched_stmt:
        print(c("\n  未匹配流水(可能缺发票):", Colors.YELLOW))
        for stmt in unmatched_stmt[:10]:
            print(f"    ¥{stmt.get('amount', 0):.2f} | {stmt.get('merchant', '未知')} | {stmt.get('date', '')}")
        if len(unmatched_stmt) > 10:
            print(f"    ... 还有 {len(unmatched_stmt) - 10} 条")

    pause()


def op_mark():
    """标记垫款"""
    print_banner()
    print(c("🏷️  标记公司垫款\n", Colors.BOLD))

    df = load_combined_statements()
    if df is None or len(df) == 0:
        print(c("❌ 尚未导入流水数据", Colors.RED))
        pause()
        return

    print(f"  当前流水: {len(df)} 条")
    print(f"  大额阈值: ¥{config.LARGE_AMOUNT_THRESHOLD}\n")

    # 自动按阈值标记
    df = auto_mark_by_threshold(df)
    save_combined_statements(df)

    # 交互确认大额记录
    large = df[df['amount'] >= config.LARGE_AMOUNT_THRESHOLD].copy()
    if len(large) == 0:
        print(c("  没有超过阈值的大额消费", Colors.GREEN))
        pause()
        return

    print(c(f"\n  有 {len(large)} 条消费超过阈值，需要确认:\n", Colors.YELLOW))

    confirmed = 0
    for idx, row in large.iterrows():
        print(f"\n  {c('─'*40', Colors.BLUE}")
        print(f"  💰 金额: ¥{row['amount']:.2f}")
        print(f"  🏪 商户: {row.get('merchant', '未知')}")
        print(f"  📅 日期: {row.get('date', '未知')}")
        print(f"  📱 来源: {config.PAYMENT_SOURCES.get(row.get('source', ''), row.get('source', '未知'))}")
        print(f"  📌 标记: {row.get('is_company_expense', '?')}")

        action = input(c("  → 确认公司垫款? (y/n/q): ", Colors.CYAN)).strip().lower()
        if action == 'y':
            df.at[idx, 'is_company_expense'] = '是'
            confirmed += 1
        elif action == 'n':
            df.at[idx, 'is_company_expense'] = '否'
        elif action == 'q':
            break

    save_combined_statements(df)
    get_expense_summary(df)
    print(c(f"\n✅ 确认了 {confirmed} 条公司垫款", Colors.GREEN))
    pause()


def op_report():
    """生成报销报表"""
    print_banner()
    print(c("📊 生成报销报表\n", Colors.BOLD))

    df = load_combined_statements()
    if df is None or len(df) == 0:
        print(c("❌ 尚未导入流水数据", Colors.RED))
        pause()
        return

    company = df[df['is_company_expense'] == '是'].copy()
    if len(company) == 0:
        print(c("⚠️ 没有标记为公司垫款的消费", Colors.YELLOW))
        pause()
        return

    # 分组
    pending = company[company['reimburse_status'] == 'pending']
    invoiced = company[company['reimburse_status'] == 'invoiced']
    reimbursed = company[company['reimburse_status'] == 'reimbursed']

    # 生成文件
    date_str = datetime.now().strftime('%Y-%m-%d')
    report_file = config.OUTPUT_DIR / f"报销核对清单_{date_str}.xlsx"
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(report_file, engine='openpyxl') as writer:
        # 汇总
        summary = pd.DataFrame({
            '项目': ['总垫款金额', '未提交', '已开发票', '已报销'],
            '笔数': [len(company), len(pending), len(invoiced), len(reimbursed)],
            '金额': [
                company['amount'].sum(),
                pending['amount'].sum() if len(pending) else 0,
                invoiced['amount'].sum() if len(invoiced) else 0,
                reimbursed['amount'].sum() if len(reimbursed) else 0,
            ]
        })
        summary.to_excel(writer, sheet_name='汇总', index=False)

        if len(pending) > 0:
            pending.to_excel(writer, sheet_name='待提交', index=False)
        if len(invoiced) > 0:
            invoiced.to_excel(writer, sheet_name='已开发票', index=False)
        if len(reimbursed) > 0:
            reimbursed.to_excel(writer, sheet_name='已报销', index=False)
        company.to_excel(writer, sheet_name='全部垫款', index=False)

    print(c(f"\n✅ 报表已生成!\n", Colors.GREEN))
    print(f"  📁 {report_file}")
    print(f"\n  📊 统计:")
    print(f"     总垫款: ¥{company['amount'].sum():,.2f} ({len(company)} 笔)")
    print(f"     待提交: ¥{pending['amount'].sum():,.2f} ({len(pending)} 笔)")
    print(f"     已开发票: ¥{invoiced['amount'].sum():,.2f} ({len(invoiced)} 笔)")
    print(f"     已报销: ¥{reimbursed['amount'].sum():,.2f} ({len(reimbursed)} 笔)")

    pause()


def op_status():
    """查看当前状态"""
    print_banner()
    print(c("📊 当前数据状态\n", Colors.BOLD))

    df = load_combined_statements()
    if df is None or len(df) == 0:
        print(c("❌ 尚未导入任何流水数据", Colors.RED))
        print(f"\n  请先将 CSV 流水文件放入:\n  {config.STATEMENTS_DIR}\n")
        print("  然后选择 [1] 导入流水 开始使用")
    else:
        print(f"  📁 流水文件: {get_statements_file().name}")
        print(f"  📊 总记录: {len(df)} 条\n")

        print(c("  按来源分布:", Colors.BOLD))
        for src, cnt in df['source'].value_counts().items():
            name = config.PAYMENT_SOURCES.get(src, src)
            print(f"    {name}: {cnt} 条")

        print()
        get_expense_summary(df)

        # 检查未匹配
        if 'invoice_id' in df.columns:
            unmatched = df[(df['is_company_expense'] == '是') & (df['invoice_id'] == '')]
            if len(unmatched) > 0:
                print(c(f"\n  ⚠️  有 {len(unmatched)} 笔垫款尚未关联发票", Colors.YELLOW))

    print(f"\n  📂 目录信息:")
    print(f"     流水: {config.STATEMENTS_DIR}")
    csv_count = len(list_csv_files(config.STATEMENTS_DIR))
    print(f"     待导入CSV: {csv_count} 个")

    inv_list = scan_invoices(config.INVOICE_DIR)
    print(f"     发票: {len(inv_list)} 张")

    pause()


def op_guide():
    """使用指南"""
    print_banner()
    print(c("📖 使用指南\n", Colors.BOLD + Colors.CYAN))

    guide = """
    【首次使用流程】

    ① 导出账单
       微信: 微信 → 我 → 服务 → 钱包 → 账单 → 账单下载
       支付宝: 支付宝 → 我的 → 账单 → 导出账单
       招商银行: 掌上生活 → 账单 → 导出

    ② 将 CSV 文件放入目录
       C:\\Users\\123\\openclaw_data\\expense\\statements\\

    ③ 回到本程序，依次操作:
       [1] 导入流水  →  选择来源和文件
       [2] 扫描发票  →  确认发票已录入
       [3] 匹配发票  →  自动关联发票与流水
       [4] 标记垫款  →  确认大额消费
       [5] 生成报表  →  导出报销核对清单

    【每月操作】
       每月初导入上月流水，匹配发票，标记垫款，
       生成报表后上传至公司发票云发起报销。

    【数据存放】
       所有数据保存在:
       C:\\Users\\123\\openclaw_data\\expense\\
    """
    print(guide)
    pause()


# ─────────────────────────────────────────────
# 主程序
# ─────────────────────────────────────────────

def main():
    ensure_data_dirs()

    while True:
        print_banner()

        menu_options = [
            {"label": "导入流水", "desc": "从CSV文件导入微信/支付宝/招行账单"},
            {"label": "扫描发票", "desc": "扫描发票目录，检查已收录发票"},
            {"label": "匹配发票", "desc": "自动将发票与流水记录关联"},
            {"label": "标记垫款", "desc": "确认大额消费为公司垫款"},
            {"label": "生成报表", "desc": "导出报销核对清单 Excel"},
            {"label": "查看状态", "desc": "查看当前数据汇总"},
            {"label": "使用指南", "desc": "查看操作流程说明"},
        ]

        print_menu(menu_options)
        choice = get_choice(len(menu_options))

        if choice == 0:
            print(c("\n👋 再见！报销顺利～\n", Colors.CYAN + Colors.BOLD))
            break
        elif choice == 1:
            op_import_statements()
        elif choice == 2:
            op_scan_invoices()
        elif choice == 3:
            op_match()
        elif choice == 4:
            op_mark()
        elif choice == 5:
            op_report()
        elif choice == 6:
            op_status()
        elif choice == 7:
            op_guide()


if __name__ == "__main__":
    main()
