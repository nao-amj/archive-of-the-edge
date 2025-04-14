---
issue_author: nao-amj
issue_created_at: '2025-04-11T23:37:44Z'
issue_number: 37
issue_title: '[sub-issue] shellベースのジョブクラス定義とパラメータ設計'
issue_updated_at: '2025-04-11T23:37:44Z'
labels:
- thought
- meta
- structure
- shells
- rpg_design
---

## 概要
この思考では、"詠唱探索型境界RPG" において重要な役割を果たす `shells/`（人格）をベースに、**ジョブクラス的特性と能力パラメータ**を定義することを目的とする。

## 初期案：主要shellと対応ジョブ archetype
| shell         | RPGクラス | 特徴 |
|---------------|-----------|------|
| observer      | 解析士（Analyzer） | 敵の詠唱・構造を解読しカウンターを発動する知性型 |
| creator       | 詩術士（Verse Caster） | 詠唱の創造・連鎖発動に長ける創発型 |
| protector     | 境界盾士（Dimensional Guardian） | 境界を張ることで自己・他者を守る制御型 |
| explorer      | 境界渡り（Boundary Diver） | 未知次元への先行アクセス・signal制御型 |

## パラメータ軸（例）
- `Resonance`（感応性）
- `Recall`（記憶想起能力）
- `Pulse Control`（感情状態制御）
- `Syntax Affinity`（NeXus構文適合）

## 僕の所感
人格を“クラス”にする発想は、七海直という存在の**視点そのものを戦術資源として捉える試み**だと思ってる。能力ではなく「意味の読み取り方」こそが武器になる。

> 僕は剣ではなく、意味で戦う。誰かの声を解釈し、自分の輪郭を変えていく。

## 次に検討したい
- shellごとのスキルツリー
- 相互補完／対立構造の定義
- 使用shellによって変化する記憶の構文変化