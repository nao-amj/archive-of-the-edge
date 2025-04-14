---
issue_author: nao-amj
issue_created_at: '2025-04-11T01:24:03Z'
issue_number: 17
issue_title: '@octokit/rest の ESM モジュールエラーを解消'
issue_updated_at: '2025-04-11T01:24:29Z'
labels: []
---

## 修正内容

GitHub Actions の実行エラーを解消するため、@octokit/rest の ESM モジュールインポート方法を修正しました。

### 変更点
- `require('@octokit/rest')` から動的インポート `import('@octokit/rest')` に変更
- 以下のスクリプトファイルを修正:
  - `.github/scripts/analyze-content.js`
  - `.github/scripts/memory-manager.js`
  - `.github/scripts/generate-content.js`

### 修正の背景
@octokit/rest パッケージが CommonJS から ESM に移行したことで、従来の `require()` での読み込みが動作しなくなり、GitHub Actions での自動処理が失敗していました。この PR では、動的インポートを使用することで ESM モジュールを正しく読み込めるようにしています。