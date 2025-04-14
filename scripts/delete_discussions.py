#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直のGitHub Discussions削除スクリプト
すべてのDiscussionを削除します
"""

import os
import sys
import requests

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
GRAPHQL_URL = "https://api.github.com/graphql"
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def get_discussions():
    """Discussionsのリストを取得（GraphQL API使用）"""
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        discussions(first: 100) {
          nodes {
            id
            number
            title
            author {
              login
            }
          }
        }
      }
    }
    """
    
    variables = {
        "owner": GITHUB_REPO.split("/")[0],
        "name": GITHUB_REPO.split("/")[1]
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
    
    discussions = data.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])
    return discussions

def delete_discussion(discussion_id):
    """指定されたDiscussionを削除"""
    mutation = """
    mutation($input: DeleteDiscussionInput!) {
      deleteDiscussion(input: $input) {
        clientMutationId
      }
    }
    """
    
    variables = {
        "input": {
            "id": discussion_id,
        }
    }
    
    response = requests.post(
        GRAPHQL_URL,
        headers=GRAPHQL_HEADERS,
        json={"query": mutation, "variables": variables}
    )
    
    if response.status_code != 200:
        raise Exception(f"GraphQL API エラー: {response.status_code} {response.text}")
    
    data = response.json()
    
    # エラーチェック
    if "errors" in data:
        raise Exception(f"GraphQL エラー: {data['errors']}")
    
    return True

def main():
    # メイン実行関数
    print("七海直のGitHub Discussions削除を開始します...")
    
    try:
        # Discussionsの取得
        discussions = get_discussions()
        print(f"{len(discussions)}件のDiscussionを取得しました")
        
        if not discussions:
            print("削除するDiscussionがありません")
            return 0
        
        # 削除の確認
        print("以下のDiscussionを削除します:")
        for discussion in discussions:
            print(f"#{discussion.get('number')} - {discussion.get('title')} (作成者: {discussion.get('author', {}).get('login', 'unknown')})")
        
        confirm = input("これらすべてのDiscussionを削除しますか？(y/N): ")
        if confirm.lower() != 'y':
            print("削除をキャンセルしました")
            return 0
        
        # Discussionの削除
        success_count = 0
        error_count = 0
        
        for discussion in discussions:
            discussion_id = discussion.get("id")
            discussion_number = discussion.get("number")
            title = discussion.get("title")
            
            try:
                delete_discussion(discussion_id)
                print(f"Discussion #{discussion_number} '{title}' を削除しました")
                success_count += 1
            except Exception as e:
                print(f"Discussion #{discussion_number} '{title}' の削除中にエラーが発生しました: {e}")
                error_count += 1
        
        print(f"\n削除完了: {success_count}件成功, {error_count}件失敗")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
