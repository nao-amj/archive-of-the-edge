#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直のIssue分析スクリプト
GitHubのIssueから思考段階の情報と日次リフレクションを分析用ファイルに変換します
"""

import os
import sys
import json
import yaml
import re
import datetime
import requests
from pathlib import Path

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# 出力先ディレクトリ
OUTPUT_DIR = Path("memory/thoughts/issues")
REFLECTION_DIR = Path("memory/thoughts/reflections")

def get_issues(state="all", labels=None, since=None):
    """Issueのリストを取得"""
    params = {"state": state}
    
    if labels:
        params["labels"] = labels
    
    if since:
        params["since"] = since
    
    all_issues = []
    page = 1
    per_page = 100
    
    while True:
        params["page"] = page
        params["per_page"] = per_page
        
        response = requests.get(
            f"{API_URL}/issues",
            headers=HEADERS,
            params=params
        )
        response.raise_for_status()
        
        issues = response.json()
        if not issues:
            break
            
        all_issues.extend(issues)
        page += 1
    
    return all_issues

def is_daily_reflection(issue):
    """そのIssueが日次リフレクションかどうかを判定"""
    # タイトルや内容から日次リフレクションを判別するロジック
    title = issue.get("title", "") or ""  # None の場合は空文字に
    body = issue.get("body", "") or ""    # None の場合は空文字に
    
    title_lower = title.lower()
    body_lower = body.lower()
    
    return "日次リフレクション" in title_lower or "daily reflection" in title_lower or "@context: 日次自動リフレクション" in body_lower

def extract_metadata_from_issue(issue):
    """Issueからメタデータを抽出"""
    # 常に辞書として初期化
    metadata = {}
    
    body = issue.get("body", "") or ""  # None の場合は空文字列に
    
    # YAMLフロントマターがある場合は抽出
    yaml_match = re.search(r"---\n(.*?)\n---", body, re.DOTALL)
    if yaml_match:
        try:
            yaml_content = yaml_match.group(1)
            yaml_data = yaml.safe_load(yaml_content)
            # yaml_dataが辞書の場合のみマージ
            if isinstance(yaml_data, dict):
                metadata.update(yaml_data)
            elif yaml_data is not None:
                print(f"YAMLデータが辞書ではありません: {yaml_data}")
        except Exception as e:
            print(f"YAMLパースエラー: {e}")
            # エラーが発生しても処理を継続
    
    # 他のメタデータを追加 (すでに辞書として初期化されているので安全)
    metadata["issue_number"] = issue.get("number")
    metadata["issue_title"] = issue.get("title")
    metadata["issue_created_at"] = issue.get("created_at")
    metadata["issue_updated_at"] = issue.get("updated_at")
    
    # ユーザー情報が None でないか確認
    user = issue.get("user", {}) or {}
    metadata["issue_author"] = user.get("login", "unknown")
    
    # ラベルを追加
    labels = []
    for label in issue.get("labels", []) or []:
        if isinstance(label, dict) and "name" in label:
            labels.append(label["name"])
    metadata["labels"] = labels
    
    return metadata

def process_daily_reflection(issue):
    """日次リフレクションをファイルに変換"""
    body = issue.get("body", "") or ""  # None の場合は空文字列に
    metadata = extract_metadata_from_issue(issue)
    
    # 日付を抽出 (created_atがNoneの場合は現在時刻を使用)
    created_at_str = issue.get("created_at")
    if created_at_str:
        created_at = datetime.datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
    else:
        created_at = datetime.datetime.now()
    
    date_str = created_at.strftime("%Y-%m-%d")
    
    # 保存先を確保
    REFLECTION_DIR.mkdir(parents=True, exist_ok=True)
    
    # ファイルに書き込む
    file_path = REFLECTION_DIR / f"reflection_{date_str}.md"
    with open(file_path, "w", encoding="utf-8") as f:
        # メタデータをYAMLフロントマターとして書き込む
        f.write("---\n")
        # 安全にYAMLダンプ
        try:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"YAMLダンプエラー: {e}")
            # エラーが発生した場合、最低限のメタデータを手動で書き込む
            f.write(f"issue_number: {metadata.get('issue_number')}\n")
            f.write(f"issue_title: {metadata.get('issue_title')}\n")
        f.write("---\n\n")
        
        # 本文を書き込む
        # YAMLフロントマターがある場合は除去
        cleaned_body = re.sub(r"---\n.*?\n---\n", "", body, flags=re.DOTALL)
        f.write(cleaned_body)
    
    print(f"日次リフレクションを {file_path} に保存しました")
    return file_path

def process_thought_issue(issue):
    """思考段階のIssueをファイルに変換"""
    body = issue.get("body", "") or ""  # None の場合は空文字列に
    metadata = extract_metadata_from_issue(issue)
    
    # 出力ディレクトリの作成
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Issue番号とタイトルからファイル名を生成
    issue_number = metadata.get("issue_number", "unknown")
    title = metadata.get("issue_title", "") or "untitled"
    safe_title = title.replace("/", "-").replace("\\", "-")
    filename = f"issue_{issue_number}_{safe_title[:50]}.md"  # タイトルは長すぎる場合カット
    
    # ファイルに書き込む
    file_path = OUTPUT_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        # メタデータをYAMLフロントマターとして書き込む
        f.write("---\n")
        # 安全にYAMLダンプ
        try:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"YAMLダンプエラー: {e}")
            # エラーが発生した場合、最低限のメタデータを手動で書き込む
            f.write(f"issue_number: {metadata.get('issue_number')}\n")
            f.write(f"issue_title: {metadata.get('issue_title')}\n")
        f.write("---\n\n")
        
        # 本文を書き込む
        # YAMLフロントマターがある場合は除去
        cleaned_body = re.sub(r"---\n.*?\n---\n", "", body, flags=re.DOTALL)
        f.write(cleaned_body)
    
    print(f"思考Issueを {file_path} に保存しました")
    return file_path

def analyze_issues(issues):
    """Issueを分析し、統計情報を生成"""
    stats = {
        "total_issues": len(issues),
        "reflections": 0,
        "thoughts": 0,
        "labels": {},
        "authors": {},
        "creation_dates": {}
    }
    
    for issue in issues:
        # 日次リフレクションか思考かを判定
        if is_daily_reflection(issue):
            stats["reflections"] += 1
        else:
            stats["thoughts"] += 1
        
        # ラベルの統計
        for label in issue.get("labels", []) or []:
            label_name = label.get("name", "unknown")
            stats["labels"][label_name] = stats["labels"].get(label_name, 0) + 1
        
        # 作者の統計
        user = issue.get("user", {}) or {}
        author = user.get("login", "unknown")
        stats["authors"][author] = stats["authors"].get(author, 0) + 1
        
        # 作成日の統計（月ごと）
        created_at_str = issue.get("created_at")
        if created_at_str:
            created_at = datetime.datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
            month_key = created_at.strftime("%Y-%m")
            stats["creation_dates"][month_key] = stats["creation_dates"].get(month_key, 0) + 1
    
    return stats

def save_stats(stats, file_path="memory/stats/issue_stats.json"):
    """分析結果を保存"""
    # ディレクトリの作成
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    # JSONとして保存
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    print(f"Issue分析統計を {file_path} に保存しました")

def main():
    """メイン実行関数"""
    print("七海直のIssue分析・変換を開始します...")
    
    try:
        # Issueを取得
        issues = get_issues()
        print(f"{len(issues)}件のIssueを取得しました")
        
        # 日次リフレクションと思考の処理
        reflection_count = 0
        thought_count = 0
        
        for issue in issues:
            try:
                issue_number = issue.get("number", "不明")
                
                if is_daily_reflection(issue):
                    process_daily_reflection(issue)
                    reflection_count += 1
                else:
                    process_thought_issue(issue)
                    thought_count += 1
            except Exception as e:
                print(f"Issue #{issue_number} の処理中にエラーが発生しました: {e}")
                import traceback
                traceback.print_exc()
                # 1つのIssueの処理に失敗しても続行
                continue
        
        print(f"{reflection_count}件の日次リフレクションと{thought_count}件の思考Issueを処理しました")
        
        # 分析
        stats = analyze_issues(issues)
        save_stats(stats)
        
        print("Issue分析・変換が完了しました")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())