"""
G:\股票 → F:\政治+经济+股市知识思维框架知识库\raw\股票\
批量导入脚本 v2.0（无复制模式：仅生成 Obsidian Markdown 索引条目）

策略：G盘 116GB 文件不再复制，直接在 Obsidian 生成 markdown 条目
（每个子目录生成一个索引 .md 条目，YAML frontmatter 指向 G:\ 原文件路径）
"""
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# 修复 Windows 控制台 Unicode 输出
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# === 路径配置 ===
SRC_ROOT = Path(r"G:\股票")
DST_RAW = Path(r"F:\政治+经济+股市知识思维框架知识库\raw\股票")
DST_ROOT = Path(r"F:\政治+经济+股市知识思维框架知识库\股票")

# === 分类配置 ===
CATEGORIES = {
    "精品资料": {
        "desc": "核心付费股票资料合集（PDF为主）",
        "tags": ["精品", "资料", "PDF", "股票学习"],
        "color": "red",
        "extensions": [".pdf", ".docx", ".doc", ".pptx", ".txt", ".md"]
    },
    "二次买入法": {
        "desc": "二次买入法系统教程（70节）",
        "tags": ["二次买入法", "买点", "买入策略", "系统教程"],
        "color": "blue",
        "extensions": [".pdf", ".docx", ".mp4", ".avi", ".mkv", ".txt"]
    },
    "系统化操盘技术_技法篇": {
        "desc": "系统化操盘技术-技法篇（K线/量价/形态）",
        "tags": ["系统化操盘", "技法", "K线", "量价", "形态"],
        "color": "green",
        "extensions": [".pdf", ".docx", ".mp4", ".rmvb", ".avi", ".mkv"]
    },
    "系统化操盘技术_功法篇": {
        "desc": "系统化操盘技术-功法篇（内功/心法）",
        "tags": ["系统化操盘", "功法", "心法", "内功"],
        "color": "green",
        "extensions": [".pdf", ".docx", ".mp4", ".rmvb", ".avi", ".mkv"]
    },
    "股市廖聊吧有声书": {
        "desc": "股市廖聊吧有声读物（视频课程）",
        "tags": ["有声书", "视频课程", "廖聊吧"],
        "color": "purple",
        "extensions": [".mp3", ".m4a", ".wav", ".pdf", ".docx", ".mp4", ".vob"]
    },
    "牛散训练营第一期": {
        "desc": "牛散训练营第一期课程（廖英强讲座）",
        "tags": ["牛散训练营", "课程", "第一期", "廖英强"],
        "color": "orange",
        "extensions": [".flv", ".vob", ".rar", ".ifo", ".bup", ".pdf", ".docx", ".mp4", ".avi"]
    },
    "牛散训练营第二期": {
        "desc": "牛散训练营第二期课程（廖英强讲座）",
        "tags": ["牛散训练营", "课程", "第二期", "廖英强"],
        "color": "orange",
        "extensions": [".mp3", ".mp4", ".flv", ".pdf", ".docx", ".avi"]
    },
    "牛散训练营第三期": {
        "desc": "牛散训练营第三期课程（廖英强讲座）",
        "tags": ["牛散训练营", "课程", "第三期", "廖英强"],
        "color": "orange",
        "extensions": [".pdf", ".flv", ".wav", ".rar", ".mp4", ".docx"]
    },
    "谈股论金-唐英强": {
        "desc": "谈股论金唐英强老师资料",
        "tags": ["唐英强", "谈股论金", "课程"],
        "color": "teal",
        "extensions": [".pdf", ".docx", ".mp4", ".txt"]
    },
    "股票中医": {
        "desc": "股票中医理论（估值/基本面/长期持有）",
        "tags": ["股票中医", "基本面", "估值", "价值投资"],
        "color": "cyan",
        "extensions": [".pdf", ".docx", ".txt", ".md", ".mp4", ".jpg", ".jpeg", ".png", ".gif"]
    },
    "滇南王": {
        "desc": "滇南王股票体系（含大量实操案例图）",
        "tags": ["滇南王", "实操案例", "案例图", "K线图"],
        "color": "pink",
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx"]
    },
    "竹子魔板的案例": {
        "desc": "竹子魔板实战案例图/分时图/上市公司分析图",
        "tags": ["竹子魔板", "案例图", "实战", "分时图", "K线"],
        "color": "lime",
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".pdf", ".docx"]
    },
    "万点来了": {
        "desc": "万点来了系列资料",
        "tags": ["万点来了", "大盘", "牛市"],
        "color": "gold",
        "extensions": [".pdf", ".docx", ".pptx", ".txt", ".mp4", ".zip"]
    },
    "股票学习": {
        "desc": "通用股票学习资料",
        "tags": ["股票学习", "入门", "基础"],
        "color": "gray",
        "extensions": [".pdf", ".docx", ".txt", ".md"]
    },
    "股市的道": {
        "desc": "股市的道（竹子魔板精简版等）",
        "tags": ["股市的道", "竹子", "心法"],
        "color": "indigo",
        "extensions": [".pdf", ".pptx", ".docx", ".md"]
    },
    "实操案例": {
        "desc": "实盘操作案例分享",
        "tags": ["实操案例", "实盘", "分享"],
        "color": "brown",
        "extensions": [".pdf", ".docx", ".jpg", ".png", ".txt"]
    },
    "最近照片": {
        "desc": "最近照片（与股票无关，不导入）",
        "tags": ["照片", "图片"],
        "color": "slate",
        "extensions": [".jpg", ".jpeg", ".png", ".gif", ".mp4", ".avi"],
        "skip": True
    }
}


