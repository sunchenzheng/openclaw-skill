# -*- coding: utf-8 -*-
"""
差旅报销配置
"""

import os
from pathlib import Path

# ============ 用户配置 ============

# 数据存放根目录（根据你的实际情况修改）
DATA_ROOT = Path(r"C:\Users\123\openclaw_data\expense")

# 数电发票存放目录
INVOICE_DIR = DATA_ROOT / "invoices"

# 银行流水CSV存放目录
STATEMENTS_DIR = DATA_ROOT / "statements"

# 输出报表目录
OUTPUT_DIR = DATA_ROOT / "output"

# ============ 系统配置 ============

# 大额垫款阈值（元），超过此金额自动标记为可能的公司垫款
LARGE_AMOUNT_THRESHOLD = 500

# 发票与流水匹配：日期容差（天）
DATE_TOLERANCE_DAYS = 3

# 支持的支付渠道
PAYMENT_SOURCES = {
    "wechat": "微信支付",
    "alipay": "支付宝",
    "cmb": "招商银行8651商务卡",
    "cmb2690": "招商银行2690借记卡",
    "cib": "兴业银行信用卡",
}

# 报销状态
EXPENSE_STATUS = {
    "pending": "未提交",
    "invoiced": "已开发票",
    "reimbursed": "已报销",
}

# ============ 初始化目录 ============

def ensure_dirs():
    """确保所有必要目录存在"""
    for d in [INVOICE_DIR, STATEMENTS_DIR, OUTPUT_DIR]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"📁 目录已确认: {d}")

if __name__ == "__main__":
    ensure_dirs()
