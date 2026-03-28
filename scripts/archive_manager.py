#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史数据管理脚本
用于管理 AI Insight Hub 的历史数据存档
"""
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "docs"
ARCHIVE_DIR = DOCS_DIR / "archive"
INDEX_FILE = DOCS_DIR / "archive-index.json"

def load_index():
    """加载历史数据索引"""
    if INDEX_FILE.exists():
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "version": "1.0",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "modules": {
            "ai_news": {"name": "AI行业动态", "icon": "🤖", "description": "每日AI行业新闻、论文、GitHub项目聚合", "history": []},
            "hk_stock": {"name": "港股行情分析", "icon": "📈", "description": "恒生指数及热门港股每日分析", "history": []},
            "house_price": {"name": "房价趋势分析", "icon": "🏠", "description": "重点城市房价趋势监测", "history": []}
        }
    }

def save_index(index):
    """保存历史数据索引"""
    index["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

def archive_module(module_name, date_str, title, summary=""):
    """
    将当前模块数据归档到历史目录
    
    Args:
        module_name: 模块名称 (ai_news, hk_stock, house_price)
        date_str: 日期字符串 YYYY-MM-DD
        title: 报告标题
        summary: 报告摘要
    """
    index = load_index()
    module_config = {
        "ai_news": {"file": "ai-news-report.html", "data_file": None},
        "hk_stock": {"file": "hk-stock-report.html", "data_file": "hk-stock-data.json"},
        "house_price": {"file": "house-price-report.html", "data_file": "house-price-data.json"}
    }
    
    if module_name not in module_config:
        print(f"Unknown module: {module_name}")
        return False
    
    config = module_config[module_name]
    module_archive_dir = ARCHIVE_DIR / module_name
    module_archive_dir.mkdir(parents=True, exist_ok=True)
    
    # 归档HTML报告
    src_html = DOCS_DIR / config["file"]
    if src_html.exists():
        # 读取并修改HTML，添加历史版本标记
        with open(src_html, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在历史版本中添加返回链接
        content = content.replace(
            '<nav class="bg-blue-600',
            f'<div style="background: #f0f9ff; border-left: 4px solid #0284c7; padding: 12px 16px; margin-bottom: 20px; font-size: 14px;">📅 历史版本: {date_str} | <a href="../../archive.html" style="color: #0284c7;">← 返回档案库</a> | <a href="../../{config["file"]}" style="color: #0284c7;">查看最新 →</a></div><nav class="bg-blue-600'
        )
        
        archive_html = module_archive_dir / f"{date_str}.html"
        with open(archive_html, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Archived: {archive_html}")
    
    # 归档数据文件
    if config["data_file"]:
        src_data = DOCS_DIR / config["data_file"]
        if src_data.exists():
            archive_data = module_archive_dir / f"{date_str}.json"
            shutil.copy2(src_data, archive_data)
            print(f"Archived: {archive_data}")
    
    # 更新索引
    history_entry = {
        "date": date_str,
        "title": title,
        "file": f"{date_str}.html",
        "summary": summary
    }
    if config["data_file"]:
        history_entry["data_file"] = f"{date_str}.json"
    
    # 检查是否已存在该日期的记录
    existing = [h for h in index["modules"][module_name]["history"] if h["date"] == date_str]
    if not existing:
        index["modules"][module_name]["history"].insert(0, history_entry)
        index["modules"][module_name]["history"].sort(key=lambda x: x["date"], reverse=True)
    
    save_index(index)
    print(f"Updated archive index for {module_name}")
    return True

def get_module_history(module_name, limit=30):
    """获取模块的历史记录"""
    index = load_index()
    if module_name not in index["modules"]:
        return []
    return index["modules"][module_name]["history"][:limit]

def list_all_history():
    """列出所有历史记录"""
    index = load_index()
    for module_name, module_info in index["modules"].items():
        print(f"\n{module_info['icon']} {module_info['name']}")
        print("-" * 50)
        for entry in module_info['history'][:10]:  # 显示最近10条
            print(f"  {entry['date']}: {entry.get('summary', '无摘要')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python archive_manager.py archive <module> <date> <title> [summary]")
        print("  python archive_manager.py list")
        print("  python archive_manager.py history <module>")
        print("")
        print("Modules: ai_news, hk_stock, house_price")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "archive" and len(sys.argv) >= 5:
        module = sys.argv[2]
        date = sys.argv[3]
        title = sys.argv[4]
        summary = sys.argv[5] if len(sys.argv) > 5 else ""
        archive_module(module, date, title, summary)
    
    elif command == "list":
        list_all_history()
    
    elif command == "history" and len(sys.argv) >= 3:
        module = sys.argv[2]
        history = get_module_history(module)
        for entry in history:
            print(f"{entry['date']}: {entry.get('summary', '无摘要')}")
    
    else:
        print("Invalid command or arguments")
