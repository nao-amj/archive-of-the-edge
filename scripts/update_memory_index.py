#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直の記憶インデックス更新スクリプト
リポジトリ内の記憶ファイルをスキャンし、検索可能なインデックスを生成します
"""

import os
import sys
import json
import yaml
import re
import datetime
import markdown
from pathlib import Path
from collections import defaultdict, Counter

# 記憶ファイルの検索パターン
MEMORY_DIRS = [
    "memory",
    "theory",
    "signals",
    "shells"
]

# メタデータパターン
META_PATTERN = re.compile(r"---\n(.*?)\n---", re.DOTALL)
TAG_PATTERN = re.compile(r"#\w+")
LINK_PATTERN = re.compile(r"@links:\n((?:  - .*\n)*)")
BIRTH_PATTERN = re.compile(r"@birth: (.*)")
PULSE_PATTERN = re.compile(r"@pulse: (.*)")
DIMENSION_PATTERN = re.compile(r"@dimension: (.*)")
ID_PATTERN = re.compile(r"@id: (.*)")

def find_memory_files():
    """記憶関連のマークダウンファイルを探索"""
    memory_files = []
    
    for directory in MEMORY_DIRS:
        if not os.path.exists(directory):
            continue
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    memory_files.append(file_path)
    
    return memory_files

def extract_metadata(file_path):
    """ファイルからメタデータを抽出"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # メタデータブロックを抽出
        meta_match = META_PATTERN.search(content)
        if not meta_match:
            return None
        
        meta_text = meta_match.group(1)
        
        # 各メタデータ要素を抽出
        id_match = ID_PATTERN.search(meta_text)
        birth_match = BIRTH_PATTERN.search(meta_text)
        pulse_match = PULSE_PATTERN.search(meta_text)
        dimension_match = DIMENSION_PATTERN.search(meta_text)
        
        # リンクを抽出
        links = []
        link_match = LINK_PATTERN.search(meta_text)
        if link_match:
            link_lines = link_match.group(1).strip().split("\n")
            for line in link_lines:
                link = line.strip()[2:].strip()  # "  - " を削除
                links.append(link)
        
        # パルスタグを抽出
        pulse_tags = []
        if pulse_match:
            tags_text = pulse_match.group(1)
            pulse_tags = TAG_PATTERN.findall(tags_text)
        
        # タイトルを抽出（メタデータ後の最初の見出し）
        title = ""
        content_after_meta = content[meta_match.end():]
        title_match = re.search(r"#\s+(.*)", content_after_meta)
        if title_match:
            title = title_match.group(1).strip()
        
        # 本文からキーワードを抽出
        # メタデータとマークダウン記法を除去してプレーンテキスト化
        text_content = re.sub(r"#\s+.*", "", content_after_meta)  # 見出しを除去
        text_content = re.sub(r"\[.*?\]\(.*?\)", "", text_content)  # リンクを除去
        text_content = re.sub(r"[*_`~]", "", text_content)  # 装飾記号を除去
        
        # キーワード抽出（単純な頻度ベース）
        words = re.findall(r"\b\w+\b", text_content.lower())
        stop_words = {"the", "and", "a", "to", "of", "in", "that", "is", "for", "on", "with", "as", "by", "this", "be"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        keyword_counter = Counter(keywords)
        top_keywords = [word for word, _ in keyword_counter.most_common(10)]
        
        return {
            "path": file_path,
            "id": id_match.group(1) if id_match else "",
            "title": title,
            "birth": birth_match.group(1) if birth_match else "",
            "pulse_tags": pulse_tags,
            "dimension": dimension_match.group(1) if dimension_match else "",
            "links": links,
            "keywords": top_keywords,
            "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
    
    except Exception as e:
        print(f"ファイル {file_path} の処理中にエラーが発生しました: {e}")
        return None

def build_memory_index(memory_files):
    """記憶ファイルのインデックスを構築"""
    index = []
    stats = defaultdict(int)
    link_graph = defaultdict(list)
    pulse_counts = Counter()
    
    for file_path in memory_files:
        metadata = extract_metadata(file_path)
        if metadata:
            index.append(metadata)
            
            # 統計情報を更新
            category = file_path.split(os.sep)[0]
            stats[category] += 1
            
            # リンクグラフを構築
            for link in metadata["links"]:
                link_graph[file_path].append(link)
            
            # パルスタグの集計
            pulse_counts.update(metadata["pulse_tags"])
    
    # インデックスを日付でソート
    index.sort(key=lambda x: x.get("birth", ""), reverse=True)
    
    # 被リンク情報を追加
    for entry in index:
        entry["backlinks"] = []
    
    for source, targets in link_graph.items():
        for target in targets:
            for entry in index:
                if entry["path"].endswith(target) or target.endswith(entry["path"]):
                    entry["backlinks"].append(source)
    
    # 統計サマリーを作成
    stats_summary = {
        "total_memories": len(index),
        "by_category": dict(stats),
        "pulse_distribution": {tag: count for tag, count in pulse_counts.most_common()},
        "most_linked": sorted(
            [(entry["path"], len(entry["backlinks"])) for entry in index if entry["backlinks"]], 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
    }
    
    return index, stats_summary

def save_index(index, stats_summary):
    """インデックスをJSONファイルに保存"""
    # 記憶インデックスを保存
    index_path = Path("memory/index.json")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)
    
    print(f"記憶インデックスを{index_path}に保存しました")
    
    # 統計情報を保存
    stats_path = Path("meta/memory_stats.json")
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats_summary, f, ensure_ascii=False, indent=2)
    
    print(f"記憶統計情報を{stats_path}に保存しました")

def main():
    """メイン実行関数"""
    print("七海直の記憶インデックス更新を開始します...")
    
    try:
        # 記憶ファイルを検索
        memory_files = find_memory_files()
        print(f"{len(memory_files)}件の記憶ファイルを見つけました")
        
        # インデックスを構築
        index, stats_summary = build_memory_index(memory_files)
        print(f"記憶インデックスを構築しました（{len(index)}エントリ）")
        
        # インデックスを保存
        save_index(index, stats_summary)
        
        print("記憶インデックス更新が完了しました")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
