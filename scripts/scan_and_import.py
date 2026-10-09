#!/usr/bin/env python3
"""扫描G:\股票中的PDF/DOCX/TXT文件并生成Obsidian索引"""
import os, hashlib, json
from datetime import datetime

STOCK_DIR = r"G:\股票"
OBSIDIAN_RAW = r"F:\政治+经济+股市知识思维框架知识库\raw\股票"
INDEX_FILE = r"F:\政治+经济+股市知识思维框架知识库\股票\文件清单.md"

EXT_MAP = {
    '.pdf': 'PDF研究报告',
    '.docx': 'Word文档',
    '.doc': 'Word文档',
    '.pptx': 'PPT演示',
    '.txt': '文本资料',
}

def scan():
    if not os.path.exists(STOCK_DIR):
        print("[WARN] G:\股票 不可用，跳过扫描")
        return []
    
    results = []
    for root, dirs, files in os.walk(STOCK_DIR):
        rel_dir = os.path.relpath(root, STOCK_DIR)
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in EXT_MAP:
                full = os.path.join(root, f)
                size = os.path.getsize(full)
                results.append({
                    'file': f,
                    'path': full,
                    'relpath': os.path.join(rel_dir, f),
                    'size_kb': round(size/1024, 1),
                    'type': EXT_MAP[ext],
                    'ext': ext,
                })
    return results

def generate_index(files):
    lines = [
        "---",
        "title: \"G:\\股票 文件清单\"",
        f"date: {datetime.now().strftime('%Y-%m-%d')}",
        "tags: [股票, 文件清单, G盘]",
        "---",
        "",
        f"# 📂 G:\\股票 文件清单 ({len(files)} 个可识别文件)",
        "",
        "> 此清单由 bamboo-stock skill 自动生成",
        "",
    ]
    
    # Group by type
    by_type = {}
    for f in files:
        by_type.setdefault(f['type'], []).append(f)
    
    for t, items in sorted(by_type.items()):
        lines.append(f"\n## {t} ({len(items)}个)\n")
        lines.append("| 文件名 | 路径 | 大小 |")
        lines.append("|--------|------|------|")
        for item in sorted(items, key=lambda x: x['file']):
            lines.append(f"| {item['file']} | `{item['relpath']}` | {item['size_kb']}KB |")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    files = scan()
    index = generate_index(files)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index)
    print(f"[OK] 共识别 {len(files)} 个可读文件")
    print(f"[OK] 索引已写入 {INDEX_FILE}")
