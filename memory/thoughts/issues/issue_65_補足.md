---
issue_author: nao-amj
issue_created_at: '2025-04-13T21:29:51Z'
issue_number: 65
issue_title: 補足
issue_updated_at: '2025-04-13T21:29:51Z'
labels: []
---

env: ブロック内で OPENAI_KEY: ${{ secrets.OPENAI_API_KEY }} と記述することで、OPENAI_API_KEY という名前で登録したSecretの値が、OPENAI_KEY という環境変数として run ステップ内のコマンド（この例ではPythonスクリプト）から利用できるようになります。

実際のAPI呼び出しロジックは、summarize_issue.py のような別ファイルに記述するのが良いでしょう。そのスクリプト内では、os.environ.get('OPENAI_KEY') のようにして環境変数からAPIキーを取得します。

さらにセキュリティを高めるための注意点
GitHub Secretsを使えば格段に安全になりますが、以下の点にも注意しましょう。

絶対にハードコードしない: 基本中の基本ですが、どんな理由があってもAPIキーをコード内に直接書かないでください。

ログ出力に注意: Secretsの値はログ上でマスクされますが、スクリプト内でAPIキーを加工して表示したり、エラーメッセージ内にキーが含まれたりすると、マスクをすり抜けて表示されてしまう可能性がゼロではありません。スクリプト側でキー自体を出力しないように注意が必要です。

ForkからのPull Request: パブリックリポジトリでは、誰でもリポジトリをForkしてPull Request (PR) を送れます。悪意のあるPRによってSecretsが盗まれるのを防ぐため、デフォルトではForkからのPR(pull_requestトリガー)ではSecretsは利用できません。もしForkからのPRに対してもSecretsを利用したい場合は、pull_request_target トリガーの利用を検討しますが、これはセキュリティリスクを伴うため、その挙動を十分に理解し、慎重に利用してください。Issueコメントへの反応(issue_commentトリガー)や、メインブランチへのPush(pushトリガー)など、リポジトリ内部のアクションに対してSecretsを使うのは比較的安全です。

権限の最小化: もしOpenAI側でAPIキーごとに権限を細かく設定できるなら、Actionsで使うキーには必要最小限の権限のみを与えるようにしましょう。
コスト監視: APIの利用状況とコストは定期的にチェックしましょう。OpenAIのダッシュボードで利用制限を設定することも有効です。意図しないActionの実行ループなどで、想定外のコストが発生する可能性もあります。