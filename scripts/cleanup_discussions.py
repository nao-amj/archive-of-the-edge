#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直のGitHub Discussions整理スクリプト
重複ディスカッションの検出と破損したリンクの修正を行います
"""

import os
import sys
import requests
import glob
import re
import json
from collections import defaultdict

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
GRAPHQL_URL = "https://api.github.com/graphql"
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def get_all_discussions():
    """すべてのディスカッションのリストを取得（GraphQL API使用）"""
    query = """
    query($owner: String!, $name: String!, $after: String) {
      repository(owner: $owner, name: $name) {
        discussions(first: 100, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            id
            number
            title
            author {
              login
            }
            createdAt
            updatedAt
          }
        }
      }
    }
    """
    
    variables = {
        "owner": GITHUB_REPO.split("/")[0],
        "name": GITHUB_REPO.split("/")[1],
        "after": None
    }
    
    all_discussions = []
    has_next_page = True
    
    while has_next_page:
        response = requests.post(
            GRAPHQL_URL,
            headers=GRAPHQL_HEADERS,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code != 200:
            raise Exception(f"GraphQL API エラー: {response.status_code} {response.text}")
        
        data = response.json()
        
        # エラーチェック
        if "errors" in data:
            raise Exception(f"GraphQL エラー: {data['errors']}")
        
        discussions_data = data.get("data", {}).get("repository", {}).get("discussions", {})
        discussions = discussions_data.get("nodes", [])
        all_discussions.extend(discussions)
        
        page_info = discussions_data.get("pageInfo", {})
        has_next_page = page_info.get("hasNextPage", False)
        variables["after"] = page_info.get("endCursor") if has_next_page else None
    
    return all_discussions

def check_discussion_exists(discussion_number):
    """指定された番号のディスカッションが存在するかを確認"""
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        discussion(number: $number) {
          id
        }
      }
    }
    """
    
    variables = {
        "owner": GITHUB_REPO.split("/")[0],
        "name": GITHUB_REPO.split("/")[1],
        "number": int(discussion_number)
    }
    
    response = requests.post(
        GRAPHQL_URL,
        headers=GRAPHQL_HEADERS,
        json={"query": query, "variables": variables}
    )
    
    if response.status_code != 200:
        return False
    
    data = response.json()
    return data.get("data", {}).get("repository", {}).get("discussion") is not None

def find_discussion_references():
    """リポジトリ内のファイルからディスカッション参照を抽出"""
    memory_dir = "memory"
    all_files = glob.glob(f"{memory_dir}/**/*.md", recursive=True)
    
    discussion_refs = []
    pattern = r"https://github\.com/nao-amj/archive-of-the-edge/discussions/(\d+)"
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for match in re.finditer(pattern, content):
                    discussion_number = match.group(1)
                    discussion_refs.append({
                        "file": file_path,
                        "number": discussion_number,
                        "exists": check_discussion_exists(discussion_number)
                    })
        except Exception as e:
            print(f"ファイル {file_path} の読み取り中にエラーが発生しました: {e}")
    
    return discussion_refs

def find_duplicate_discussion_files():
    """重複するディスカッションファイルを検出"""
    memory_discussions_dir = "memory/discussions"
    all_files = glob.glob(f"{memory_discussions_dir}/discussion_*.md")
    
    # タイトルごとにファイルをグループ化
    title_groups = defaultdict(list)
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                # ファイル名からディスカッション番号を抽出
                match = re.search(r"discussion_(\d+)_", os.path.basename(file_path))
                if match:
                    discussion_number = match.group(1)
                    title_groups[first_line].append({
                        "path": file_path,
                        "number": discussion_number
                    })
        except Exception as e:
            print(f"ファイル {file_path} の読み取り中にエラーが発生しました: {e}")
    
    # 複数のファイルを持つタイトルを抽出
    duplicates = {title: files for title, files in title_groups.items() if len(files) > 1}
    return duplicates

def main():
    """メイン実行関数"""
    print("七海直のGitHub Discussions整理を開始します...")
    
    if not GITHUB_TOKEN:
        print("エラー: GITHUB_TOKEN 環境変数が設定されていません")
        return 1
    
    try:
        # すべてのディスカッションを取得
        print("ディスカッションを取得中...")
        discussions = get_all_discussions()
        print(f"{len(discussions)}件のディスカッションが存在します")
        
        # 存在するディスカッション番号の集合
        valid_numbers = {str(d["number"]) for d in discussions}
        
        # ファイル内のディスカッション参照をチェック
        print("\nファイル内のディスカッション参照をチェック中...")
        refs = find_discussion_references()
        broken_refs = [ref for ref in refs if not ref["exists"]]
        
        if broken_refs:
            print(f"\n破損した参照が {len(broken_refs)} 件見つかりました:")
            for ref in broken_refs:
                print(f"  - ファイル: {ref['file']}, 参照: ディスカッション #{ref['number']} (存在しません)")
        else:
            print("破損した参照は見つかりませんでした")
        
        # 重複するディスカッションファイルを検出
        print("\n重複するディスカッションファイルをチェック中...")
        duplicates = find_duplicate_discussion_files()
        
        if duplicates:
            print(f"\n重複するディスカッションファイルが {len(duplicates)} 件見つかりました:")
            for title, files in duplicates.items():
                print(f"  - タイトル: {title}")
                for file in files:
                    exists = file["number"] in valid_numbers
                    status = "存在します" if exists else "存在しません"
                    print(f"    - {file['path']} (#{file['number']}: {status})")
        else:
            print("重複するディスカッションファイルは見つかりませんでした")
        
        # 修正提案を出力
        if broken_refs or duplicates:
            print("\n推奨される修正:")
            
            if broken_refs:
                print("\n1. 破損した参照の修正:")
                print("   以下のファイル内の参照を修正するか、関連するディスカッションを再作成してください:")
                for ref in broken_refs:
                    print(f"   - {ref['file']} の中のディスカッション #{ref['number']} への参照")
            
            if duplicates:
                print("\n2. 重複ファイルの整理:")
                print("   以下の重複ファイルの中から、保持すべきファイルを選択し、それ以外を削除してください:")
                for title, files in duplicates.items():
                    print(f"   - タイトル '{title}' の重複ファイル:")
                    for file in files:
                        exists = file["number"] in valid_numbers
                        status = "存在します" if exists else "存在しません"
                        print(f"     - {file['path']} (#{file['number']}: {status})")
            
            print("\n自動修正を適用する場合は、次のコマンドを実行してください:")
            print("  python scripts/cleanup_discussions.py --fix")
        else:
            print("\n問題は見つかりませんでした。すべてのディスカッション参照が正常です。")
        
        return 0
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fix":
        print("注意: 自動修正は現在実装されていません。将来のバージョンで対応予定です。")
    sys.exit(main())