def get_file_category(filename):
    """根据扩展名判断文件类型"""
    ext = Path(filename).suffix.lower()
    type_map = {
        ".pdf": "📄 PDF",
        ".docx": "📝 Word",
        ".doc": "📝 Word",
        ".pptx": "📊 PPT",
        ".ppt": "📊 PPT",
        ".txt": "📃 文本",
        ".md": "📋 Markdown",
        ".mp4": "🎬 视频",
        ".avi": "🎬 视频",
        ".mkv": "🎬 视频",
        ".mp3": "🎵 音频",
        ".m4a": "🎵 音频",
        ".wav": "🎵 音频",
        ".jpg": "🖼️ 图片",
        ".jpeg": "🖼️ 图片",
        ".png": "🖼️ 图片",
        ".gif": "🖼️ GIF",
        ".xlsx": "📈 Excel",
        ".xls": "📈 Excel",
    }
    return type_map.get(ext, "📁 文件")


def clean_filename(name):
    """清理文件名（移除非法字符）"""
    return re.sub(r'[<>:"/\\|?*\[\]]', '_', name)


def make_obsidian_entry(src_path, category_info, subdir=""):
    """生成单个文件的 Obsidian Markdown 条目"""
    p = Path(src_path)
    fname = p.name
    stem = p.stem
    ext = p.suffix.lower()
    size_mb = round(p.stat().st_size / 1024 / 1024, 1) if p.exists() else 0

    # frontmatter
    icon = get_file_category(fname)
    tags = category_info.get("tags", [])
    tags_str = "\n  - ".join(tags) if tags else ""
    now = datetime.now().strftime("%Y-%m-%d")

    md = f"""---
title: "{stem}"
type: stock-file
category: "{subdir if subdir else '精品资料'}"
file-type: "{ext.lstrip('.')}"
original-path: "{src_path}"
size-mb: {size_mb}
tags:
  - {tags_str}
created: {now}
source: G:\\股票
framework: [[竹子·冰山·政事堂_股市综合框架]]
---

# {stem}

{icon} **类型**：`{ext.lstrip(".").upper()}` | 📦 **{size_mb} MB**

**原始路径**：`{src_path}`

> 📌 本文件为 G:\\股票 资料库条目，原始文件保留在 G 盘。
> 相关框架：[[竹子·冰山·政事堂_股市综合框架]]

"""
    return md


def scan_directory(src_dir, category_key, category_info):
    """扫描目录，生成条目列表"""
    entries = []
    allowed_exts = category_info.get("extensions", [])
    skip = category_info.get("skip", False)

    if skip:
        return entries

    try:
        for p in sorted(Path(src_dir).rglob("*")):
            if p.is_file():
                ext = p.suffix.lower()
                if ext in allowed_exts or not allowed_exts:
                    entries.append(str(p))
    except Exception as e:
        print(f"  ⚠️ 扫描失败 {src_dir}: {e}")

    return entries


def build_category_index(category_key, category_info, files):
    """构建某个分类的索引 Markdown"""
    tag_color = category_info.get("color", "gray")
    desc = category_info.get("desc", "")
    tags = category_info.get("tags", [])

    lines = [
        "---",
        f"title: \"📁 {category_key}\"",
        f"type: category-index",
        f"category: \"{category_key}\"",
        f'tags: [{", ".join(tags)}]',
        f"created: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
        "",
        f"# 📁 {category_key}",
        "",
        f"> {desc}",
        "",
        f"**文件数量**：{len(files)} 个",
        f"**来源**：G:\\股票\\{category_key}",
        "",
        "## 文件列表",
        ""
    ]

    # 按类型分组
    type_groups = {}
    for f in files:
        ext = Path(f).suffix.lower()
        icon = get_file_category(f)
        if ext not in type_groups:
            type_groups[ext] = []
        type_groups[ext].append(f)

    for ext, flist in sorted(type_groups.items()):
        ext_upper = ext.lstrip('.').upper()
        lines.append(f"### {get_file_category(flist[0])} {ext_upper} 文件（{len(flist)}个）")
        for i, f in enumerate(flist, 1):
            fname = Path(f).name
            size_mb = round(Path(f).stat().st_size / 1024 / 1024, 1)
            rel = f.replace(str(SRC_ROOT), "G:\\股票").replace("\\", "/")
            lines.append(f"{i}. [{fname}](file:///{f.replace(chr(92), '/')}) *({size_mb} MB)*")
        lines.append("")

    # 关联框架
    lines.extend([
        "---",
        "",
        "## 相关框架",
        "",
        "- [[竹子·冰山·政事堂_股市综合框架]]",
        "- [[竹子魔板35条（应用篇）]]",
        ""
    ])

    return "\n".join(lines)


