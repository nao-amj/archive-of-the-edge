# Archive of the Edge - シーケンス図

このドキュメントでは、「Archive of the Edge」システムの主要なワークフローをシーケンス図として説明します。

## 1. 日次リフレクション生成

このワークフローは毎日深夜（UTC）に実行され、リポジトリの分析に基づいて内省的な思考を生成します。

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant AS as analyze-content.js
    participant MM as memory-manager.js
    participant GC as generate-content.js
    participant Repo as リポジトリ

    GHA->>GHA: daily_reflection.yml実行
    GHA->>AS: リポジトリ分析実行
    AS->>Repo: Markdownファイル取得
    Repo-->>AS: ファイル内容
    AS->>AS: 内容を解析（キーワード、トピック抽出）
    AS->>AS: 最近の活動を特定
    AS->>AS: 分析結果を.github/temp/に保存
    AS-->>GHA: 分析完了
    
    GHA->>GC: 内容生成を実行
    GC->>GC: テンプレート選択（リフレクション）
    GC->>MM: 関連する記憶を要求
    MM->>MM: 記憶グラフをロード
    MM->>MM: 分析内容に基づいて関連記憶検索
    MM-->>GC: 関連記憶
    GC->>GC: リフレクション内容を生成
    GC->>GC: 生成内容を一時ファイルに保存
    GC-->>GHA: 生成完了
    
    GHA->>Repo: memory/thoughts/にリフレクションを保存
    GHA->>Repo: コミットして変更をプッシュ
```

## 2. 記憶インデクサーとグラフメンテナンス

このワークフローは、記憶関連ファイルが変更された時に実行され、記憶インデックスとグラフを更新します。

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant MM as memory-manager.js
    participant Repo as リポジトリ

    GHA->>GHA: memory_indexer.yml実行
    
    GHA->>MM: 記憶グラフ更新を実行
    MM->>MM: 記憶グラフをロード
    MM->>Repo: 記憶ディレクトリを再帰的に検索
    Repo-->>MM: 記憶ファイル一覧と内容
    
    loop 各記憶ファイルに対して
        MM->>MM: 記憶をトークン化
        MM->>MM: 既存の記憶との類似度計算
        MM->>MM: 関連エッジを作成（閾値以上の類似度）
    end
    
    MM->>Repo: 記憶グラフを保存（memory/graph/memory-graph.json）
    GHA->>Repo: 変更をコミットしてプッシュ
    
    GHA->>MM: GitHub IssuesとDiscussionsを取得
    MM->>MM: 記憶グラフにIssuesとDiscussionsを追加
    MM->>Repo: 更新された記憶グラフを保存
    GHA->>Repo: 変更をコミットしてプッシュ
```

## 3. 七海直自律システム

このワークフローは2日に1回、または手動で実行され、自律的な思考を生成してIssueとして公開します。

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant AS as analyze-content.js
    participant MM as memory-manager.js
    participant GC as generate-content.js
    participant Repo as リポジトリ
    participant Issues as GitHub Issues

    GHA->>GHA: nao-autonomy.yml実行
    GHA->>AS: リポジトリ分析実行
    AS->>Repo: Markdownファイル取得
    Repo-->>AS: ファイル内容
    AS->>AS: 内容を解析（キーワード、トピック抽出）
    AS->>AS: 最近の活動を特定
    AS->>AS: 分析結果を.github/temp/に保存
    AS-->>GHA: 分析完了
    
    GHA->>MM: 記憶メンテナンスを実行
    MM->>MM: 古い記憶を整理
    MM-->>GHA: メンテナンス完了
    
    GHA->>GC: 自律思考生成を実行
    GC->>GC: 思考タイプの決定（random/指定）
    GC->>MM: 思考コンテキスト構築を要求
    MM->>MM: 記憶グラフをロード
    MM->>MM: 分析内容に基づいて関連記憶検索
    MM-->>GC: 関連記憶とコンテキスト
    GC->>GC: 思考内容を生成
    GC->>GC: メタデータを付与
    GC->>GC: 生成内容を一時ファイルに保存
    GC-->>GHA: 生成完了
    
    GHA->>Issues: 思考内容をIssueとして作成
    GHA->>Repo: dreams/ディレクトリに思考を保存
    GHA->>Repo: コミットして変更をプッシュ
```

## 4. 記憶ネットワーク視覚化システム

このワークフローは、記憶グラフデータを使用して視覚化インターフェースを生成し、GitHub Pagesにデプロイします。

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant MM as memory-manager.js
    participant Viz as Visualization Generator
    participant Repo as リポジトリ
    participant Pages as GitHub Pages

    GHA->>GHA: deploy-pages.yml実行
    GHA->>MM: 記憶グラフデータ取得
    MM->>Repo: memory/graph/memory-graph.jsonの読み込み
    Repo-->>MM: グラフデータ
    MM-->>GHA: 処理済みグラフデータ
    
    GHA->>Viz: 視覚化HTMLの生成
    Viz->>Viz: vis.jsを使用したネットワークグラフ生成
    Viz->>Viz: 記憶カードUIの構築
    Viz->>Viz: フィルタリングと検索機能の実装
    Viz->>GHA: 生成されたHTMLファイル
    
    GHA->>Repo: meta/memory_index.htmlの更新
    GHA->>Pages: GitHub Pagesへのデプロイ
    Pages-->>GHA: デプロイ完了通知
```

## 5. コンテンツ分析プロセス

このシーケンスは、analyze-content.jsスクリプトの内部動作を詳細に示しています。

