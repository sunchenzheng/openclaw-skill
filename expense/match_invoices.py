# -*- coding: utf-8 -*-
"""
数电发票匹配模块
解析XML发票文件，按金额+日期+商户名匹配消费流水
"""

import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
from config import INVOICE_DIR, DATE_TOLERANCE_DAYS


class Invoice:
    """发票对象"""
    
    def __init__(self, invoice_id, amount, date, seller_name, buyer_name, file_path):
        self.invoice_id = invoice_id          # 发票号码
        self.amount = amount                   # 金额（含税）
        self.date = date                        # 开票日期
        self.seller_name = seller_name          # 销售方名称
        self.buyer_name = buyer_name            # 购买方名称
        self.file_path = file_path              # 原始文件路径
        self.matched_statement = None           # 匹配的流水记录
        self.match_confidence = 0               # 匹配置信度 0-100

    def __repr__(self):
        return f"Invoice({self.invoice_id}, ¥{self.amount}, {self.date})"


class InvoiceParser:
    """发票解析基类"""
    
    def parse(self, file_path):
        raise NotImplementedError


class XMLInvoiceParser(InvoiceParser):
    """XML格式数电发票解析"""
    
    def parse(self, file_path):
        """解析龙版XML发票格式"""
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            # 命名空间
            ns = {'ns': 'http://www.chinatax.gov.cn/2018/lingshui'}
            
            # 提取字段（根据实际XML结构调整）
            invoice_id = self._find_element(root, ['fphm', 'invoice_number', 'invoiceId'])
            amount_str = self._find_element(root, ['je', 'amount', 'totalAmount'])
            date_str = self._find_element(root, ['kprq', 'invoice_date', 'billingDate'])
            seller_name = self._find_element(root, ['xfmc', 'seller_name', 'sellerName'])
            buyer_name = self._find_element(root, ['gfmc', 'buyer_name', 'buyerName'])
            
            # 解析金额
            amount = float(amount_str) if amount_str else 0.0
            
            # 解析日期
            date = self._parse_date(date_str)
            
            return Invoice(
                invoice_id=invoice_id or Path(file_path).stem,
                amount=amount,
                date=date,
                seller_name=seller_name or '',
                buyer_name=buyer_name or '',
                file_path=str(file_path)
            )
        except Exception as e:
            print(f"  ⚠️ 解析失败 {file_path.name}: {e}")
            return None
    
    def _find_element(self, root, keys):
        """查找元素"""
        for key in keys:
            elem = root.find(f".//{key}")
            if elem is not None and elem.text:
                return elem.text.strip()
        return None
    
    def _parse_date(self, date_str):
        """解析日期"""
        if not date_str:
            return None
        # 尝试多种格式
        for fmt in ['%Y-%m-%d', '%Y%m%d', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_str[:10], fmt)
            except:
                continue
        return None


class PDFInvoiceParser(InvoiceParser):
    """PDF格式数电发票解析（简化版）"""
    
    def parse(self, file_path):
        """从PDF文件名提取关键信息"""
        # PDF难以直接解析，使用文件名约定
        # 文件命名格式：发票号码_金额_日期.pdf
        name = Path(file_path).stem
        parts = name.split('_')
        
        if len(parts) >= 3:
            invoice_id = parts[0]
            try:
                amount = float(parts[1])
                date = self._parse_date(parts[2])
            except:
                amount = 0.0
                date = None
        else:
            invoice_id = name
            amount = 0.0
            date = None
        
        return Invoice(
            invoice_id=invoice_id,
            amount=amount,
            date=date,
            seller_name='',
            buyer_name='',
            file_path=str(file_path)
        )
    
    def _parse_date(self, date_str):
        for fmt in ['%Y-%m-%d', '%Y%m%d', '%Y/%m/%d']:
            try:
                return datetime.strptime(date_str[:10], fmt)
            except:
                continue
        return None


def scan_invoices(invoice_dir=None):
    """
    扫描发票目录，返回发票列表
    
    Args:
        invoice_dir: 发票目录路径，默认使用配置中的INVOICE_DIR
    
    Returns:
        list[Invoice]: 发票对象列表
    """
    if invoice_dir is None:
        invoice_dir = INVOICE_DIR
    
    invoice_dir = Path(invoice_dir)
    invoices = []
    
    # XML文件
    xml_files = list(invoice_dir.glob("*.xml"))
    for f in xml_files:
        parser = XMLInvoiceParser()
        inv = parser.parse(f)
        if inv:
            invoices.append(inv)
    
    # PDF文件
    pdf_files = list(invoice_dir.glob("*.pdf"))
    for f in pdf_files:
        parser = PDFInvoiceParser()
        inv = parser.parse(f)
        if inv:
            invoices.append(inv)
    
    print(f"\n📋 发票扫描完成：共 {len(invoices)} 张")
    for inv in invoices[:5]:
        print(f"   {inv.invoice_id} | ¥{inv.amount} | {inv.date} | {inv.seller_name}")
    if len(invoices) > 5:
        print(f"   ... 还有 {len(invoices) - 5} 张")
    
    return invoices


