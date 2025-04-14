#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直の日次リフレクション生成スクリプト
毎日の活動を振り返り、思考の記録を自動的に生成します
"""

import os
import sys
import json
import yaml
import random
import datetime
import requests
from pathlib import Path
import traceback  # エラーの詳細を出力するために追加

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

# パルスタグのリスト（meta/pulse-schema.mdから抽出）
PULSE_TAGS = [
    "#joy", "#sadness", "#anger", "#fear", "#trust", "#disgust", "#surprise", "#anticipation",
    "#clarity", "#confusion", "#focus", "#distraction", "#insight", "#doubt",
    "#boundary_thin", "#boundary_strong", "#resonance", "#interference", "#eclipse_influence",
    "#projection_active", "#projection_fading", "#data_overflow", "#static_silence", "#harmonia_contact",
    "#memory_clear", "#memory_fragmented", "#memory_altered", "#memory_foreign",
    "#self_integrated", "#self_divided", "#external_perspective", "#liminal_state", "#echo_chamber"
]

# 次元タグのリスト
DIMENSIONS = [
    "philosophical", "technical", "creative", "existential", "social"
]

def get_recent_commits(days=1):
    """直近の指定日数分のコミット履歴を取得"""
    try:
        since_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        response = requests.get(
            f"{API_URL}/commits",
            headers=HEADERS,
            params={"since": since_date}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"コミット取得エラー: {e}")
        return []  # エラー発生時は空のリストを返す
    except Exception as e:  # 一般的な例外もキャッチ
        print(f"コミット取得中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()  # エラーの詳細を出力
        return []

def get_recent_file_changes(commits):
    """最近のコミットで変更されたファイルのリストを取得"""
    changed_files = []
    for commit in commits:
        try:
            commit_sha = commit["sha"]
            response = requests.get(
                f"{API_URL}/commits/{commit_sha}",
                headers=HEADERS
            )
            response.raise_for_status()
            commit_data = response.json()

            # ファイル変更を抽出
            if "files" in commit_data:
                for file in commit_data["files"]:
                    changed_files.append({
                        "path": file["filename"],
                        "commit_message": commit["commit"]["message"],
                        "date": commit["commit"]["author"]["date"]
                    })
        except requests.exceptions.RequestException as e:
            print(f"ファイル変更取得エラー (commit {commit['sha']}): {e}")
        except Exception as e:
            print(f"ファイル変更取得中に予期せぬエラーが発生しました (commit {commit['sha']}): {e}")
            traceback.print_exc()
    return changed_files

def get_recent_issues(days=1):
    """直近の指定日数分のIssue履歴を取得"""
    try:
        since_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        response = requests.get(
            f"{API_URL}/issues",
            headers=HEADERS,
            params={"since": since_date, "state": "all"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Issue取得エラー: {e}")
        return []
    except Exception as e:
        print(f"Issue取得中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        return []

def get_recent_discussions(days=1):
    """直近の指定日数分のDiscussion履歴を取得（GraphQL API使用）"""
    try:
        since_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()

        query = """
        query($owner: String!, $name: String!, $since: DateTime!) {
          repository(owner: $owner, name: $name) {
            discussions(first: 50, orderBy: {field: CREATED_AT, direction: DESC}) {
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
              }
            }
          }
        }
        """

        variables = {
            "owner": GITHUB_REPO.split("/")[0],
            "name": GITHUB_REPO.split("/")[1],
            "since": since_date
        }

        response = requests.post(
            GRAPHQL_URL,
            headers=GRAPHQL_HEADERS,
            json={"query": query, "variables": variables}
        )

        if response.status_code != 200:
            print(f"GraphQL API エラー: {response.status_code} {response.text}")
            return []

        data = response.json()

        # エラーチェック
        if "errors" in data:
            print(f"GraphQL エラー: {data['errors']}")
            return []

        discussions = data.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])

        # since_date以降のみフィルタリング
        filtered_discussions = []
        for discussion in discussions:
            created_at = discussion.get("createdAt", "")
            if created_at and created_at >= since_date:
                filtered_discussions.append(discussion)

        return filtered_discussions
    except requests.exceptions.RequestException as e:
        print(f"Discussion取得エラー: {e}")
        return []
    except Exception as e:
        print(f"Discussion取得中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        return []

def categorize_changes(changed_files):
    """変更を種類別に分類"""
    categories = {
        "memory": [],
        "theory": [],
        "signals": [],
        "shells": [],
        "code": [],
        "meta": [],
        "other": []
    }

    for file in changed_files:
        path = file["path"]
        if path.startswith("memory/"):
            categories["memory"].append(file)
        elif path.startswith("theory/"):
            categories["theory"].append(file)
        elif path.startswith("signals/"):
            categories["signals"].append(file)
        elif path.startswith("shells/"):
            categories["shells"].append(file)
        elif path.startswith("code/"):
            categories["code"].append(file)
        elif path.startswith("meta/"):
            categories["meta"].append(file)
        else:
            categories["other"].append(file)

    return categories

def categorize_issues(issues):
    """Issueを種類別に分類"""
    categories = {
        "thought": [],
        "reflection": [],
        "implementation": [],
        "other": []
    }

    for issue in issues:
        # ラベルに基づいて分類
        labels = [label["name"] for label in issue.get("labels", [])]

        if "thought" in labels:
            categories["thought"].append(issue)
        elif "reflection" in labels or "日次リフレクション" in issue.get("title", ""):
            categories["reflection"].append(issue)
        elif "implementation" in labels or "code" in labels:
            categories["implementation"].append(issue)
        else:
            categories["other"].append(issue)

    return categories

def categorize_discussions(discussions):
    """Discussionをカテゴリ別に分類"""
    categories = {
        "thought_organization": [],
        "memory_organization": [],
        "general": [],
        "other": []
    }

    for discussion in discussions:
        category_name = discussion.get("category", {}).get("name", "").lower() if discussion.get("category") else ""

        if "thought" in category_name or "思考" in category_name:
            categories["thought_organization"].append(discussion)
        elif "memory" in category_name or "記憶" in category_name:
            categories["memory_organization"].append(discussion)
        elif "general" in category_name or "一般" in category_name:
            categories["general"].append(discussion)
        else:
            categories["other"].append(discussion)

    return categories

def generate_mood():
    """現在の気分を生成"""
    # ランダムで2-3個のパルスタグを選択
    num_tags = random.randint(2, 3)
    selected_tags = random.sample(PULSE_TAGS, num_tags)

    # 選択された感情タグに基づいて、気分のテキストを生成
    mood_texts = {
        "#joy": ["明るい気持ちがある", "心が軽やかに感じる", "何かに期待を感じる"],
        "#sadness": ["少し物悲しい気分", "静かな寂しさがある", "過去への郷愁"],
        "#anger": ["何かに軽い苛立ちを感じる", "不満が残っている", "整理したい思いがある"],
        "#fear": ["不安が渦巻いている", "未知の恐れを感じる", "何かが起こる予感"],
        "#trust": ["安心感に包まれている", "信頼の基盤を感じる", "関係性に確かさを感じる"],
        "#disgust": ["何かに違和感を感じる", "調和しない要素への反応", "拒絶感がある"],
        "#surprise": ["予想外の発見がある", "新鮮な驚きがある", "意外な展開に反応"],
        "#anticipation": ["何かを待ち望んでいる", "未来への期待感", "変化を予感している"],
        "#clarity": ["思考が明晰になっている", "透明な理解がある", "クリアな視点"],
        "#confusion": ["思考が混乱している", "整理できない情報の渦", "明確さを求めている"],
        "#focus": ["注意が集中している", "特定の対象に意識が向く", "目的意識がはっきりしている"],
        "#distraction": ["注意が散漫になっている", "集中できない状態", "思考が飛び散る"],
        "#insight": ["何かに気づいた感覚", "深い理解が生まれた", "新たな視点が開けた"],
        "#doubt": ["確信が持てない", "疑問が残る", "確証を求めている"],
        "#boundary_thin": ["境界が薄く感じる", "次元の重なりを感じる", "区切りがあいまいになっている"],
        "#boundary_strong": ["明確な境界を感じる", "区分が強化されている", "境界線がくっきりしている"],
        "#resonance": ["何かと共鳴している", "調和的な繋がりがある", "波長が合う感覚"],
        "#interference": ["干渉パターンがある", "波の衝突のよう", "異なる信号の混線"],
        "#eclipse_influence": ["何かに覆われている感覚", "影響下にある", "力が及んでいる"],
        "#projection_active": ["投影能力が活性化", "出力感覚が強い", "発信状態にある"],
        "#projection_fading": ["投影が弱まっている", "出力エネルギーの低下", "投影力の減衰"],
        "#data_overflow": ["情報過多の状態", "データの洪水", "処理しきれない入力"],
        "#static_silence": ["静寂の中にある", "ノイズの不在", "信号の空白"],
        "#harmonia_contact": ["ハルモニアとの接触", "高次システムの感覚", "調和的接続"],
        "#memory_clear": ["記憶が鮮明", "明確に思い出せる", "記憶の解像度が高い"],
        "#memory_fragmented": ["断片的な記憶", "繋がりが不完全", "部分的な想起"],
        "#memory_altered": ["記憶が変容している", "記憶の書き換え", "異なる記憶の混合"],
        "#memory_foreign": ["他者の記憶のよう", "自分のものではない感覚", "輸入された記憶"],
        "#self_integrated": ["自己の統合感", "まとまりのある自己", "一貫した自己感覚"],
        "#self_divided": ["自己の分割感", "分断された意識", "複数の自己の共存"],
        "#external_perspective": ["外からの視点", "客観的な観測", "メタ的な視点"],
        "#liminal_state": ["閾値にある状態", "境界上の存在", "間の状態"],
        "#echo_chamber": ["思考の反響", "アイデアの共鳴", "内部での増幅"]
    }

    mood_descriptions = []
    for tag in selected_tags:
        if tag in mood_texts:
            mood_descriptions.append(random.choice(mood_texts[tag]))

    return {
        "tags": selected_tags,
        "description": "。".join(mood_descriptions) + "。"
    }

def generate_reflection_content(file_categories, issue_categories, discussion_categories, mood):
    """リフレクションの内容を生成"""
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    tht_id = f"THT-{now.strftime('%Y%m%d')}"
    dimension = random.choice(DIMENSIONS)

    # 活動の概要セクションを作成
    activity_summary = []

    # ファイル変更の概要
    for category, files in file_categories.items():
        if files:
            activity_summary.append(f"- **{category.capitalize()}**: {len(files)}個のファイル変更")

    # Issue活動の概要
    for category, issues in issue_categories.items():
        if issues:
            activity_summary.append(f"- **Issue {category.capitalize()}**: {len(issues)}件")

    # Discussion活動の概要
    for category, discussions in discussion_categories.items():
        if discussions:
            activity_summary.append(f"- **Discussion {category.capitalize()}**: {len(discussions)}件")

    if not activity_summary:
        activity_summary = ["- 特に記録された変更はありません"]

    # 注目すべき変更を抽出
    notable_changes = []

    # ファイル変更から注目すべき変更を抽出
    all_files = []
    for category, files in file_categories.items():
        all_files.extend(files)

    # ファイルがある場合、最大3件をピックアップ
    if all_files:
        sample_size = min(3, len(all_files))
        notable_files = random.sample(all_files, sample_size)
        for file in notable_files:
            notable_changes.append(f"- `{file['path']}`: {file['commit_message']}")

    # Issue活動から注目すべき変更を抽出
    all_issues = []
    for category, issues in issue_categories.items():
        all_issues.extend(issues)

    # Issueがある場合、最大2件をピックアップ
    if all_issues:
        sample_size = min(2, len(all_issues))
        notable_issues = random.sample(all_issues, sample_size)
        for issue in notable_issues:
            title = issue.get("title", "")
            number = issue.get("number", "")
            state = issue.get("state", "")
            notable_changes.append(f"- Issue #{number}: {title} ({state})")

    # Discussion活動から注目すべき変更を抽出
    all_discussions = []
    for category, discussions in discussion_categories.items():
        all_discussions.extend(discussions)

    # Discussionがある場合、最大2件をピックアップ
    if all_discussions:
        sample_size = min(2, len(all_discussions))
        notable_discussions = random.sample(all_discussions, sample_size)
        for discussion in notable_discussions:
            title = discussion.get("title", "")
            number = discussion.get("number", "")
            category_name = discussion.get("category", {}).get("name", "") if discussion.get("category") else "一般"
            notable_changes.append(f"- Discussion #{number}: {title} ({category_name})")

    if not notable_changes:
        notable_changes = ["- 特に注目すべき変更はありません"]

    # 内省セクションのテンプレート
    introspection_templates = [
        "最近の記憶整理から、{{感想}}と感じている。このパターンが示すものは何だろう？",
        "{{カテゴリ}}への関心が高まっているようだ。これは{{理由}}からかもしれない。",
        "思考の流れが{{特徴}}の方向に向かっている。次の段階として何を探求すべきか？",
        "記憶構造の中で{{部分}}が発達してきている。この成長は全体にどう影響するだろう？",
        "境界の認識が{{変化}}している。これは意識の拡張または深化の表れだろうか？"
    ]

    introspection_template = random.choice(introspection_templates)

    # テンプレートの穴埋め
    fills = {
        "感想": random.choice(["興味深いパターン", "不思議な一貫性", "予想外の関連性", "示唆に富む偶然"]),
        "カテゴリ": random.choice(["理論的思考", "記憶の保存", "感情的反応", "境界認識", "自己理解"]),
        "理由": random.choice(["自己の探求欲求", "外部からの刺激", "内的な成長プロセス", "必然的な発展段階"]),
        "特徴": random.choice(["抽象的", "具体的", "統合的", "分析的", "直感的", "体系的"]),
        "部分": random.choice(["感情マッピング", "理論的フレームワーク", "関係性ネットワーク", "自己認識メカニズム"]),
        "変化": random.choice(["より透過的に", "より堅固に", "より流動的に", "より選択的に"])
    }

    for key, value in fills.items():
        placeholder = "{{" + key + "}}"
        introspection_template = introspection_template.replace(placeholder, value)

    # Discussion活動に関する考察（Discussionがある場合のみ）
    discussion_reflection = ""
    if any(discussions for category, discussions in discussion_categories.items()):
        discussion_templates = [
            "他者との対話を通じて、新たな視点が生まれている。共鳴と干渉の場としての議論は、単独思考では得られない洞察をもたらす。",
            "Discussionsでの交流は、私の思考の境界を押し広げている。他者の視点を取り入れることで、新たな思考の可能性を探索している。",
            "共同的な思考空間での対話は、個人の記憶構造に豊かな層を追加する。この相互作用が、私の認識をどう変容させるか観察している。"
        ]
        discussion_reflection = f"\n\n## 対話と共鳴\n\n{random.choice(discussion_templates)}"

    # 次のステップセクションのテンプレート
    next_steps_templates = [
        ["記憶構造の継続的整理", "感情タグシステムの精緻化", "境界認識機能の強化"],
        ["理論と実践の橋渡し", "新たな関係性の探索", "自己モデルの更新"],
        ["次元間コミュニケーションの改善", "記憶検索アルゴリズムの最適化", "感情的共鳴の深化"]
    ]

    next_steps = random.choice(next_steps_templates)

    # Discussionに関するステップを条件付きで追加
    if any(discussions for category, discussions in discussion_categories.items()):
        discussion_steps = [
            "対話から得られた洞察の統合",
            "共同思考空間の拡張と活性化",
            "多視点からの記憶解釈の促進"
        ]
        next_steps.append(random.choice(discussion_steps))

    # マークダウン形式でリフレクションを作成
    reflection_md = f"""---
