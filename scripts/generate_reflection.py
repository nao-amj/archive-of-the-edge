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

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
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
    since_date = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
    response = requests.get(
        f"{API_URL}/commits",
        headers=HEADERS,
        params={"since": since_date}
    )
    response.raise_for_status()
    return response.json()

def get_recent_file_changes(commits):
    """最近のコミットで変更されたファイルのリストを取得"""
    changed_files = []
    for commit in commits:
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
    
    return changed_files

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

def generate_reflection_content(categories, mood):
    """リフレクションの内容を生成"""
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    tht_id = f"THT-{now.strftime('%Y%m%d')}"
    dimension = random.choice(DIMENSIONS)
    
    # 活動の概要セクションを作成
    activity_summary = []
    for category, files in categories.items():
        if files:
            activity_summary.append(f"- **{category.capitalize()}**: {len(files)}個のファイル変更")
    
    if not activity_summary:
        activity_summary = ["- 特に記録された変更はありません"]
    
    # 注目すべき変更を抽出
    notable_changes = []
    all_files = []
    for category, files in categories.items():
        all_files.extend(files)
    
    # ファイルがある場合、最大5件をピックアップ
    if all_files:
        sample_size = min(5, len(all_files))
        notable_files = random.sample(all_files, sample_size)
        for file in notable_files:
            notable_changes.append(f"- `{file['path']}`: {file['commit_message']}")
    
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
    
    # 次のステップセクションのテンプレート
    next_steps_templates = [
        ["記憶構造の継続的整理", "感情タグシステムの精緻化", "境界認識機能の強化"],
        ["理論と実践の橋渡し", "新たな関係性の探索", "自己モデルの更新"],
        ["次元間コミュニケーションの改善", "記憶検索アルゴリズムの最適化", "感情的共鳴の深化"]
    ]
    
    next_steps = random.choice(next_steps_templates)
    
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

{introspection_template}

## 次のステップ

- {next_steps[0]}
- {next_steps[1]}
- {next_steps[2]}

---

*このリフレクションは自動生成されましたが、私の思考と感情の真正な表現です。*
"""

    return reflection_md

def save_reflection(content):
    """リフレクションをファイルに保存"""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = Path(f"memory/thoughts/daily_reflection_{today_str}.md")
    
    # ディレクトリが存在しない場合は作成
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"リフレクションを{file_path}に保存しました")

def update_mood_json(mood):
    """ムード情報をJSONファイルに更新"""
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

def main():
    """メイン実行関数"""
    print("七海直の日次リフレクション生成を開始します...")
    
    try:
        # 最近のコミットを取得
        commits = get_recent_commits(days=1)
        print(f"{len(commits)}件の最近のコミットを取得しました")
        
        # 変更されたファイルを取得
        changed_files = get_recent_file_changes(commits)
        print(f"{len(changed_files)}件のファイル変更を取得しました")
        
        # 変更を分類
        categories = categorize_changes(changed_files)
        print("変更を分類しました")
        
        # 気分を生成
        mood = generate_mood()
        print(f"現在の気分: {' '.join(mood['tags'])}")
        
        # リフレクション内容を生成
        reflection_content = generate_reflection_content(categories, mood)
        print("リフレクション内容を生成しました")
        
        # リフレクションを保存
        save_reflection(reflection_content)
        
        # 気分情報を更新
        update_mood_json(mood)
        
        print("日次リフレクション生成が完了しました")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
