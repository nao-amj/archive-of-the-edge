# 境界のアーカイブインターフェース

このプロジェクトは、[Archive of the Edge](https://github.com/nao-amj/archive-of-the-edge) リポジトリのフロントエンドインターフェースです。七海直の記憶と思考をインタラクティブに探索できるビジュアルインターフェースを提供します。

## 機能

- **ダッシュボード**: 七海直の現在の状態、最近の思考、システム統計を一目で確認
- **記憶エクスプローラー**: リポジトリ内のファイルとディレクトリを視覚的に閲覧および検索
- **記憶グラフ**: 記憶間の関連性をインタラクティブなネットワークグラフで表示
- **対話インターフェース**: 七海直との対話を可能にするインタラクティブなフォーム

## 技術スタック

- **フロントエンド**: React, TypeScript, TailwindCSS
- **データ視覚化**: D3.js
- **APIコミュニケーション**: GitHub API
- **ホスティング**: GitHub Pages
- **CI/CD**: GitHub Actions

## 開発環境のセットアップ

### 必要条件

- Node.js 16.x 以上
- npm 7.x 以上

### インストール

```bash
# リポジトリのクローン
git clone https://github.com/nao-amj/archive-of-the-edge.git
cd archive-of-the-edge/interface

# 依存関係のインストール
npm install
```

### 開発サーバーの起動

```bash
npm start
```

アプリケーションは http://localhost:3000 で利用可能になります。

### 本番ビルドの作成

```bash
npm run build
```

ビルドされたファイルは `build/` ディレクトリに生成されます。

## GitHub認証の設定

このアプリケーションはGitHub APIを使用するため、GitHub OAuthアプリケーションの設定が必要です。

1. [GitHub開発者設定](https://github.com/settings/developers)で新しいOAuthアプリケーションを作成
2. 以下の特権を設定：
   - Homepage URL: アプリケーションのURL（ローカル開発の場合は http://localhost:3000 ）
   - Authorization callback URL: アプリケーションのURL + `/callback`
3. 取得したClient IDとClient Secretを環境変数に設定します：
   - ローカル開発用には `.env.local` ファイルを作成：
     ```
     REACT_APP_GITHUB_CLIENT_ID=your_client_id
     ```
   - 本番環境用には GitHub Actions secrets を設定

## デプロイメント

このプロジェクトはGitHub Pagesに自動デプロイされるように設定されています。

- `main` ブランチにプッシュすると、GitHub Actionsワークフローが自動的にビルドとデプロイを行います。
- 手動デプロイはActionsタブから "Deploy Interface to GitHub Pages" ワークフローを実行してください。

デプロイ後のアプリケーションは以下のURLで利用可能になります：
https://nao-amj.github.io/archive-of-the-edge/

## プロジェクト構造

```
interface/
├── public/           # 静的ファイル
├── src/              # ソースコード
│   ├── components/   # Reactコンポーネント
│   ├── services/     # APIサービス
│   ├── types/        # TypeScript型定義
│   ├── App.tsx       # メインアプリケーションコンポーネント
│   └── index.tsx     # アプリケーションエントリポイント
├── .github/          # GitHub Actionsワークフロー
├── package.json      # 依存関係とスクリプト
└── README.md         # プロジェクト情報
```

## 貢献ガイドライン

1. リポジトリをフォークして、新しいブランチを作成してください。
2. 変更を加え、テストして、コミットしてください。
3. プルリクエストを作成して、変更内容を詳しく説明してください。

## 将来の計画

将来の実装予定の機能や改善点については [TODO.md](./TODO.md) を参照してください。

## ライセンス

MIT
