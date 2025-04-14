#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
七海直の日次リフレクション生成スクリプト (簡易版)
毎日の活動を振り返り、思考の記録を自動的に生成します
"""

import os
import sys
import json
import random
import datetime
from pathlib import Path
import requests

# GitHub APIの設定
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "nao-amj/archive-of-the-edge"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}"

# パルスタグと次元タグのリスト
PULSE_TAGS = ["#joy", "#clarity", "#focus", "#boundary_thin", "#memory_clear"]
DIMENSIONS = ["philosophical", "technical", "creative", "existential", "social"]

def generate_mood():
    """現在の気分を生成"""
    num_tags = random.randint(2, 3)
    selected_tags = random.sample(PULSE_TAGS, num_tags)
    mood_descriptions = ["思考が明晰になっている", "心が軽やかに感じる"]
    
    return {
        "tags": selected_tags,
        "description": "。".join(mood_descriptions) + "。"
    }

def generate_reflection_content(mood):
    """リフレクションの内容を生成"""
    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%dT%H:%M:%S+09:00")
    tht_id = f"THT-{now.strftime('%Y%m%d')}"
    dimension = random.choice(DIMENSIONS)
    
    # マークダウン形式でリフレクションを作成
    reflection_md = f"""---
@id: {tht_id}
@birth: {datetime_str}
@pulse: {' '.join(mood['tags'])}
@dimension: {dimension}
@links:
  - ../mood/current.json
@context: 日次自動リフレクション
---

# 日次リフレクション: {today_str}

## 現在の状態

{mood['description']}

## 活動の概要

- **生成AI**: スクリプト修正作業
- **リポジトリ**: コード整理

## 注目すべき変更

- スクリプトのバグ修正
- 処理の効率化

## 内省

思考の流れが統合的の方向に向かっている。次の段階として何を探求すべきか？

## 次のステップ

- 記憶構造の継続的整理
- 感情タグシステムの精緻化
- 境界認識機能の強化

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
    return file_path

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
    print("七海直の日次リフレクション生成を開始します (簡易版)...")
    
    try:
        # 気分を生成
        mood = generate_mood()
        print(f"現在の気分: {' '.join(mood['tags'])}")
        
        # リフレクション内容を生成
        reflection_content = generate_reflection_content(mood)
        print("リフレクション内容を生成しました")
        
        # リフレクションをファイルに保存
        file_path = save_reflection(reflection_content)
        
        # 気分情報を更新
        update_mood_json(mood)
        
        print("日次リフレクション生成が完了しました")
        return 0
    
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())