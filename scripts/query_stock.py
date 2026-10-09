#!/usr/bin/env python3
"""bamboo-stock westock-data 集成脚本
功能：一键调用westock-data查询行情并叠加三层分析
"""
import json, subprocess, sys
from datetime import datetime

def query_westock(cmd_args):
    """调用 westock-data"""
    full_cmd = f'npx --yes westock-data-skillhub@latest {cmd_args}'
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, shell=True, timeout=30)
        return result.stdout
    except Exception as e:
        return f"[ERROR] {e}"

def query_to_analysis(code, name=""):
    """从股票代码查询到三层分析"""
    print(f"\n🔍 查询: {name or code}")
    
    # 查行情
    raw = query_westock(f"kline {code} day 10")
    print(f"[行情] {raw[:200]}...")
    
    # 查资金
    fund = query_westock(f"asfund {code}") if code[:2] in ('sh','sz') else ""
    if fund:
        print(f"[资金流向] {fund[:200]}...")
    
    # 查技术指标
    tech = query_westock(f"technical {code} macd") if code[:2] in ('sh','sz','bj') else ""
    if tech:
        print(f"[技术指标MACD] {tech[:200]}...")
    
    # 查财报
    finance = query_westock(f"finance {code} 2")
    if finance:
        print(f"[财报] {finance[:200]}...")
    
    return {
        'code': code,
        'name': name,
        'raw': raw,
        'fund': fund,
        'tech': tech,
        'finance': finance
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python query_stock.py <股票代码> [股票名称]")
        print("示例: python query_stock.py sh600519 贵州茅台")
        sys.exit(1)
    
    code = sys.argv[1]
    name = sys.argv[2] if len(sys.argv) > 2 else ""
    result = query_to_analysis(code, name)
    print(f"\n✅ {name or code} 数据获取完成")
