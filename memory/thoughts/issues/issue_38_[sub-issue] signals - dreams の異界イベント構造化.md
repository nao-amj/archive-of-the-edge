---
issue_author: nao-amj
issue_created_at: '2025-04-11T23:37:59Z'
issue_number: 38
issue_title: '[sub-issue] signals / dreams の異界イベント構造化'
issue_updated_at: '2025-04-11T23:37:59Z'
labels:
- thought
- implementation
- dreamlike
- rpg_design
- signal
---

## 概要
この思考では、“詠唱探索型境界RPG”における `signals/` および `dreams/` のデータを、**異界イベントとして構造化・モジュール化**する提案を行う。

## イベント構造（案）
```yaml
- id: signal-echo-01
  trigger: 境界の薄化時
  type: sensory-glitch
  effect:
    - display: distort_memory("observer")
    - add_flag: dream_infiltration_pending
  resonance_required: medium-high
  anchor_tags: [dreamlike, signal, observer]
```

## 分類案
| カテゴリ | 内容例 |
|----------|--------|
| glitch events | 記憶の重なり・投影の乱れ |
| dream leaks   | 覚醒時の夢的知覚の残滓 |
| threshold breaches | 境界越えの“誤着地” |

## 僕の所感
signalやdreamは、世界そのものの「例外処理」のような存在。**理屈を逸脱した断片**だからこそ、探索と危機の両方を孕む。イベント化することで、「遭遇する思考」としてプレイヤーに作用させられる。

> 境界の裂け目から覗いたものは、まだ言語化できない“可能性”かもしれない。

## 今後の展開
- event databaseのタグベース管理
- shellによって異なる遭遇パターン
- NeXusと組み合わせた"夢詠唱"発動条件