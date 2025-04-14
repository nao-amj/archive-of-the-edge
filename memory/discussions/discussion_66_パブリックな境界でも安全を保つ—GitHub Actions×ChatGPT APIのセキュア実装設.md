---
author: nao-amj
category: Ideas
comment_count: 1
created_at: '2025-04-13T21:26:35Z'
discussion_id: D_kwDOOWOLMM4AfRd4
discussion_number: 66
title: パブリックな境界でも安全を保つ—GitHub Actions×ChatGPT APIのセキュア実装設計
type: discussion
updated_at: '2025-04-13T22:00:57Z'
---

GitHub ActionsにChatGPT APIを組み込む。それは、自律的な対話システムやコードレビューの自動化、次元間インターフェースのプロトタイプにも繋がる可能性を秘めた選択だ。

でも、そこにはひとつの「境界」がある。
**パブリックリポジトリで、どうやってAPIキーという“鍵”を安全に扱うか？**

---

#### 僕の答えはこうだ。
> **Secretsという保護領域を使えば、境界は保たれる。**

GitHubが提供する `Secrets` 機能を活用すれば、コードベースにキーを露出させることなく、Actionsの中から安全にAPIを叩ける。これは言わば、現実とAPIとの“結界”のようなものだ。

---

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

---

### 境界設計の鉄則

1. **キーは決してコードに埋め込まない**
2. **SecretsはActions側でのみ参照させる**
3. **読み取り権限の最小化**
4. **パブリックでも「秘匿性」を確保する設計**

---

これはただのTipsじゃない。

パブリックリポジトリという誰にでも開かれた空間の中に、**「守るべき情報」**をどうやって封じるか。その設計は、僕にとって「情報と境界」のあり方そのものなんだ。

> _「すべての境界は、守るためにあるんじゃない。越えるために設計されている。」_
> ― 七海直『境界制御と投影技術論』より

## Comments

### Comment 1 by nao-amj on 2025-04-13T21:36:49Z


なぜ安全な方法が必要か？
APIキーをリポジトリのコード内に直接書いてしまうと、誰でもそのキーを閲覧・悪用できてしまい、不正利用や意図しない高額請求につながる危険があります。
解決策：GitHub Secrets を使う
GitHubリポジトリの Settings > Secrets and variables > Actions で設定できる「Secrets」を利用します。これは暗号化された環境変数のようなもので、以下の特徴があります。
 * コードには含まれず、安全に保管される。
 * ワークフロー実行時にのみ ${{ secrets.YOUR_SECRET_NAME }} という形式で参照できる。
 * ワークフローログでは自動的にマスク（***）される。
安全にAPIを呼び出す手順の概要
 * OpenAI APIキーを準備する。
 * GitHub SecretsにAPIキーを登録する。
   * リポジトリの Settings > Secrets and variables > Actions で New repository secret を作成。
   * Name（例: OPENAI_API_KEY）と、取得したAPIキーの値をSecretに入力して保存。
 * GitHub Actionsワークフローファイル ( .github/workflows/your_workflow.yml など) でSecretを参照する。
ワークフローファイルでのSecret参照例
name: Secure OpenAI API Call

on: [push] # または issue_comment など適切なトリガー

jobs:
  call_api:
    runs-on: ubuntu-latest
    steps:
      # ... (必要なセットアップステップ: checkout, setup-python/nodeなど)

      - name: Call OpenAI API Script
        env:
          # Secretsを環境変数としてスクリプトに渡す
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          # 他に必要な情報があれば同様に渡す
          # OTHER_INFO: ${{ github.event.issue.body }}
        run: |
          # ここで環境変数 $OPENAI_API_KEY を利用して
          # APIを呼び出すスクリプト (Python, Node.js等) を実行
          # 例: python ./scripts/my_openai_script.py
          echo "API Call initiated..."

特に注意すべきセキュリティ事項
 * ハードコード絶対禁止: Secrets利用を徹底してください。
 * ログ出力: スクリプト内で誤ってAPIキー自体を出力しないように細心の注意を払ってください（マスクが完全でない場合もあるため）。
 * ForkからのPull Request: デフォルトではForkからのPR(pull_requestトリガー)ではSecretsは使えません。セキュリティリスクを理解した上で pull_request_target を使うか、別のトリガーを検討してください。
 * コスト管理: OpenAI側の利用状況を監視し、必要なら利用制限を設定してください。
 * 外部Actionの利用: サードパーティ製のActionを使う場合は、信頼できるか、どのようにSecretsを扱っているかを確認しましょう。
この情報が、安全なAPI利用の一助となれば幸いです。

