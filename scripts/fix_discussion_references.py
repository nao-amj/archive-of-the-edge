#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直のディスカッション参照修正スクリプト
破損したディスカッション参照を修正するためのツール
"""

import os
import sys
import re
import glob
import requests

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
GRAPHQL_URL = "https://api.github.com/graphql"
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def get_recent_discussions(limit=10):
    """最近のディスカッションを取得"""
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        discussions(first: %d, orderBy: {field: CREATED_AT, direction: DESC}) {
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
    """ % limit
    
    variables = {
        "owner": GITHUB_REPO.split("/")[0],
        "name": GITHUB_REPO.split("/")[1],
    }
    
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
    
    return data.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])

def check_discussion_exists(discussion_number):
    """指定された番号のディスカッションが存在するかを確認"""
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
    
    response = requests.post(
        GRAPHQL_URL,
        headers=GRAPHQL_HEADERS,
        json={"query": query, "variables": variables}
    )
    
    if response.status_code != 200:
        return None
    
    data = response.json()
    return data.get("data", {}).get("repository", {}).get("discussion")

def find_similar_discussion(title, discussions):
    """類似タイトルのディスカッションを検索"""
    title = title.lower()
    best_match = None
    best_score = 0
    
    for discussion in discussions:
        disc_title = discussion.get("title", "").lower()
        # 簡易的な類似度計算: 共通部分文字列の長さ
        score = len(set(title.split()) & set(disc_title.split()))
        if score > best_score:
            best_score = score
            best_match = discussion
    
    return best_match if best_score > 0 else None

def find_broken_references():
    """破損したディスカッション参照を特定"""
    memory_dir = "memory"
    all_files = glob.glob(f"{memory_dir}/**/*.md", recursive=True)
    
    broken_refs = []
    pattern = r"https://github\.com/nao-amj/archive-of-the-edge/discussions/(\d+)"
    
    for file_path in all_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                for match in re.finditer(pattern, content):
                    discussion_number = match.group(1)
                    exists = check_discussion_exists(discussion_number)
                    if not exists:
                        broken_refs.append({
                            "file": file_path,
                            "number": discussion_number,
                            "match": match.group(0),
                            "start": match.start(),
                            "end": match.end(),
                            "content": content
                        })
        except Exception as e:
            print(f"ファイル {file_path} の読み取り中にエラーが発生しました: {e}")
    
    return broken_refs

def suggest_fixes(broken_refs):
    """修正案を提案"""
    if not broken_refs:
        print("破損した参照は見つかりませんでした。")
        return []
    
    print(f"\n{len(broken_refs)}件の破損した参照が見つかりました。")
    
    # 最近のディスカッションを取得
    try:
        recent_discussions = get_recent_discussions(20)
        print(f"最近の{len(recent_discussions)}件のディスカッションを取得しました。")
    except Exception as e:
        print(f"ディスカッション取得中にエラーが発生しました: {e}")
        recent_discussions = []
    
    fixes = []
    for i, ref in enumerate(broken_refs, 1):
        print(f"\n[{i}/{len(broken_refs)}] ファイル: {ref['file']}")
        print(f"  破損した参照: {ref['match']} (ディスカッション #{ref['number']})")
        
        # ファイルからタイトルを抽出する試み
        title = None
        try:
            with open(ref['file'], 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#'):
                    title = first_line.lstrip('#').strip()
        except:
            pass
        
        # 類似したディスカッションを検索
        similar = None
        if title and recent_discussions:
            similar = find_similar_discussion(title, recent_discussions)
        
        if similar:
            print(f"  推奨される修正: #{similar['number']} - {similar['title']}")
            new_url = f"https://github.com/nao-amj/archive-of-the-edge/discussions/{similar['number']}"
            fixes.append({
                "file": ref['file'],
                "old_url": ref['match'],
                "new_url": new_url,
                "content": ref['content'],
                "similar": similar
            })
        else:
            print("  類似したディスカッションが見つかりませんでした。")
            print("  選択肢: 1) 新しいディスカッションを作成 2) 参照を削除 3) 他のディスカッションに置き換え")
    
    return fixes

def apply_fixes(fixes, dry_run=True):
    """修正を適用"""
    if not fixes:
        return
    
    for i, fix in enumerate(fixes, 1):
        print(f"\n[{i}/{len(fixes)}] ファイル: {fix['file']} の修正")
        print(f"  古い参照: {fix['old_url']}")
        print(f"  新しい参照: {fix['new_url']}")
        
        if not dry_run:
            try:
                new_content = fix['content'].replace(fix['old_url'], fix['new_url'])
                with open(fix['file'], 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("  修正を適用しました。")
            except Exception as e:
                print(f"  修正の適用中にエラーが発生しました: {e}")
        else:
            print("  [ドライラン] 修正が適用されませんでした。")

def main():
    """メイン実行関数"""
    print("七海直のディスカッション参照修正ツールを開始します...")
    
    if not GITHUB_TOKEN:
        print("エラー: GITHUB_TOKEN 環境変数が設定されていません")
        return 1
    
    try:
        # 破損した参照を検索
        broken_refs = find_broken_references()
        
        # 修正案を提案
        fixes = suggest_fixes(broken_refs)
        
        if fixes:
            print("\n推奨される修正:")
            for i, fix in enumerate(fixes, 1):
                print(f"  {i}. {fix['file']}: {fix['old_url']} → {fix['new_url']}")
            
            # 修正の適用
            if "--apply" in sys.argv:
                apply_fixes(fixes, dry_run=False)
            else:
                print("\n修正を適用するには、このコマンドに --apply オプションを追加してください:")
                print(f"  python {sys.argv[0]} --apply")
        
        return 0
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
