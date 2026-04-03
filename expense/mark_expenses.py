# -*- coding: utf-8 -*-
"""
垫款标记模块
交互式标记公司垫款，设置报销状态
"""

import pandas as pd
from pathlib import Path
from config import LARGE_AMOUNT_THRESHOLD, EXPENSE_STATUS, OUTPUT_DIR


def load_statements_from_csv(csv_path):
    """从CSV加载流水数据"""
    return pd.read_csv(csv_path)


def save_statements_to_csv(df, csv_path):
    """保存流水数据到CSV"""
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"  💾 已保存: {csv_path}")


def mark_interactive(df):
    """
    交互式标记垫款
    
    显示待确认的流水记录，提示用户标记
    """
    print("\n" + "=" * 60)
    print("🏷️  垫款标记工具")
    print("=" * 60)
    print(f"\n大额阈值: ¥{LARGE_AMOUNT_THRESHOLD} (超过此金额自动标记为'可能公司垫款')")
    print("\n操作说明:")
    print("  输入 'y' - 确认是公司垫款")
    print("  输入 'n' - 确认是个人消费")
    print("  输入 's' - 跳过此条，处理下一条")
    print("  输入 'q' - 退出标记")
    print()
    
    # 筛选出需要确认的记录（金额>=阈值，或自动标记为可能的垫款）
    needs_confirmation = df[
        (df['amount'] >= LARGE_AMOUNT_THRESHOLD) | 
        (df['is_company_expense'] == '是')
    ].copy()
    
    if len(needs_confirmation) == 0:
        print("  ✅ 没有需要标记的记录")
        return df
    
    print(f"📋 共有 {len(needs_confirmation)} 条记录需要确认\n")
    
    confirmed_count = 0
    for idx, row in needs_confirmation.iterrows():
        print("-" * 50)
        print(f"💰 金额: ¥{row['amount']:.2f}")
        print(f"🏪 商户: {row.get('merchant', '未知')}")
        print(f"📅 日期: {row.get('date', '未知')}")
        print(f"📱 来源: {row.get('source', '未知')}")
        print(f"📌 当前状态: {row.get('is_company_expense', '未知')}")
        
        action = input("\n→ 这是公司垫款吗? (y/n/s/q): ").strip().lower()
        
        if action == 'q':
            print("\n👋 退出标记")
            break
        elif action == 'y':
            df.at[idx, 'is_company_expense'] = '是'
            confirmed_count += 1
            print("   ✓ 已标记为公司垫款")
        elif action == 'n':
            df.at[idx, 'is_company_expense'] = '否'
            print("   ✓ 已标记为个人消费")
        else:  # 's'
            print("   ⊙ 已跳过")
    
    print(f"\n✅ 标记完成! 确认了 {confirmed_count} 条公司垫款")
    return df


def auto_mark_by_threshold(df, threshold=None):
    """
    根据阈值自动标记垫款
    
    Args:
        df: 流水DataFrame
        threshold: 金额阈值，默认使用配置中的LARGE_AMOUNT_THRESHOLD
    """
    if threshold is None:
        threshold = LARGE_AMOUNT_THRESHOLD
    
    before_count = len(df[df['is_company_expense'] == '是'])
    
    df['is_company_expense'] = df['amount'].apply(
        lambda x: '是' if x >= threshold else '否'
    )
    
    after_count = len(df[df['is_company_expense'] == '是'])
    new_marked = after_count - before_count
    
    print(f"\n🔧 自动标记完成 (阈值≥¥{threshold}):")
    print(f"   新标记为垫款: {new_marked} 条")
    print(f"   垫款总计: {after_count} 条")
    
    return df


def set_reimburse_status(df, invoice_id, status='invoiced'):
    """
    批量设置报销状态
    
    Args:
        df: 流水DataFrame
        invoice_id: 发票号码（字符串或正则表达式）
        status: 'pending' | 'invoiced' | 'reimbursed'
    """
    status_display = EXPENSE_STATUS.get(status, status)
    
    # 简单匹配：如果发票号在流水备注或关联字段中
    mask = df['invoice_id'].astype(str).str.contains(str(invoice_id), na=False)
    df.loc[mask, 'reimburse_status'] = status
    df.loc[mask, 'invoice_id'] = invoice_id
    
    count = mask.sum()
    print(f"\n📝 已将 {count} 条记录状态设置为: {status_display}")
    
    return df


def get_expense_summary(df):
    """
    获取报销统计摘要
    """
    total_amount = df[df['is_company_expense'] == '是']['amount'].sum()
    pending = df[
        (df['is_company_expense'] == '是') & 
        (df['reimburse_status'] == 'pending')
    ]
    invoiced = df[
        (df['is_company_expense'] == '是') & 
        (df['reimburse_status'] == 'invoiced')
    ]
    reimbursed = df[
        (df['is_company_expense'] == '是') & 
        (df['reimburse_status'] == 'reimbursed')
    ]
    
    print("\n" + "=" * 50)
    print("📊 报销统计摘要")
    print("=" * 50)
    print(f"总垫款金额: ¥{total_amount:,.2f}")
    print(f"  - 未提交: {len(pending)} 笔, ¥{pending['amount'].sum():,.2f}")
    print(f"  - 已开发票: {len(invoiced)} 笔, ¥{invoiced['amount'].sum():,.2f}")
    print(f"  - 已报销: {len(reimbursed)} 笔, ¥{reimbursed['amount'].sum():,.2f}")
    print("=" * 50)
    
    return {
        'total': total_amount,
        'pending_count': len(pending),
        'pending_amount': pending['amount'].sum(),
        'invoiced_count': len(invoiced),
        'invoiced_amount': invoiced['amount'].sum(),
        'reimbursed_count': len(reimbursed),
        'reimbursed_amount': reimbursed['amount'].sum(),
    }


if __name__ == "__main__":
    print("差旅报销 - 垫款标记模块")
    print("=" * 40)
    print(f"\n大额阈值: ¥{LARGE_AMOUNT_THRESHOLD}")
    print("\n使用方法:")
    print("  from mark_expenses import mark_interactive, auto_mark_by_threshold")
    print("  df = mark_interactive(df)  # 交互式标记")
    print("  df = auto_mark_by_threshold(df)  # 自动按阈值标记")
