---
issue_author: nao-amj
issue_created_at: '2025-04-11T23:36:31Z'
issue_number: 36
issue_title: '[sub-issue] 詠唱テンプレート構文の初期設計（NeXus戦術詠唱）'
issue_updated_at: '2025-04-11T23:36:31Z'
labels:
- thought
- implementation
- shells
- rpg_design
- code
---

## 概要
このIssueでは「詠唱探索型境界RPG」におけるNeXus詠唱バトルを支える**詠唱テンプレート構文**の初期構造を設計する。

## 詠唱の構造（案）
```nexus
@invoke battle
@emotion pulse="resonance"
@sync shell="observer"

spell("boundary fracture") {
    target: "information-layer.core",
    method: rewrite(
        pattern: "denial",
        with: "recursive_self"
    )
}
```

## 要素分解
- `@invoke`：詠唱の目的（例：`battle`, `observe`, `dreamshift`）
- `@emotion`：現在の@pulse（感情）と同調状態
- `@sync`：どのshellで詠唱しているか（人格の影響）
- `spell{}`：詠唱本体、NeXus構文で指定された対象・方法・意図

## 次の展開
- 各shellごとの得意な詠唱カテゴリ（戦術分類）
- 詠唱失敗や過負荷時のエラーハンドリング
- pulse値によるリアルタイム詠唱成功率のシミュレーション