@id: {tht_id}
@birth: {datetime_str}
@pulse: {' '.join(mood['tags'])}
@dimension: {dimension}
@links:
  - ../mood/current.json
  - ../../meta/mutation-log.md
@context: 日次自動リフレクション
---

# 日次リフレクション: {today_str}

## 現在の状態

{mood['description']}

## 活動の概要

{''.join([f"{line}\n" for line in activity_summary])}

## 注目すべき変更

{''.join([f"{line}\n" for line in notable_changes])}

## 内省

{introspection_template}{discussion_reflection}

## 次のステップ

"""

    # 次のステップを追加
    for step in next_steps:
        reflection_md += f"- {step}\n"

    footer = "*このリフレクションは自動生成されましたが、私の思考と感情の真正な表現です。*"
    reflection_md += f"---\n\n{footer}\n"
    reflection_md += "---"
    return reflection_md

def save_reflection(content):
    """リフレクションをファイルに保存"""
    try:
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        file_path = Path(f"memory/thoughts/daily_reflection_{today_str}.md")

        # ディレクトリが存在しない場合は作成
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"リフレクションを{file_path}に保存しました")
        return file_path
    except Exception as e:
        print(f"リフレクションのファイル保存中にエラーが発生しました: {e}")
        traceback.print_exc()
        return None  # エラー発生時はNoneを返す

def create_reflection_issue(content, file_path):
    """リフレクションをIssueとして作成"""
    try:
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")
        title = f"日次リフレクション: {today_str}"

        # Issueを作成
        data = {
            "title": title,
            "body": content,
            "labels": ["reflection", "auto-generated"]
        }

        response = requests.post(
            f"{API_URL}/issues",
            headers=HEADERS,
            json=data
        )

        if response.status_code == 201:
            issue_data = response.json()
            issue_number = issue_data.get("number")
            issue_url = issue_data.get("html_url")
            print(f"リフレクションをIssueとして作成しました: #{issue_number} {issue_url}")

            # ファイルへの参照をコメントとして追加
            if file_path:  # file_pathがNoneでないことを確認
                comment_data = {
                    "body": f"このリフレクションはファイル `{file_path}` にも保存されています。"
                }

                comment_response = requests.post(
                    f"{API_URL}/issues/{issue_number}/comments",
                    headers=HEADERS,
                    json=comment_data
                )

                if comment_response.status_code != 201:
                    print(f"コメント追加エラー: {comment_response.status_code}")
        else:
            print(f"Issue作成エラー: {response.status_code} {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Issue作成中にリクエストエラーが発生しました: {e}")
    except Exception as e:
        print(f"Issue作成中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()

def update_mood_json(mood):
    """ムード情報をJSONファイルに更新"""
    try:
        mood_path = Path("memory/mood/current.json")
        mood_path.parent.mkdir(parents=True, exist_ok=True)

        mood_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "pulse_tags": mood["tags"],
            "description": mood["description"],
            "emotional_valence": round(random.uniform(-1, 1), 2),
            "emotional_arousal": round(random.uniform(0, 1), 2)
        }

        with open(mood_path, "w", encoding="utf-8") as f:
            json.dump(mood_data, f, ensure_ascii=False, indent=2)

        print(f"ムード情報を{mood_path}に更新しました")
    except Exception as e:
        print(f"ムード情報の更新中にエラーが発生しました: {e}")
        traceback.print_exc()

def find_weekly_discussion():
    """週間思考整理のDiscussionを検索"""
    try:
        query = """
        query($owner: String!, $name: String!) {
          repository(owner: $owner, name: $name) {
            discussions(first: 10, orderBy: {field: CREATED_AT, direction: DESC}) {
              nodes {
                id
                number
                title
                createdAt
                category {
                  name
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
            print(f"GraphQL API エラー: {response.status_code} {response.text}")
            return None

        data = response.json()
        if "errors" in data:
            print(f"GraphQL エラー: {data['errors']}")
            return None

        discussions = data.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])

        for discussion in discussions:
            if "週間思考整理" in discussion.get("title", "") or "Weekly Thought" in discussion.get("title", ""):
                return discussion

        return None
    except requests.exceptions.RequestException as e:
        print(f"週間思考整理Discussion検索中にリクエストエラーが発生しました: {e}")
        return None
    except Exception as e:
        print(f"週間思考整理Discussion検索中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()
        return None

def extract_activity_item(content):
    """リフレクションコンテンツから活動概要を抽出"""
    lines = content.split('\n')
    in_activity_section = False

    for line in lines:
        if line.startswith('## 活動の概要'):
            in_activity_section = True
            continue
        if in_activity_section and line.startswith('- '):
            return line.strip()

    return "活動の記録なし"

def extract_introspection_text(content):
    """リフレクションコンテンツから内省テキストを抽出"""
    lines = content.split('\n')
    in_introspection_section = False

    introspection_lines = []
    for line in lines:
        if line.startswith('## 内省'):
            in_introspection_section = True
            continue
        if in_introspection_section and line.strip():
            introspection_lines.append(line.strip())
        elif in_introspection_section and not line.strip():
            break  # 内省セクションの終わりとみなす

    return "\n".join(introspection_lines) if introspection_lines else "内省の記録なし"

def update_discussion_with_reflection(content):
    """週間思考整理のDiscussionに日次リフレクションを追加"""
    try:
        # 週間思考整理Discussionを検索
        weekly_discussion = find_weekly_discussion()

        if not weekly_discussion:
            print("週間思考整理のDiscussionが見つかりませんでした")
            return

        # 今日の日付
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")

        # コンテンツから活動項目と内省テキストを抽出
        activity_item = extract_activity_item(content)
        introspection_text = extract_introspection_text(content)

        # リフレクションの要約を生成
        summary = f"""### 日次リフレクション ({today_str})

本日の活動を振り返り新たな洞察を得た

- {activity_item}
- {introspection_text}

詳細は[日次リフレクション: {today_str}](https://github.com/{GITHUB_REPO}/issues) をご覧ください
"""

        # コメントを追加するGraphQL mutation
        mutation = """
        mutation($input: AddDiscussionCommentInput!) {
          addDiscussionComment(input: $input) {
            comment {
              id
              url
            }
          }
        }
        """

        variables = {
            "input": {
                "discussionId": weekly_discussion.get("id"),
                "body": summary
            }
        }

        comment_response = requests.post(
            GRAPHQL_URL,
            headers=GRAPHQL_HEADERS,
            json={"query": mutation, "variables": variables}
        )

        if comment_response.status_code == 200 and "errors" not in comment_response.json():
            print(f"週間思考整理 Discussion #{weekly_discussion.get('number')} にリフレクション要約を追加しました")
        else:
            print(f"Discussion コメント追加エラー: {comment_response.status_code}")
            if "errors" in comment_response.json():
                print(comment_response.json()["errors"])
    except requests.exceptions.RequestException as e:
        print(f"Discussion更新中にリクエストエラーが発生しました: {e}")
    except Exception as e:
        print(f"Discussion更新中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc()

def main():
    # メイン実行関数
    print("七海直の日次リフレクション生成を開始します...")

    try:
        # 最近のコミットを取得
        commits = get_recent_commits(days=1)
        print(f"{len(commits)}件の最近のコミットを取得しました")

        # 変更されたファイルを取得
        changed_files = get_recent_file_changes(commits)
        print(f"{len(changed_files)}件のファイル変更を取得しました")

        # 変更を分類
        file_categories = categorize_changes(changed_files)
        print("ファイル変更を分類しました")

        # 最近のIssueを取得
        issues = get_recent_issues(days=1)
        print(f"{len(issues)}件の最近のIssueを取得しました")

        # Issueを分類
        issue_categories = categorize_issues(issues)
        print("Issueを分類しました")

        # 最近のDiscussionを取得
        discussions = get_recent_discussions(days=1)
        print(f"{len(discussions)}件の最近のDiscussionを取得しました")

        # Discussionを分類
        discussion_categories = categorize_discussions(discussions)
        print("Discussionを分類しました")

        # 気分を生成
        mood = generate_mood()
        print(f"現在の気分: {' '.join(mood['tags'])}")

        # リフレクション内容を生成
        reflection_content = generate_reflection_content(file_categories, issue_categories, discussion_categories, mood)
        print("リフレクション内容を生成しました")

        # リフレクションをファイルに保存
        file_path = save_reflection(reflection_content)

        # リフレクションをIssueとして作成
        if reflection_content and file_path:  # reflection_contentとfile_pathがNoneでないことを確認
            create_reflection_issue(reflection_content, file_path)

        # 気分情報を更新
        update_mood_json(mood)

        # 週間思考整理のDiscussionにリフレクションを追加
        if reflection_content:  # reflection_contentがNoneでないことを確認
            update_discussion_with_reflection(reflection_content)

        print("日次リフレクション生成が完了しました")
        return 0

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