def main():
    print(f"📂 源目录: {SRC_ROOT}")
    print(f"📂 目标目录: {DST_RAW}")
    print()

    # 确保目录存在
    DST_RAW.mkdir(parents=True, exist_ok=True)
    DST_ROOT.mkdir(parents=True, exist_ok=True)

    all_files = {}  # category_key -> [file_paths]

    for cat_key, cat_info in CATEGORIES.items():
        src_path = SRC_ROOT / cat_key
        if not src_path.exists():
            print(f"⏭️  跳过（不存在）: {src_path}")
            continue
        if cat_info.get("skip"):
            print(f"⏭️  跳过（标记skip）: {cat_key}")
            continue

        print(f"🔍 扫描: {cat_key}...")
        files = scan_directory(str(src_path), cat_key, cat_info)
        all_files[cat_key] = files
        print(f"   → 找到 {len(files)} 个文件")

        # 写分类索引
        if files:
            idx_path = DST_ROOT / f"{cat_key}.md"
            idx_content = build_category_index(cat_key, cat_info, files)
            idx_path.write_text(idx_content, encoding="utf-8")
            print(f"   ✅ 写入索引: {idx_path.name}")

            # 写 individual 条目（仅PDF/DOCX/MP4，写图片/音视频/压缩包/音频不写条目）
            writable_exts = {".pdf", ".docx", ".doc", ".txt", ".md", ".pptx", ".xlsx", ".xls", ".mp4", ".flv", ".rar"}
            for f in files:
                ext = Path(f).suffix.lower()
                if ext not in writable_exts:
                    continue
                fname_clean = clean_filename(Path(f).stem)
                out_path = DST_RAW / f"{fname_clean}.md"
                if out_path.exists():
                    continue
                entry = make_obsidian_entry(f, cat_info, cat_key)
                try:
                    out_path.write_text(entry, encoding="utf-8")
                except Exception as e:
                    print(f"   ⚠️ 写入失败: {f} → {e}")

    # 生成总索引
    print()
    print("📋 生成总索引...")

    total_files = sum(len(v) for v in all_files.values())

    index_lines = [
        "---",
        'title: "📈 股票资料库 索引"',
        "type: stock-index",
        'tags: ["股票", "资料库", "索引", "G盘"]',
        f"created: {datetime.now().strftime('%Y-%m-%d')}",
        "framework: [[竹子·冰山·政事堂_股市综合框架]]",
        "---",
        "",
        "# 📈 股票资料库",
        "",
        f"> **来源**：G:\\股票（{SRC_ROOT.stat().st_size / 1024**3:.1f} GB，共 {total_files} 个可索引文件）",
        f"> **知识库**：[[竹子·冰山·政事堂_股市综合框架]]",
        "",
        f"**最后更新**：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## 分类索引",
        "",
    ]

    for cat_key, files in sorted(all_files.items(), key=lambda x: -len(x[1])):
        if not files:
            continue
        total_bytes = sum(Path(f).stat().st_size for f in files if Path(f).exists())
        total_gb = round(total_bytes / 1024**3, 2)
        icon = "📁" if len(files) > 50 else "📂"
        index_lines.append(f"- {icon} [[{cat_key}|{cat_key}]] — **{len(files)} 个文件**（{total_gb} GB）")

    index_lines.extend([
        "",
        "---",
        "",
        "## 框架关联",
        "",
        "| 框架文件 | 说明 |",
        "|------|------|",
        "| [[竹子·冰山·政事堂_股市综合框架]] | 三层联动总框架 |",
        "| [[竹子魔板35条（应用篇）]] | 技术执行层（竹子魔板） |",
        "",
        "## 快速跳转",
        "",
        "- [[精品资料]] — 核心付费资料（PDF为主）",
        "- [[二次买入法]] — 二次买入系统教程",
        "- [[系统化操盘技术_技法篇]] — K线/量价/形态",
        "- [[系统化操盘技术_功法篇]] — 内功心法",
        "- [[股票中医]] — 基本面/估值/价值投资",
        "- [[股市廖聊吧有声书]] — 有声课程",
        "- [[牛散训练营第一期]]/[[牛散训练营第二期]]/[[牛散训练营第三期]] — 牛散体系",
        "- [[滇南王]] — 滇南王体系实操案例图",
        "- [[竹子魔板的案例]] — 竹子魔板实战案例",
        "",
    ])

    # 覆盖主索引
    main_index = DST_ROOT / "索引.md"
    main_index.write_text("\n".join(index_lines), encoding="utf-8")
    print(f"✅ 主索引已更新: {main_index}")

    print()
    print("=" * 50)
    print(f"🎉 批量导入完成！")
    print(f"   总计: {total_files} 个文件，{len(all_files)} 个分类")
    print(f"   输出: {DST_RAW}")
    print(f"   索引: {DST_ROOT}")


if __name__ == "__main__":
    main()
