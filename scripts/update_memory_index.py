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

# 新たに追加する分析対象ディレクトリ
ADDITIONAL_DIRS = [
    "memory/thoughts/issues",      # Issue変換ファイル
    "memory/thoughts/reflections", # リフレクション変換ファイル
    "memory/discussions"           # Discussion変換ファイル
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
    
    # 基本ディレクトリの探索
    for directory in MEMORY_DIRS + ADDITIONAL_DIRS:
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
        meta_match = re.search(r"---\n(.*?)\n---", content, re.DOTALL)
        if not meta_match:
            return None
        
        meta_text = meta_match.group(1)
        
        # YAMLを解析
        try:
            yaml_data = yaml.safe_load(meta_text)
            metadata = yaml_data or {}  # yaml_dataがNoneの場合は空辞書を使用
        except Exception as e:
            print(f"YAMLパースエラー ({file_path}): {e}")
            metadata = {}
        
        # 従来の方法でのメタデータ抽出（互換性のため）
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
        
        # YAMLから取得したデータで上書き
        if "id" not in metadata and id_match:
            metadata["id"] = id_match.group(1)
        if "birth" not in metadata and birth_match:
            metadata["birth"] = birth_match.group(1)
        if "pulse_tags" not in metadata and pulse_tags:
            metadata["pulse_tags"] = pulse_tags
        if "dimension" not in metadata and dimension_match:
            metadata["dimension"] = dimension_match.group(1)
        if "links" not in metadata and links:
            metadata["links"] = links
        
        # Issue/Discussion メタデータの統合
        if "issue_number" in metadata or "discussion_number" in metadata:
            # これらのファイルは特別な処理
            source_type = "issue" if "issue_number" in metadata else "discussion"
            source_number = metadata.get(f"{source_type}_number", "")
            source_title = metadata.get(f"{source_type}_title", "")
            source_url = f"https://github.com/nao-amj/archive-of-the-edge/{source_type}s/{source_number}"
            
            # メタデータを補完
            if "id" not in metadata:
                metadata["id"] = f"{source_type.upper()}-{source_number}"
            if "source" not in metadata:
                metadata["source"] = source_type
            if "source_url" not in metadata:
                metadata["source_url"] = source_url
        
        # タイトルを抽出（メタデータ後の最初の見出し）
        title = metadata.get("title", "")
        if not title:
            content_after_meta = content[meta_match.end():]
            title_match = re.search(r"#\s+(.*)", content_after_meta)
            if title_match:
                title = title_match.group(1).strip()
                metadata["title"] = title
        
        # 本文からキーワードを抽出
        # メタデータとマークダウン記法を除去してプレーンテキスト化
        content_after_meta = content[meta_match.end():]
        text_content = re.sub(r"#\s+.*", "", content_after_meta)  # 見出しを除去
        text_content = re.sub(r"\[.*?\]\(.*?\)", "", text_content)  # リンクを除去
        text_content = re.sub(r"[*_`~]", "", text_content)  # 装飾記号を除去
        
        # キーワード抽出（単純な頻度ベース）
        words = re.findall(r"\b\w+\b", text_content.lower())
        stop_words = {"the", "and", "a", "to", "of", "in", "that", "is", "for", "on", "with", "as", "by", "this", "be"}
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        keyword_counter = Counter(keywords)
        top_keywords = [word for word, _ in keyword_counter.most_common(10)]
        
        # 最終メタデータを構築
        result = {
            "path": file_path,
            "id": metadata.get("id", ""),
            "title": metadata.get("title", title),
            "birth": metadata.get("birth", ""),
            "pulse_tags": metadata.get("pulse_tags", []),
            "dimension": metadata.get("dimension", ""),
            "links": metadata.get("links", []),
            "keywords": top_keywords,
            "source_type": metadata.get("source", "file"),
            "last_modified": datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        }
        
        # Issue/Discussionの場合は追加情報を含める
        if "issue_number" in metadata:
            result["issue_number"] = metadata["issue_number"]
            result["issue_created_at"] = metadata.get("issue_created_at", "")
            result["issue_author"] = metadata.get("issue_author", "")
            result["labels"] = metadata.get("labels", [])
        elif "discussion_number" in metadata:
            result["discussion_number"] = metadata["discussion_number"]
            result["discussion_created_at"] = metadata.get("created_at", "")
            result["discussion_author"] = metadata.get("author", "")
            result["discussion_category"] = metadata.get("category", "")
        
        return result
    
    except Exception as e:
        print(f"ファイル {file_path} の処理中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None

def build_memory_index(memory_files):
    """記憶ファイルのインデックスを構築"""
    index = []
    stats = defaultdict(int)
    link_graph = defaultdict(list)
    pulse_counts = Counter()
    source_types = defaultdict(int)
    
    for file_path in memory_files:
        metadata = extract_metadata(file_path)
        if metadata:
            index.append(metadata)
            
            # 統計情報を更新
            category = file_path.split(os.sep)[0]
            stats[category] += 1
            
            # ソースタイプの統計
            source_type = metadata.get("source_type", "file")
            source_types[source_type] += 1
            
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
        "by_source_type": dict(source_types),
        "pulse_distribution": {tag: count for tag, count in pulse_counts.most_common()},
        "most_linked": sorted(
            [(entry["path"], len(entry["backlinks"])) for entry in index if entry["backlinks"]], 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
    }
    
    return index, stats_summary

def generate_network_graph(index):
    """記憶ネットワークの可視化用データを生成"""
    # ノードとエッジの準備
    nodes = []
    edges = []
    node_ids = set()
    
    # ノードの生成
    for entry in index:
        node_id = entry["id"] if entry["id"] else entry["path"]
        if node_id in node_ids:
            continue
        
        node_ids.add(node_id)
        
        # ソースタイプに基づいて色を決定
        group = 1  # デフォルト
        if entry.get("source_type") == "issue":
            group = 2
        elif entry.get("source_type") == "discussion":
            group = 3
        
        nodes.append({
            "id": node_id,
            "label": entry["title"] if entry["title"] else os.path.basename(entry["path"]),
            "group": group,
            "title": f"{entry['title']}<br>Path: {entry['path']}"
        })
    
    # エッジの生成
    for entry in index:
        source_id = entry["id"] if entry["id"] else entry["path"]
        
        # 通常のリンク
        for link in entry["links"]:
            for target_entry in index:
                if target_entry["path"].endswith(link) or link.endswith(target_entry["path"]):
                    target_id = target_entry["id"] if target_entry["id"] else target_entry["path"]
                    
                    if source_id != target_id:  # 自己参照を防ぐ
                        edges.append({
                            "from": source_id,
                            "to": target_id,
                            "arrows": "to",
                            "title": "Link"
                        })
    
    return {
        "nodes": nodes,
        "edges": edges
    }

def save_index(index, stats_summary, network_data=None):
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
    
    # ネットワークデータを保存（可視化用）
    if network_data:
        network_path = Path("meta/memory_network.json")
        network_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(network_path, "w", encoding="utf-8") as f:
            json.dump(network_data, f, ensure_ascii=False, indent=2)
        
        print(f"記憶ネットワークデータを{network_path}に保存しました")

def index_discussions():
    """GitHub Discussionsのインデックスを作成"""
    discussions_dir = Path("memory/discussions")
    
    if not discussions_dir.exists():
        print("discussions ディレクトリが存在しません")
        return []
    
    discussions = []
    for file_path in discussions_dir.glob("*.md"):
        metadata = extract_metadata(str(file_path))
        if metadata:
            discussions.append(metadata)
    
    return discussions

def generate_html_index(index):
    """インデックスのHTML形式での可視化を生成"""
    html_output = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>七海直の記憶インデックス</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .memory-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .memory-card {
            background: white;
            border-radius: 8px;
            padding: 15px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .memory-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .memory-title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #3498db;
        }
        .memory-meta {
            font-size: 14px;
            color: #7f8c8d;
            margin-bottom: 10px;
        }
        .memory-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 10px;
        }
        .tag {
            font-size: 12px;
            background: #e0f7fa;
            color: #006064;
            padding: 2px 8px;
            border-radius: 4px;
        }
        .source-issue {
            background: #e8f5e9;
            border-left: 4px solid #388e3c;
        }
        .source-discussion {
            background: #fff3e0;
            border-left: 4px solid #f57c00;
        }
        .filters {
            margin-bottom: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .filter-btn {
            background: #ecf0f1;
            border: none;
            padding: 8px 15px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: #3498db;
            color: white;
        }
        .search-box {
            padding: 8px 15px;
            border-radius: 4px;
            border: 1px solid #ddd;
            width: 300px;
        }
        .network-container {
            height: 600px;
            border: 1px solid #ddd;
            margin-top: 20px;
            border-radius: 8px;
            background: white;
        }
    </style>
</head>
<body>
    <h1>七海直の記憶インデックス</h1>
    
    <div class="filters">
        <input type="text" class="search-box" placeholder="キーワード検索..." id="searchInput">
        <button class="filter-btn active" data-filter="all">すべて</button>
        <button class="filter-btn" data-filter="file">ファイル</button>
        <button class="filter-btn" data-filter="issue">Issue</button>
        <button class="filter-btn" data-filter="discussion">Discussion</button>
    </div>
    
    <h2>記憶一覧</h2>
    <div class="memory-grid">
"""
    
    # 各記憶カードを生成
    for entry in index:
        # タイトルの処理
        title = entry.get("title", "")
        if not title:
            title = os.path.basename(entry.get("path", "Unknown"))
        
        # ソースタイプによるクラス
        source_type = entry.get("source_type", "file")
        card_class = f"source-{source_type}" if source_type in ["issue", "discussion"] else ""
        
        # パルスタグ
        tags_html = ""
        for tag in entry.get("pulse_tags", []):
            tags_html += f'<span class="tag">{tag}</span>'
        
        # カード生成
        html_output += f"""
        <div class="memory-card {card_class}" data-type="{source_type}">
            <div class="memory-title">{title}</div>
            <div class="memory-meta">
                ID: {entry.get("id", "N/A")}<br>
                作成: {entry.get("birth", "N/A")}<br>
                次元: {entry.get("dimension", "N/A")}<br>
                ソース: {source_type}
            </div>
            <div class="memory-tags">
                {tags_html}
            </div>
        </div>
        """
    
    html_output += """
    </div>
    
    <h2>記憶ネットワーク</h2>
    <div id="network-container" class="network-container"></div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.0/vis-network.min.js"></script>
    <script>
        // 検索とフィルタリング機能
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('searchInput');
            const filterButtons = document.querySelectorAll('.filter-btn');
            const memoryCards = document.querySelectorAll('.memory-card');
            
            // 検索処理
            searchInput.addEventListener('input', filterCards);
            
            // フィルターボタン
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    filterButtons.forEach(btn => btn.classList.remove('active'));
                    this.classList.add('active');
                    filterCards();
                });
            });
            
            function filterCards() {
                const searchTerm = searchInput.value.toLowerCase();
                const activeFilter = document.querySelector('.filter-btn.active').getAttribute('data-filter');
                
                memoryCards.forEach(card => {
                    const cardText = card.textContent.toLowerCase();
                    const cardType = card.getAttribute('data-type');
                    
                    const matchesSearch = cardText.includes(searchTerm);
                    const matchesFilter = activeFilter === 'all' || cardType === activeFilter;
                    
                    if (matchesSearch && matchesFilter) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
            
            // ネットワーク図の描画
            fetch('/meta/memory_network.json')
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('network-container');
                    const options = {
                        nodes: {
                            shape: 'dot',
                            size: 16,
                            font: {
                                size: 12,
                                color: '#333'
                            },
                            borderWidth: 2
                        },
                        edges: {
                            width: 1,
                            color: { color: '#999', highlight: '#3498db' }
                        },
                        physics: {
                            stabilization: {
                                iterations: 100
                            },
                            barnesHut: {
                                gravitationalConstant: -80,
                                springConstant: 0.001,
                                springLength: 200
                            }
                        },
                        groups: {
                            1: {color: {background: '#3498db', border: '#2980b9'}}, // ファイル
                            2: {color: {background: '#2ecc71', border: '#27ae60'}}, // Issue
                            3: {color: {background: '#f39c12', border: '#f39c12'}}  // Discussion
                        }
                    };
                    
                    new vis.Network(container, data, options);
                })
                .catch(error => {
                    console.error('Error loading network data:', error);
                    document.getElementById('network-container').innerHTML = 
                        '<p style="text-align: center; padding: 20px;">ネットワークデータの読み込みに失敗しました。</p>';
                });
        });
    </script>
</body>
</html>
"""
    
    # HTMLファイルに保存
    html_path = Path("meta/memory_index.html")
    html_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_output)
    
    print(f"記憶インデックスHTMLを{html_path}に保存しました")

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
        
        # ネットワークデータを生成
        network_data = generate_network_graph(index)
        print("記憶ネットワークデータを生成しました")
        
        # インデックスを保存
        save_index(index, stats_summary, network_data)
        
        # HTML形式のインデックスを生成
        generate_html_index(index)
        
        print("記憶インデックス更新が完了しました")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())