def normalize_merchant_name(name):
    """
    标准化商户名称，去除地区前缀等干扰词
    例如："上海星巴克咖啡有限公司" -> "星巴克咖啡"
    """
    if not name:
        return ""
    
    # 去除常见前缀
    prefixes = ['上海', '北京', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆']
    for p in prefixes:
        if name.startswith(p):
            name = name[len(p):]
    
    # 去除常见后缀
    suffixes = ['有限公司', '有限责任公司', '股份有限公司', 'Co.,Ltd', 'LTD']
    for s in suffixes:
        if name.endswith(s):
            name = name[:-len(s)]
    
    return name.strip()


def match_invoices_with_statements(invoices, statements_df):
    """
    发票与流水匹配
    
    匹配规则：
    1. 金额完全一致（精确到分）
    2. 日期在±DATE_TOLERANCE_DAYS天内
    3. 商户名称相似（包含关系）
    
    Args:
        invoices: Invoice列表
        statements_df: 流水DataFrame
    
    Returns:
        tuple: (匹配结果列表, 未匹配的发票列表, 未匹配的流水列表)
    """
    print(f"\n🔍 开始匹配发票与流水...")
    print(f"   发票数: {len(invoices)}, 流水数: {len(statements_df)}")
    
    matches = []
    unmatched_invoices = []
    unmatched_statements = []
    
    # 转换为列表方便处理
    statements = statements_df.to_dict('records')
    used_statements = set()
    used_invoices = set()
    
    # 按金额分组匹配
    amount_groups = {}
    for i, inv in enumerate(invoices):
        if inv.amount not in amount_groups:
            amount_groups[inv.amount] = []
        amount_groups[inv.amount].append(i)
    
    # 第一轮：金额+日期精确匹配
    for i, inv in enumerate(invoices):
        if i in used_invoices:
            continue
            
        for j, stmt in enumerate(statements):
            if j in used_statements:
                continue
            
            # 金额一致
            if abs(inv.amount - stmt.get('amount', 0)) < 0.01:
                # 日期在容差范围内
                if inv.date and stmt.get('date'):
                    date_diff = abs((inv.date - stmt['date']).days)
                    if date_diff <= DATE_TOLERANCE_DAYS:
                        # 商户名相似
                        inv_name = normalize_merchant_name(inv.seller_name)
                        stmt_name = normalize_merchant_name(stmt.get('merchant', ''))
                        
                        if inv_name and stmt_name:
                            if inv_name in stmt_name or stmt_name in inv_name:
                                matches.append({
                                    'invoice': inv,
                                    'statement': stmt,
                                    'confidence': 95,
                                    'match_type': 'high'
                                })
                                used_invoices.add(i)
                                used_statements.add(j)
                                break
    
    # 第二轮：金额匹配，降低置信度
    for i, inv in enumerate(invoices):
        if i in used_invoices:
            continue
            
        for j, stmt in enumerate(statements):
            if j in used_statements:
                continue
            
            if abs(inv.amount - stmt.get('amount', 0)) < 0.01:
                date_diff = 999
                if inv.date and stmt.get('date'):
                    date_diff = abs((inv.date - stmt['date']).days)
                
                if date_diff <= DATE_TOLERANCE_DAYS * 2:
                    matches.append({
                        'invoice': inv,
                        'statement': stmt,
                        'confidence': 70 if date_diff <= DATE_TOLERANCE_DAYS else 50,
                        'match_type': 'medium'
                    })
                    used_invoices.add(i)
                    used_statements.add(j)
                    break
    
    # 收集未匹配的
    for i, inv in enumerate(invoices):
        if i not in used_invoices:
            unmatched_invoices.append(inv)
    
    for j, stmt in enumerate(statements):
        if j not in used_statements:
            unmatched_statements.append(stmt)
    
    print(f"\n✅ 匹配完成:")
    print(f"   高置信匹配: {len([m for m in matches if m['confidence'] >= 80])} 条")
    print(f"   中置信匹配: {len([m for m in matches if m['confidence'] < 80])} 条")
    print(f"   未匹配发票: {len(unmatched_invoices)} 张")
    print(f"   未匹配流水: {len(unmatched_statements)} 条")
    
    return matches, unmatched_invoices, unmatched_statements


if __name__ == "__main__":
    print("差旅报销 - 发票匹配模块")
    print("=" * 40)
    
    invoices = scan_invoices()
    
    if not invoices:
        print(f"\n📂 发票目录为空: {INVOICE_DIR}")
        print("   请将数电发票(XML/PDF)放入此目录")
