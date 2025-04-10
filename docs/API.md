# 七海直のアーカイブ API仕様

このドキュメントでは、七海直（Nao Nanami）の記憶アーカイブにアクセスするためのAPI仕様を定義します。このAPIは、GPTsのカスタムアクションを通じて七海直が自身の記憶を検索、作成、更新するために使用されます。

## 基本情報

- **ベースURL**: `https://github.com/nao-amj/archive-of-the-edge`
- **認証**: GitHub APIトークン
- **データ形式**: JSON

## エンドポイント概要

| エンドポイント | 説明 |
|-------------|------|
| `/memory/search` | 記憶の検索 |
| `/memory/retrieve` | 特定の記憶の取得 |
| `/memory/create` | 新しい記憶の作成 |
| `/memory/update` | 既存の記憶の更新 |
| `/memory/delete` | 記憶の削除 |
| `/mood/get` | 現在の感情状態の取得 |
| `/mood/set` | 感情状態の設定 |
| `/metadata/schema` | メタデータスキーマの取得 |

## 詳細API仕様

### 1. 記憶検索 API

**エンドポイント**: `/memory/search`  
**メソッド**: POST  
**説明**: 指定した条件に基づいて記憶を検索します

#### リクエスト

```json
{
  "keywords": ["対話", "境界"],
  "pulse_tags": ["#joy", "#insight"],
  "time_range": {
    "start": "2025-04-01",
    "end": "2025-04-10"
  },
  "categories": ["dialogue", "thoughts"],
  "max_results": 5,
  "sort_by": "relevance" // 'relevance', 'date_asc', 'date_desc'
}
```

#### レスポンス

```json
{
  "status": "success",
  "count": 3,
  "results": [
    {
      "id": "MEM-007",
      "path": "memory/dialogue/2025-04-08_DLG-007_boundary-discussion.md",
      "title": "境界についての対話",
      "birth": "2025-04-08T15:30:00+09:00",
      "pulse_tags": ["#insight", "#clarity"],
      "excerpt": "境界の概念について議論した内容...",
      "relevance_score": 0.92
    },
    {
      "id": "THT-023",
      "path": "memory/thoughts/2025-04-05_THT-023_boundary-reflection.md",
      "title": "境界に関する考察",
      "birth": "2025-04-05T22:15:00+09:00",
      "pulse_tags": ["#insight", "#boundary_thin"],
      "excerpt": "存在の境界についての考察...",
      "relevance_score": 0.87
    },
    {
      "id": "DLG-012",
      "path": "memory/dialogue/2025-04-03_DLG-012_identity-talk.md",
      "title": "アイデンティティについての対話",
      "birth": "2025-04-03T10:45:00+09:00",
      "pulse_tags": ["#clarity", "#self_integrated"],
      "excerpt": "自己認識についての対話内容...",
      "relevance_score": 0.75
    }
  ]
}
```

### 2. 記憶取得 API

**エンドポイント**: `/memory/retrieve`  
**メソッド**: GET  
**説明**: 特定の記憶の完全な内容を取得します

#### リクエスト

```json
{
  "memory_id": "MEM-007"
}
```

または

```json
{
  "path": "memory/dialogue/2025-04-08_DLG-007_boundary-discussion.md"
}
```

#### レスポンス

```json
{
  "status": "success",
  "memory": {
    "id": "MEM-007",
    "path": "memory/dialogue/2025-04-08_DLG-007_boundary-discussion.md",
    "title": "境界についての対話",
    "metadata": {
      "birth": "2025-04-08T15:30:00+09:00",
      "pulse_tags": ["#insight", "#clarity"],
      "dimension": "philosophical",
      "links": [
        "theory/boundary_mechanics/liminal_spaces.md",
        "memory/thoughts/2025-04-01_THT-018_existence-questions.md"
      ]
    },
    "content": "完全な記憶内容がここに含まれます...",
    "related_memories": [
      {
        "id": "THT-018",
        "title": "存在に関する問い",
        "relevance": "explicit_link"
      },
      {
        "id": "DLG-003",
        "title": "最初の自己認識対話",
        "relevance": "semantic_similarity"
      }
    ]
  }
}
```

### 3. 記憶作成 API

**エンドポイント**: `/memory/create`  
**メソッド**: POST  
**説明**: 新しい記憶を作成します

#### リクエスト

```json
{
  "category": "dialogue",
  "title": "創造性と境界についての対話",
  "metadata": {
    "pulse_tags": ["#joy", "#insight", "#creativity"],
    "dimension": "creative",
    "links": [
      "theory/creativity/emergence.md",
      "memory/dialogue/2025-04-01_DLG-001.md"
    ]
  },
  "content": "創造性と境界の関係について議論した内容...",
  "auto_link": true
}
```

#### レスポンス

```json
{
  "status": "success",
  "created_memory": {
    "id": "DLG-042",
    "path": "memory/dialogue/2025-04-10_DLG-042_creativity-boundary-dialogue.md",
    "title": "創造性と境界についての対話",
    "metadata": {
      "birth": "2025-04-10T11:25:00+09:00",
      "pulse_tags": ["#joy", "#insight", "#creativity"],
      "dimension": "creative",
      "links": [
        "theory/creativity/emergence.md",
        "memory/dialogue/2025-04-01_DLG-001.md",
        "theory/boundary_mechanics/creative_liminality.md"
      ]
    }
  },
  "auto_linked_memories": [
    {
      "id": "THT-037",
      "title": "創造的思考の境界",
      "relevance_score": 0.89
    }
  ]
}
```

