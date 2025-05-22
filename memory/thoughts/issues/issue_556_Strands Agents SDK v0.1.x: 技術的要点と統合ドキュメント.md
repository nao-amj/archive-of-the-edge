---
issue_author: nao-amj
issue_created_at: '2025-05-22T05:07:34Z'
issue_number: 556
issue_title: 'Strands Agents SDK v0.1.x: 技術的要点と統合ドキュメント'
issue_updated_at: '2025-05-22T05:07:34Z'
labels:
- Strands
- tech-note
- agent-sdk
---

## Strands Agents SDK v0.1.x

以下は、https://strandsagents.com/0.1.x/ の主要ドキュメントを統合・技術者向けに再構成したもの。


### 🔄 Agent Loop の構造

```
[User Input + Context]
       ↓
  Language Model
       ↓
[Tool 呼び出し（任意）]
       ↓
 Tool 実行結果評価
       ↓
    応答生成 / ループ継続
```

- Tool 使用は LLM により選択されるか、コードから直接呼び出し可能。


### 📜 Prompt Management
- System Prompt: 役割定義、制約条件
- User Prompt: 入力命令
- Tool Calling Prompt: tool呼び出しに変換されたLLMメッセージ
- Model Prompt: 各段階で構築される composite prompt


### 🛠 Tool System 概要
- `@tool` デコレータで Python 関数をツール化。
- tool 呼び出しは `language-based`（LLMが選択）か `direct-call`（コードから）で可能。

```python
from strands import tool

@tool
def add(x: int, y: int) -> int:
    return x + y
```


この Issue は、なお専用の開発向け技術リファレンスとして記録されたもの。一般投稿には不適。

> Threadsへの投稿はこの内容を一般向けに再編集した形で行う。