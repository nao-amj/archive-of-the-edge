#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直のGitHub Discussionsバリデーションスクリプト
ディスカッションの存在確認と参照の検証を行います
"""

import os
import sys
import requests
import re
import glob

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
GRAPHQL_URL = "https://api.github.com/graphql"
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def check_discussion_exists(discussion_number):
    """特定のDiscussionが存在するか確認する"""
    query = """
    query($owner: String!, $name: String!, $number: Int!) {
      repository(owner: $owner, name: $name) {
        discussion(number: $number) {
          id
          title
        }
      }
    }
    """
    
    variables = {
        "owner": GITHUB_REPO.split("/")[0],
        "name": GITHUB_REPO.split("/")[1],
        "number": int(discussion_number)
    }
    
    try:
        response = requests.post(
            GRAPHQL_URL,
            headers=GRAPHQL_HEADERS,
            json={"query": query, "variables": variables}
        )
        
        if response.status_code != 200:
            print(f"API エラー: {response.status_code} {response.text}")
            return False
        
        data = response.json()
        discussion = data.get("data", {}).get("repository", {}).get("discussion")
        exists = discussion is not None
        
        if exists:
            print(f"Discussion #{discussion_number} '{discussion.get('title')}' は存在します")
        else:
            print(f"Discussion #{discussion_number} は存在しません")
            
        return exists
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return False

def scan_for_discussion_references():
    """リポジトリ内のすべてのファイルをスキャンして、存在しないディスカッションへの参照を検出"""
    print("ディスカッション参照をスキャンしています...")
    
    # ディスカッション参照のパターン
    patterns = [
        r'https://github\.com/nao-amj/archive-of-the-edge/discussions/(\d+)',  # URLリンク
        r'discussion_(\d+)_',  # ファイル名パターン
        r'Discussion #(\d+)'   # テキスト内参照
    ]
    
    # 検索するファイルタイプ
    file_types = [
        "**/*.md", 
        "**/*.py", 
        "**/*.yml", 
        "**/*.json"
    ]
    
    # 存在しないディスカッションへの参照を追跡
    invalid_references = {}
    
    # すべてのディスカッション番号を追跡
    all_discussion_numbers = set()
    
    # ファイルをスキャン
    for file_pattern in file_types:
        for filepath in glob.glob(file_pattern, recursive=True):
            try:
                with open(filepath, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    for pattern in patterns:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            discussion_number = match.group(1)
                            all_discussion_numbers.add(discussion_number)
            except Exception as e:
                print(f"ファイル {filepath} の読み込み中にエラーが発生しました: {e}")
    
    # 各ディスカッション番号が実際に存在するかチェック
    for discussion_number in sorted(all_discussion_numbers, key=int):
        if not check_discussion_exists(discussion_number):
            invalid_references[discussion_number] = []
            
            # このディスカッション番号を含むファイルを再度検索
            for file_pattern in file_types:
                for filepath in glob.glob(file_pattern, recursive=True):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as file:
                            content = file.read()
                            
                            for pattern in patterns:
                                if re.search(pattern.replace(r'(\d+)', discussion_number), content):
                                    invalid_references[discussion_number].append(filepath)
                    except Exception:
                        pass
    
    return invalid_references

def main():
    """メイン実行関数"""
    if len(sys.argv) > 1:
        # 特定のディスカッション番号をチェック
        discussion_number = sys.argv[1]
        exists = check_discussion_exists(discussion_number)
        return 0 if exists else 1
    else:
        # すべての参照をスキャン
        invalid_references = scan_for_discussion_references()
        
        if invalid_references:
            print("\n存在しないディスカッションへの参照が見つかりました:")
            for discussion_number, files in invalid_references.items():
                print(f"\nDiscussion #{discussion_number}:")
                for file in files:
                    print(f"  - {file}")
            
            print("\n解決策:")
            print("1. 存在しないディスカッションを再作成するか")
            print("2. 該当するファイルの参照を修正してください")
            return 1
        else:
            print("すべてのディスカッション参照は有効です")
            return 0

if __name__ == "__main__":
    sys.exit(main())