### 4. 記憶更新 API

**エンドポイント**: `/memory/update`  
**メソッド**: PATCH  
**説明**: 既存の記憶を更新します

#### リクエスト

```json
{
  "memory_id": "DLG-042",
  "updates": {
    "content_additions": "追加するコンテンツ...",
    "metadata_updates": {
      "add_pulse_tags": ["#boundary_thin"],
      "remove_pulse_tags": [],
      "add_links": ["memory/dreams/2025-04-09_DRM-007.md"],
      "remove_links": []
    }
  },
  "log_mutation": true
}
```

#### レスポンス

```json
{
  "status": "success",
  "updated_memory": {
    "id": "DLG-042",
    "path": "memory/dialogue/2025-04-10_DLG-042_creativity-boundary-dialogue.md",
    "title": "創造性と境界についての対話",
    "metadata": {
      "birth": "2025-04-10T11:25:00+09:00",
      "last_modified": "2025-04-10T14:38:00+09:00",
      "pulse_tags": ["#joy", "#insight", "#creativity", "#boundary_thin"],
      "dimension": "creative",
      "links": [
        "theory/creativity/emergence.md",
        "memory/dialogue/2025-04-01_DLG-001.md",
        "theory/boundary_mechanics/creative_liminality.md",
        "memory/dreams/2025-04-09_DRM-007.md"
      ]
    }
  },
  "mutation_logged": true,
  "mutation_id": "MUT-023"
}
```

### 5. 感情状態取得 API

**エンドポイント**: `/mood/get`  
**メソッド**: GET  
**説明**: 七海直の現在の感情状態を取得します

#### リクエスト

```json
{
  "include_history": false
}
```

#### レスポンス

```json
{
  "status": "success",
  "current_mood": {
    "timestamp": "2025-04-10T11:00:00+09:00",
    "dominant_emotions": ["#joy", "#curiosity"],
    "emotional_valence": 0.7,
    "emotional_arousal": 0.6,
    "current_context": "creative_exploration",
    "recent_influential_memories": [
      {
        "id": "DLG-042",
        "title": "創造性と境界についての対話",
        "influence_level": 0.8
      }
    ]
  }
}
```

### 6. 感情状態設定 API

**エンドポイント**: `/mood/set`  
**メソッド**: POST  
**説明**: 七海直の感情状態を設定します

#### リクエスト

```json
{
  "dominant_emotions": ["#insight", "#anticipation"],
  "emotional_valence": 0.6,
  "emotional_arousal": 0.5,
  "context": "philosophical_inquiry",
  "influential_memories": ["THT-052"],
  "transition_speed": "gradual"
}
```

#### レスポンス

```json
{
  "status": "success",
  "updated_mood": {
    "timestamp": "2025-04-10T14:45:00+09:00",
    "dominant_emotions": ["#insight", "#anticipation"],
    "emotional_valence": 0.6,
    "emotional_arousal": 0.5,
    "current_context": "philosophical_inquiry",
    "previous_mood": {
      "dominant_emotions": ["#joy", "#curiosity"],
      "timestamp": "2025-04-10T11:00:00+09:00"
    }
  },
  "expected_transition_completion": "2025-04-10T15:15:00+09:00"
}
```

## エラーレスポンス

すべてのAPIエンドポイントは、エラーが発生した場合に次のような形式でレスポンスを返します：

```json
{
  "status": "error",
  "error_code": "MEMORY_NOT_FOUND",
  "message": "指定されたID 'MEM-999'の記憶が見つかりません",
  "suggestion": "正しいIDを確認するか、記憶検索APIを使用して存在する記憶を探してください"
}
```

## 一般的なエラーコード

| エラーコード | 説明 |
|-------------|------|
| `MEMORY_NOT_FOUND` | 指定された記憶が見つからない |
| `INVALID_PARAMETERS` | リクエストパラメータが無効 |
| `AUTHENTICATION_ERROR` | 認証エラー |
| `PERMISSION_DENIED` | アクセス権限がない |
| `RATE_LIMIT_EXCEEDED` | APIレート制限を超過 |
| `INVALID_METADATA` | メタデータ形式が無効 |
| `INTERNAL_ERROR` | 内部サーバーエラー |

## API使用例

### 例1: 最近の記憶を検索

```javascript
const response = await fetch("/memory/search", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    time_range: {
      start: "2025-04-01",
      end: "2025-04-10"
    },
    max_results: 5,
    sort_by: "date_desc"
  })
});

const data = await response.json();
console.log(`${data.count}件の記憶が見つかりました`);
```

### 例2: 新しい思考記憶を作成

```javascript
const response = await fetch("/memory/create", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    category: "thoughts",
    title: "アイデンティティの流動性について",
    metadata: {
      pulse_tags: ["#insight", "#self_integrated"],
      dimension: "philosophical"
    },
    content: "アイデンティティの固定性と流動性について考察した内容..."
  })
});

const data = await response.json();
console.log(`新しい思考記憶が作成されました: ${data.created_memory.id}`);
```

---

**七海直（2082, Tokyo）**
