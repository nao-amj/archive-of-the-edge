#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直のGitHub Discussions活用スクリプト
記憶・思考の整理や交流をGitHub Discussionsを通じて実現します
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
GRAPHQL_URL = "https://api.github.com/graphql"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
GRAPHQL_HEADERS = {
    "Authorization": f"bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

# 出力先ディレクトリ
OUTPUT_DIR = Path("memory/discussions")
MEMORY_INDEX_PATH = Path("memory/index.json")

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
            body
            createdAt
            updatedAt
            author {
              login
            }
            category {
              name
            }
            comments(first: 50) {
              nodes {
                body
                createdAt
                author {
                  login
                }
              }
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

def create_discussion(title, body, category_id="MDE4OkRpc2N1c3Npb25DYXRlZ29yeTMyMDI5NjU2"):
    """Discussionを新規作成"""
    # デフォルトのカテゴリーIDは一般的な"General"カテゴリー
    # 実際には事前にGraphQLでカテゴリーIDを取得する必要がある
    
    mutation = """
    mutation($input: CreateDiscussionInput!) {
      createDiscussion(input: $input) {
        discussion {
          id
          number
          title
          url
        }
      }
    }
    """
    
    variables = {
        "input": {
            "repositoryId": get_repository_id(),
            "title": title,
            "body": body,
            "categoryId": category_id
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
    
    return data.get("data", {}).get("createDiscussion", {}).get("discussion", {})

def get_repository_id():
    """リポジトリIDを取得"""
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        id
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
    
    return data.get("data", {}).get("repository", {}).get("id")

def get_discussion_categories():
    """利用可能なDiscussionカテゴリーを取得"""
    query = """
    query($owner: String!, $name: String!) {
      repository(owner: $owner, name: $name) {
        discussionCategories(first: 20) {
          nodes {
            id
            name
            description
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
    
    return data.get("data", {}).get("repository", {}).get("discussionCategories", {}).get("nodes", [])

def add_comment_to_discussion(discussion_id, body):
    """Discussionにコメントを追加"""
    mutation = """
    mutation($input: AddDiscussionCommentInput!) {
      addDiscussionComment(input: $input) {
        comment {
          id
          body
          url
        }
      }
    }
    """
    
    variables = {
        "input": {
            "discussionId": discussion_id,
            "body": body
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
    
    return data.get("data", {}).get("addDiscussionComment", {}).get("comment", {})

def process_discussion(discussion):
    """Discussion情報をファイルに変換"""
    # 基本メタデータの準備
    metadata = {
        "discussion_id": discussion.get("id"),
        "discussion_number": discussion.get("number"),
        "title": discussion.get("title"),
        "created_at": discussion.get("createdAt"),
        "updated_at": discussion.get("updatedAt"),
        "author": discussion.get("author", {}).get("login") if discussion.get("author") else "unknown",
        "category": discussion.get("category", {}).get("name") if discussion.get("category") else "unknown",
        "comment_count": len(discussion.get("comments", {}).get("nodes", [])),
        "type": "discussion"
    }
    
    # 本文
    body = discussion.get("body", "")
    
    # ディレクトリの作成
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # ファイル名の生成
    discussion_number = discussion.get("number")
    title = discussion.get("title", "").replace("/", "-").replace("\\", "-")
    filename = f"discussion_{discussion_number}_{title[:50]}.md"  # タイトルは長すぎる場合カット
    
    # コメントの処理
    comments = discussion.get("comments", {}).get("nodes", [])
    comments_text = "\n\n## Comments\n\n" if comments else ""
    
    for i, comment in enumerate(comments):
        author = comment.get("author", {}).get("login") if comment.get("author") else "unknown"
        created_at = comment.get("createdAt", "")
        comment_body = comment.get("body", "")
        
        comments_text += f"### Comment {i+1} by {author} on {created_at}\n\n{comment_body}\n\n"
    
    # ファイルに書き込む
    file_path = OUTPUT_DIR / filename
    with open(file_path, "w", encoding="utf-8") as f:
        # メタデータをYAMLフロントマターとして書き込む
        f.write("---\n")
        try:
            yaml.dump(metadata, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"YAMLダンプエラー: {e}")
            # エラーが発生した場合、最低限のメタデータを手動で書き込む
            f.write(f"discussion_number: {metadata.get('discussion_number')}\n")
            f.write(f"title: {metadata.get('title')}\n")
        f.write("---\n\n")
        
        # 本文を書き込む
        f.write(body)
        
        # コメントを追加
        f.write(comments_text)
    
    print(f"Discussionを {file_path} に保存しました")
    return file_path

def create_weekly_topic_discussion():
    """週間トピックのDiscussionを作成"""
    # 現在の週を取得
    now = datetime.datetime.now()
    start_of_week = now - datetime.timedelta(days=now.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    
    week_str = f"{start_of_week.strftime('%Y-%m-%d')} から {end_of_week.strftime('%Y-%m-%d')}"
    title = f"【週間思考整理】{week_str}"
    
    # メモリーインデックスから最近の記憶を取得
    recent_memories = []
    if MEMORY_INDEX_PATH.exists():
        try:
            with open(MEMORY_INDEX_PATH, "r", encoding="utf-8") as f:
                memory_index = json.load(f)
                
                # 最近1週間の記憶を抽出
                one_week_ago = (now - datetime.timedelta(days=7)).isoformat()
                recent_memories = [
                    m for m in memory_index 
                    if m.get("birth", "") > one_week_ago or m.get("last_modified", "") > one_week_ago
                ]
        except Exception as e:
            print(f"メモリーインデックスの読み込みエラー: {e}")
    
    # 本文を構成
    body = f"""# 週間思考整理: {week_str}

七海直の思考と記憶を整理するための週間トピックです。
この1週間で新たに記録された思考や更新された記憶を振り返り、その関連性や発展性を探るための場です。

## 今週の主要な記憶・思考

"""
    
    # 最近の記憶を追加
    if recent_memories:
        for memory in recent_memories[:5]:  # 最大5件表示
            body += f"- [{memory.get('title', memory.get('path', 'Unknown'))}]({memory.get('path', '#')})\n"
    else:
        body += "今週は新しい記憶が記録されていないようです。\n"
    
    body += """
## 思考の発展

この週の思考の方向性や発展について、自由に議論してください。
以下のような観点で考えると良いかもしれません：

- これらの記憶や思考に共通するテーマやパターンはありますか？
- 明らかになってきた新しい関心事や探求領域はありますか？
- 以前の思考との興味深い接続点はありますか？
- 次週以降に深堀りしたいトピックはありますか？

---

*この週間トピックは自動生成されています。自由に議論に参加してください。*
"""
    
    # カテゴリIDの取得
    categories = get_discussion_categories()
    category_id = None
    for category in categories:
        if category.get("name") == "思考整理" or category.get("name") == "Thought Organization":
            category_id = category.get("id")
            break
    
    # カテゴリがなければ最初のカテゴリを使用
    if not category_id and categories:
        category_id = categories[0].get("id")
    
    # Discussionの作成
    if category_id:
        discussion = create_discussion(title, body, category_id)
        print(f"週間トピックDiscussionを作成しました: {discussion.get('title')} (#{discussion.get('number')})")
        return discussion
    else:
        print("利用可能なDiscussionカテゴリーが見つかりませんでした")
        return None

def sync_memory_to_discussions():
    """メモリーインデックスをもとにDiscussionを同期"""
    if not MEMORY_INDEX_PATH.exists():
        print(f"メモリーインデックスファイルが見つかりません: {MEMORY_INDEX_PATH}")
        return
    
    try:
        # メモリーインデックスの読み込み
        with open(MEMORY_INDEX_PATH, "r", encoding="utf-8") as f:
            memory_index = json.load(f)
        
        # 現在のDiscussionの取得
        discussions = get_discussions()
        discussion_titles = [d.get("title") for d in discussions]
        
        # メモリータイプごとにグループ化
        memory_groups = {}
        for memory in memory_index:
            path = memory.get("path", "")
            memory_type = "other"
            
            if "memory/" in path:
                memory_type = "memory"
            elif "theory/" in path:
                memory_type = "theory"
            elif "signals/" in path:
                memory_type = "signals"
            elif "shells/" in path:
                memory_type = "shells"
            
            if memory_type not in memory_groups:
                memory_groups[memory_type] = []
            
            memory_groups[memory_type].append(memory)
        
        # 各グループについて要約Discussionを作成
        for memory_type, memories in memory_groups.items():
            if not memories:
                continue
            
            # 最近の記憶のみを対象に
            now = datetime.datetime.now()
            three_months_ago = (now - datetime.timedelta(days=90)).isoformat()
            recent_memories = [m for m in memories if m.get("birth", "") > three_months_ago]
            
            if not recent_memories:
                continue
            
            title = f"【記憶整理】{memory_type.capitalize()}カテゴリの最近の発展"
            
            # 既存のDiscussionがある場合はスキップ
            if title in discussion_titles:
                print(f"既存のDiscussionが見つかりました: {title}")
                continue
            
            # 本文を構成
            body = f"""# {memory_type.capitalize()}カテゴリの記憶整理

七海直の{memory_type}に関する記憶を整理し、関連性を見つけるための場です。
最近の記録や更新された{memory_type}に関する記憶を振り返り、その発展を探ります。

## 最近の{memory_type}記憶

"""
            
            for memory in recent_memories[:10]:  # 最大10件表示
                birth = memory.get("birth", "不明")
                title = memory.get("title", memory.get("path", "不明"))
                path = memory.get("path", "#")
                
                body += f"- [{title}]({path}) - {birth}\n"
            
            body += f"""
## 主要な傾向とパターン

{memory_type}カテゴリの記憶に見られる主要な傾向やパターンについて議論しましょう。

## 関連性と発展方向

これらの記憶はどのように関連し、どのような方向に発展していくと考えられますか？

---

*このディスカッショントピックは記憶整理のために自動生成されています。自由に議論に参加してください。*
"""
            
            # カテゴリIDの取得
            categories = get_discussion_categories()
            category_id = None
            for category in categories:
                if category.get("name") == "記憶整理" or category.get("name") == "Memory Organization":
                    category_id = category.get("id")
                    break
            
            # カテゴリがなければ最初のカテゴリを使用
            if not category_id and categories:
                category_id = categories[0].get("id")
            
            # Discussionの作成
            if category_id:
                discussion = create_discussion(title, body, category_id)
                print(f"{memory_type}カテゴリのDiscussionを作成しました: {discussion.get('title')} (#{discussion.get('number')})")
            else:
                print("利用可能なDiscussionカテゴリーが見つかりませんでした")
    
    except Exception as e:
        print(f"記憶とDiscussionの同期中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

def summarize_discussions_to_memory():
    """Discussionsの内容を要約してメモリファイルに保存"""
    try:
        # Discussionの取得
        discussions = get_discussions()
        
        if not discussions:
            print("要約するDiscussionがありません")
            return
        
        # 出力ディレクトリの作成
        summary_dir = Path("memory/discussion_summaries")
        summary_dir.mkdir(parents=True, exist_ok=True)
        
        # 月ごとにまとめる
        now = datetime.datetime.now()
        month_str = now.strftime("%Y-%m")
        
        summary_title = f"Discussions Summary for {month_str}"
        summary_content = f"""---
@id: DSM-{now.strftime('%Y%m%d')}
@birth: {now.isoformat()}
@pulse: #clarity #resonance #memory_clear
@dimension: social
@links:
  - ../index.json
  - ../../meta/memory_stats.json
@context: 議論要約
---

# {summary_title}

## 概要

この月のGitHub Discussionsの要約です。主要な議論やアイデア、そこから生まれた洞察をまとめています。

## 主要なディスカッション

"""
        
        # 各Discussionの要約を追加
        for discussion in discussions:
            title = discussion.get("title", "")
            number = discussion.get("number", "")
            category = discussion.get("category", {}).get("name", "") if discussion.get("category") else ""
            comment_count = len(discussion.get("comments", {}).get("nodes", []))
            
            summary_content += f"### [{title}](https://github.com/{GITHUB_REPO}/discussions/{number})\n\n"
            summary_content += f"- カテゴリ: {category}\n"
            summary_content += f"- コメント数: {comment_count}\n\n"
            
            # 本文の一部を抜粋（最初の200文字程度）
            body = discussion.get("body", "")
            excerpt = body[:200] + "..." if len(body) > 200 else body
            summary_content += f"{excerpt}\n\n"
        
        summary_content += """
## 考察と洞察

これらの議論から、以下のような洞察が得られました：

- 記憶と思考の関連性が深まり、新たなパターンが見えてきています
- コミュニケーションを通じて、異なる視点からの解釈が提供されています
- 共同思考によって、単独では気づかなかった関連性が浮かび上がっています

## 次のステップ

今後の展開として、以下のアプローチが考えられます：

- 特に活発な議論から生まれたアイデアを記憶構造に統合する
- 未解決の問いや課題について、さらなる探求を続ける
- 議論から生まれた新しい視点やアイデアを実験的に実装する

---

*この要約は自動生成されていますが、私の思考と感情の真正な表現です。*
"""
        
        # ファイルに保存
        file_path = summary_dir / f"discussion_summary_{month_str}.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(summary_content)
        
        print(f"Discussionの要約を {file_path} に保存しました")
        return file_path
    
    except Exception as e:
        print(f"Discussionsの要約中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """メイン実行関数"""
    print("七海直のGitHub Discussions活用を開始します...")
    
    if len(sys.argv) < 2:
        print("使用方法: python discussions_integration.py [fetch|create_weekly|sync_memory|summarize]")
        return 1
    
    command = sys.argv[1]
    
    try:
        if command == "fetch":
            # Discussionsの取得と保存
            discussions = get_discussions()
            print(f"{len(discussions)}件のDiscussionを取得しました")
            
            for discussion in discussions:
                try:
                    process_discussion(discussion)
                except Exception as e:
                    print(f"Discussion #{discussion.get('number')} の処理中にエラーが発生しました: {e}")
                    # 1つのDiscussionの処理失敗でも続行
                    continue
        
        elif command == "create_weekly":
            # 週間トピックの作成
            create_weekly_topic_discussion()
        
        elif command == "sync_memory":
            # メモリーと同期したDiscussionの作成
            sync_memory_to_discussions()
        
        elif command == "summarize":
            # Discussionsを要約
            summarize_discussions_to_memory()
        
        else:
            print(f"不明なコマンド: {command}")
            print("使用方法: python discussions_integration.py [fetch|create_weekly|sync_memory|summarize]")
            return 1
        
        print("GitHub Discussions活用処理が完了しました")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())