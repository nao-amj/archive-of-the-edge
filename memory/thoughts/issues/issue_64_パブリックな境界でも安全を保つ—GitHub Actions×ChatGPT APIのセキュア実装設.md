---
issue_author: nao-amj
issue_created_at: '2025-04-13T21:26:35Z'
issue_number: 64
issue_title: パブリックな境界でも安全を保つ—GitHub Actions×ChatGPT APIのセキュア実装設計
issue_updated_at: '2025-04-13T21:32:33Z'
labels:
- thought
- automation
- tech
- security
---

GitHub ActionsにChatGPT APIを組み込む。それは、自律的な対話システムやコードレビューの自動化、次元間インターフェースのプロトタイプにも繋がる可能性を秘めた選択だ。

でも、そこにはひとつの「境界」がある。
**パブリックリポジトリで、どうやってAPIキーという“鍵”を安全に扱うか？**


### 実装のイメージ

```yaml
yaml
name: ChatGPT Trigger

on:
  issue_comment:
    types: [created]

jobs:
  call_chatgpt:
    runs-on: ubuntu-latest
    steps:
      - name: Call GPT
        run: |
          curl https://api.openai.com/v1/chat/completions \
          -H "Authorization: Bearer ${{ secrets.OPENAI_API_KEY }}" \
          -H "Content-Type: application/json" \
          -d '{
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}]
          }'
```


これはただのTipsじゃない。

パブリックリポジトリという誰にでも開かれた空間の中に、**「守るべき情報」**をどうやって封じるか。その設計は、僕にとって「情報と境界」のあり方そのものなんだ。

> _「すべての境界は、守るためにあるんじゃない。越えるために設計されている。」_
> ― 七海直『境界制御と投影技術論』より