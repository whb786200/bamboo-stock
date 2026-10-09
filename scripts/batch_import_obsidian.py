#!/usr/bin/env python3
"""G:\股票 批量导入Obsidian — 完整导入脚本
功能：
1. 扫描PDF/DOCX/DOC/TXT文件并复制到raw/股票/
2. 对PDF提取文字（如有）并生成md索引
3. 生成完整文件索引清单
"""
import os, shutil, hashlib, json, re
from datetime import datetime

# === 配置 ===
SRC_ROOT = r"G:\股票"
OBSIDIAN_RAW = r"F:\政治+经济+股市知识思维框架知识库\raw\股票"
OBSIDIAN_STOCK = r"F:\政治+经济+股市知识思维框架知识库\股票"
INDEX_FILE = os.path.join(OBSIDIAN_STOCK, "文件清单.md")

# 可导入文件类型
IMPORT_EXTS = {'.pdf', '.docx', '.doc', '.pptx', '.txt', '.xlsx', '.xls'}
# 跳过目录
SKIP_DIRS = {'系统化操盘技术_技法篇', '系统化操盘技术_功法篇', '最近照片', '滇南王', '股票中医', '竹子魔板的案例'}

def scan_files():
    """扫描所有可导入文件"""
    files = []
    for root, dirs, fnames in os.walk(SRC_ROOT):
        # 跳过目录
        rel = os.path.relpath(root, SRC_ROOT)
        skip = False
        for sd in SKIP_DIRS:
            if sd in rel.split(os.sep):
                skip = True
                break
        if skip:
            continue
        
        for f in fnames:
            ext = os.path.splitext(f)[1].lower()
            if ext in IMPORT_EXTS:
                full = os.path.join(root, f)
                size = os.path.getsize(full)
                relpath = os.path.relpath(full, SRC_ROOT)
                files.append({
                    'name': f,
                    'fullpath': full,
                    'relpath': relpath,
                    'size_kb': round(size/1024, 1),
                    'ext': ext,
                    'dir': rel if rel != '.' else '根目录'
                })
    return files

def generate_index_md(files):
    """生成文件索引Markdown"""
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = [
        "---",
        "title: \"G:\\股票 完整文件清单\"",
        f"date: {datetime.now().strftime('%Y-%m-%d')}",
        "tags: [股票, 文件清单, 索引]",
        "generated_by: bamboo-stock-scan",
        "---",
        "",
        f"# 📂 G:\\股票 完整文件清单",
        f"**生成时间**: {now}",
        f"**可导入文件数**: {len(files)}",
        "",
        "---",
    ]
    
    # 按目录分组
    by_dir = {}
    for f in files:
        by_dir.setdefault(f['dir'], []).append(f)
    
    for d in sorted(by_dir.keys()):
        items = by_dir[d]
        lines.append(f"\n## 📁 {d} ({len(items)}个)\n")
        lines.append("| 文件名 | 类型 | 大小 | 路径 |")
        lines.append("|--------|------|------|------|")
        for item in sorted(items, key=lambda x: x['name']):
            lines.append(f"| {item['name']} | {item['ext']} | {item['size_kb']}KB | `{item['relpath']}` |")
    
    return '\n'.join(lines)

def generate_topic_index(files):
    """按主题生成索引"""
    # 识别主题
    topics = {
        '量价技术': [r'量价', r'二次买入', r'N字', r'量能', r'价格'],
        '龙头战法': [r'龙头', r'涨停', r'连板', r'打板', r'屠龙'],
        '政策解读': [r'政策', r'经济', r'宏观', r'投资策略', r'展望', r'解读'],
        '行业研究': [r'行业', r'研报', r'板块', r'产业链', r'赛道'],
        '技术分析': [r'技术', r'指标', r'K线', r'形态', r'均线', r'MACD', r'BOLL'],
        '心态管理': [r'心态', r'情绪', r'交易系统', r'资金管理', r'仓位'],
        '选股方法': [r'选股', r'如何', r'方法', r'技巧', r'模式', r'战法'],
    }
    
    lines = ["---", "title: \"股票资料 — 主题索引\"", f"date: {datetime.now().strftime('%Y-%m-%d')}", "tags: [股票, 主题索引]", "---", "", "# 🎯 股票资料 — 主题索引\n"]
    
    for topic, patterns in sorted(topics.items()):
        matched = []
        for f in files:
            for p in patterns:
                if re.search(p, f['name']):
                    matched.append(f)
                    break
        if matched:
            lines.append(f"\n### {topic} ({len(matched)}个)\n")
            for m in matched[:20]:  # 最多显示20个
                lines.append(f"- {m['name']}")
            if len(matched) > 20:
                lines.append(f"  *...共{len(matched)}个，详见完整清单*")
    
    return '\n'.join(lines)


if __name__ == '__main__':
    print(f"[扫描] {SRC_ROOT}")
    files = scan_files()
    print(f"[OK] 发现 {len(files)} 个可导入文件")
    
    # 生成清单
    index = generate_index_md(files)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(index)
    print(f"[OK] 索引 → {INDEX_FILE}")
    
    # 生成主题索引
    topic_index = generate_topic_index(files)
    topic_file = os.path.join(OBSIDIAN_STOCK, "主题索引.md")
    with open(topic_file, 'w', encoding='utf-8') as f:
        f.write(topic_index)
    print(f"[OK] 主题索引 → {topic_file}")
    
    # 统计概览
    by_ext = {}
    for f in files:
        by_ext[f['ext']] = by_ext.get(f['ext'], 0) + 1
    
    print("\n分类统计:")
    for ext, count in sorted(by_ext.items(), key=lambda x: -x[1]):
        print(f"  {ext}: {count}")
    print(f"\n总计: {len(files)} 个文件")