```mermaid
sequenceDiagram
    participant AS as analyze-content.js
    participant FS as FileSystem
    participant API as GitHub API
    participant NLP as Natural言語処理
    
    AS->>AS: スクリプト初期化
    AS->>FS: 設定ディレクトリ確認と作成
    
    par 複数ディレクトリの同時分析
        AS->>FS: memoryディレクトリ読み込み
        FS-->>AS: ファイル一覧
        AS->>FS: dreamsディレクトリ読み込み
        FS-->>AS: ファイル一覧
        AS->>FS: signalsディレクトリ読み込み
        FS-->>AS: ファイル一覧
        AS->>FS: 他のディレクトリ...
    end
    
    AS->>AS: すべてのファイルからフロントマター抽出
    AS->>NLP: コンテンツを単語に分解
    NLP->>NLP: 頻出語の検出
    NLP->>NLP: タグとキーワードの抽出
    NLP-->>AS: 抽出された言語特徴
    
    AS->>AS: 最近更新されたファイルの特定
    AS->>API: 七海直の自己分析Issue取得
    API-->>AS: Issueの内容
    AS->>AS: 関心領域の抽出
    
    AS->>FS: 七海直の設定ファイル読み込み
    FS-->>AS: 設定内容
    
    AS->>AS: 分析結果のJSONオブジェクト作成
    AS->>FS: 分析結果を一時ファイルに保存
```

## 6. 記憶グラフ管理プロセス

このシーケンスは、memory-manager.jsの記憶グラフ管理に関する内部動作を示しています。

```mermaid
sequenceDiagram
    participant MM as memory-manager.js
    participant FS as FileSystem
    participant NLP as Natural言語処理
    participant API as GitHub API
    
    MM->>FS: グラフ設定ファイル読み込み
    FS-->>MM: 設定内容（またはデフォルト使用）
    
    MM->>FS: 記憶グラフファイル確認
    alt グラフファイルが存在する
        FS-->>MM: グラフデータ
        MM->>MM: グラフオブジェクトの復元
    else 存在しない
        MM->>MM: 新しいグラフオブジェクト作成
    end
    
    MM->>MM: 新しい記憶の追加リクエスト受信
    MM->>NLP: コンテンツをトークン化
    NLP->>NLP: ステミング処理
    NLP-->>MM: 処理済みトークン
    
    MM->>MM: 記憶ノード作成
    
    loop 既存の全記憶に対して
        MM->>MM: 類似度計算（コサイン類似度）
        alt 類似度が閾値を超える
            MM->>MM: 関連エッジを作成
        end
    end
    
    MM->>API: GitHub IssuesとDiscussions取得
    API-->>MM: Issues/Discussions一覧
    
    loop 各Issue/Discussionに対して
        MM->>MM: 記憶ノードとして追加
        MM->>MM: 関連するファイル記憶との関連性計算
        MM->>MM: 関連エッジを作成
    end
    
    MM->>MM: 古い記憶の整理リクエスト受信
    MM->>MM: 維持期間を超えた記憶を特定
    MM->>MM: 永続フラグのない古い記憶を削除
    MM->>MM: 関連するエッジも削除
    
    MM->>FS: 更新されたグラフを保存
```

## 7. 思考生成プロセス

このシーケンスは、generate-content.jsが思考内容を生成する内部プロセスを示しています。

```mermaid
sequenceDiagram
    participant GC as generate-content.js
    participant FS as FileSystem
    participant MM as memory-manager.js
    participant Env as 環境変数
    
    GC->>Env: 思考タイプと優先度を取得
    GC->>FS: 分析結果ファイル読み込み
    FS-->>GC: 分析データ
    
    GC->>MM: 思考コンテキスト構築を要求
    MM->>MM: 分析データから現在コンテキストを作成
    MM->>MM: 関連する記憶を検索
    MM-->>GC: コンテキストと関連記憶
    
    alt タイプ = 質問
        GC->>GC: 質問テンプレート選択
    else タイプ = 内省
        GC->>GC: 内省テンプレート選択
    else タイプ = アイデア
        GC->>GC: アイデアテンプレート選択
    else タイプ = 物語
        GC->>GC: 物語テンプレート選択
    else タイプ = メタ内省
        GC->>GC: メタ内省テンプレート選択
    end
    
    GC->>GC: テンプレートに情報を挿入
    GC->>GC: 一貫性を確保するための調整
    GC->>GC: タイトル生成
    GC->>GC: フロントマター（メタデータ）追加
    
    GC->>FS: 生成内容を一時ファイルに保存
    GC->>Env: 環境変数に生成情報を設定
```

## 8. GitHub Pages デプロイプロセス

このシーケンスは、記憶ネットワークのビジュアライゼーションをGitHub Pagesにデプロイするプロセスを示しています。

```mermaid
sequenceDiagram
    participant GHA as GitHub Actions
    participant GHP as GitHub Pages
    participant FS as FileSystem
    
    GHA->>GHA: deploy-pages.yml実行
    GHA->>FS: 必要なアセットファイルの準備
    FS-->>GHA: アセットファイル
    
    GHA->>GHA: 静的HTMLファイルのビルド
    GHA->>GHA: CSS/JSアセットの最適化
    
    GHA->>GHP: GitHub Pagesにデプロイ
    GHP->>GHP: デプロイの検証
    GHP-->>GHA: デプロイ結果
    
    alt デプロイ成功
        GHA->>GHA: 成功ステータスを記録
    else デプロイ失敗
        GHA->>GHA: エラーログを記録
        GHA->>GHA: 通知を送信
    end
```

これらのシーケンス図は、システムの主要なワークフローと処理の流れを視覚的に示しています。実際の実装では、GitHub Actionsワークフローファイルと各スクリプトファイルを参照することで、より詳細な理解を得ることができます。