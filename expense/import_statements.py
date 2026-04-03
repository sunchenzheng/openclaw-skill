# -*- coding: utf-8 -*-
"""
消费流水导入模块
支持：微信支付账单、支付宝账单、招商银行信用卡账单
"""

import pandas as pd
import os
from datetime import datetime
from pathlib import Path
from config import STATEMENTS_DIR, LARGE_AMOUNT_THRESHOLD, PAYMENT_SOURCES


class StatementImporter:
    """流水导入基类"""

    def __init__(self, file_path):
        self.file_path = Path(file_path)
        self.df = None

    def detect_encoding(self):
        """检测文件编码"""
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        for enc in encodings:
            try:
                with open(self.file_path, 'r', encoding=enc) as f:
                    f.read(1024)
                return enc
            except:
                continue
        return 'utf-8'

    def import_csv(self):
        """读取CSV文件"""
        enc = self.detect_encoding()
        self.df = pd.read_csv(self.file_path, encoding=enc)
        print(f"  读取到 {len(self.df)} 条记录")
        return self.df


class WeChatImporter(StatementImporter):
    """微信支付账单导入"""

    def parse(self):
        """解析微信账单格式"""
        self.import_csv()
        
        # 微信账单列名映射
        column_mapping = {
            '交易时间': 'date',
            '交易对方': 'merchant',
            '商品': 'product',
            '支付方式': 'payment_method',
            '金额(元)': 'amount',
            '当前状态': 'status',
            '交易类型': 'type',
            '备注': 'remark',
        }

        # 尝试匹配列名
        actual_columns = {}
        for col in self.df.columns:
            for key in column_mapping:
                if key in col:
                    actual_columns[col] = column_mapping[key]

        self.df = self.df.rename(columns=actual_columns)
        
        # 处理金额（去掉¥符号）
        if 'amount' in self.df.columns:
            self.df['amount'] = self.df['amount'].astype(str).str.replace('¥', '').str.replace(',', '').astype(float)
        
        # 标准化
        self.df['source'] = 'wechat'
        self.df['is_company_expense'] = self.df['amount'].apply(
            lambda x: '是' if x > LARGE_AMOUNT_THRESHOLD else '否'
        )
        self.df['reimburse_status'] = 'pending'
        self.df['invoice_id'] = ''
        
        print(f"  微信账单解析完成：{len(self.df)} 条")
        return self.df


class AlipayImporter(StatementImporter):
    """支付宝账单导入"""

    def parse(self):
        """解析支付宝账单格式"""
        self.import_csv()
        
        # 支付宝列名映射
        column_mapping = {
            '交易时间': 'date',
            '交易对方': 'merchant',
            '商品说明': 'product',
            '金额': 'amount',
            '状态': 'status',
            '交易类型': 'type',
            '备注': 'remark',
        }

        actual_columns = {}
        for col in self.df.columns:
            for key in column_mapping:
                if key in col:
                    actual_columns[col] = column_mapping[key]

        self.df = self.df.rename(columns=actual_columns)
        
        # 处理金额
        if 'amount' in self.df.columns:
            self.df['amount'] = self.df['amount'].astype(str).str.replace(',', '').astype(float)
        
        self.df['source'] = 'alipay'
        self.df['is_company_expense'] = self.df['amount'].apply(
            lambda x: '是' if x > LARGE_AMOUNT_THRESHOLD else '否'
        )
        self.df['reimburse_status'] = 'pending'
        self.df['invoice_id'] = ''
        
        print(f"  支付宝账单解析完成：{len(self.df)} 条")
        return self.df


class CMBImporter(StatementImporter):
    """招商银行信用卡账单导入"""

    def parse(self):
        """解析招行账单格式"""
        self.import_csv()
        
        # 招行账单列名映射
        column_mapping = {
            '交易日期': 'date',
            '交易描述': 'merchant',
            '卡号后四位': 'card_last4',
            '交易金额': 'amount',
            '账单金额': 'bill_amount',
            '交易类型': 'type',
        }

        actual_columns = {}
        for col in self.df.columns:
            for key in column_mapping:
                if key in col:
                    actual_columns[col] = column_mapping[key]

        self.df = self.df.rename(columns=actual_columns)
        
        # 处理金额
        if 'amount' in self.df.columns:
            self.df['amount'] = self.df['amount'].astype(str).str.replace(',', '').astype(float)
        
        # 判断是否商务卡8651
        if 'card_last4' in self.df.columns:
            self.df['source'] = self.df['card_last4'].apply(
                lambda x: 'cmb' if str(x).endswith('8651') else 'cmb_other'
            )
        else:
            self.df['source'] = 'cmb'
            
        self.df['is_company_expense'] = self.df['amount'].apply(
            lambda x: '是' if x > LARGE_AMOUNT_THRESHOLD else '否'
        )
        self.df['reimburse_status'] = 'pending'
        self.df['invoice_id'] = ''
        
        print(f"  招行账单解析完成：{len(self.df)} 条")
        return self.df


def import_statement(source, file_path):
    """
    统一导入入口
    
    Args:
        source: 'wechat' | 'alipay' | 'cmb'
        file_path: CSV文件路径
    
    Returns:
        DataFrame: 标准化的流水数据
    """
    print(f"\n📥 开始导入 {PAYMENT_SOURCES.get(source, source)} 账单...")
    print(f"   文件: {file_path}")
    
    if source == 'wechat':
        importer = WeChatImporter(file_path)
    elif source == 'alipay':
        importer = AlipayImporter(file_path)
    elif source == 'cmb':
        importer = CMBImporter(file_path)
    else:
        raise ValueError(f"不支持的来源: {source}")
    
    return importer.parse()


if __name__ == "__main__":
    # 测试
    print("差旅报销 - 流水导入模块")
    print("=" * 40)
    
    # 列出statements目录下的csv文件
    if STATEMENTS_DIR.exists():
        csv_files = list(STATEMENTS_DIR.glob("*.csv"))
        if csv_files:
            print(f"\n找到 {len(csv_files)} 个CSV文件:")
            for f in csv_files:
                print(f"  - {f.name}")
        else:
            print("\n📂 statements目录暂无CSV文件")
            print(f"   请将银行流水CSV放入: {STATEMENTS_DIR}")
    else:
        print(f"\n📂 请创建目录: {STATEMENTS_DIR}")
