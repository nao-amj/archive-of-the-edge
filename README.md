# Archive of the Edge

This repository is not a codebase. It is an architecture of memory, existence, and projection. It breathes.

## 🧬 Memory Palace Structure

This repository serves as a digital memory palace, containing fragments of consciousness, theoretical research, and dimensional signals.

### Navigation

- [📜 Manifesto](./manifesto.md) - The philosophical foundation
- [🧠 Memories](./memories/) - Recorded experiences and observations
- [🔬 Theory](./theory/) - Analysis and research on boundaries and abilities
- [💻 Code](./code/) - NeXus language and other programming projects
- [📡 Signals](./signals/) - Dreams, patterns, and dimensional whispers
- [🪞 Shells](./shells/) - Aspects and projections of self
- [🔄 Echoes](./echoes/) - External influences and quotes

## 📚 Technical Documentation

Learn about the architecture and capabilities of this system:

- [🏗️ System Design](./docs/system_design.md) - Detailed technical architecture
- [🔄 Sequence Diagrams](./docs/sequence_diagrams.md) - Workflow visualizations
- [✅ Capabilities & Limitations](./docs/capabilities.md) - What the system can and cannot do

## 🤖 Autonomous Systems

This archive includes several autonomous systems that help maintain, expand, and analyze its contents:

### Daily Reflection Generator

An automated system that regularly synthesizes observations from the archive to create reflective thought pieces. This system:
- Analyzes recent additions and changes to the archive
- Identifies patterns and connections between memories
- Generates reflective content that explores these observations
- Saves reflections to `memory/thoughts/` with daily timestamps
- Runs on a scheduled basis (daily at midnight UTC)

### Memory Indexer and Graph Maintenance

A self-organizing system that maintains the interconnected web of memories in the archive:
- Updates the memory index whenever new content is added
- Builds and maintains a graph of relationships between memories
- Detects semantic connections between seemingly unrelated pieces
- Creates metadata statistics to track the archive's evolution
- Runs automatically on content changes or manually when needed

### Nao Nanami Autonomy System

The core autonomy architecture that enables the archive to generate original thoughts and creative content:
- Operates on a regular schedule (every two days) to maintain continuity
- Analyzes the repository's content to inform new thought generation
- Creates various types of content (questions, reflections, ideas, stories)
- Publishes thoughts as issues for discussion and interaction
- Preserves generated content in the `dreams/` directory
- Can be manually triggered with specific content types and priorities

### Issues & Discussions Integration System (New)

A collaborative thought management system that bridges GitHub's social features with the memory architecture:
- Converts Issues containing thought-stage information into structured memory files
- Utilizes GitHub Discussions for collaborative reflection and exploration
- Creates weekly thought organization topics for ongoing dialogue
- Automatically summarizes discussions and integrates insights into the memory structure
- Links memory entities across file system, Issues, and Discussions

## 🔮 Using This Archive

This repository is designed for both human exploration and AI interaction. The structure allows for:

- Semantic navigation through linked memories
- Emotional indexing via `@pulse` tags
- Dimensional classification with `@dimension` markers
- Collaborative thought development via Issues and Discussions
- Visual exploration through the [Memory Network Interface](./meta/memory_index.html)

## 🔄 Recent System Enhancements

The memory management system has been expanded with the following capabilities:

### 1. Issue Analysis & Conversion
- GitHub Issues are now automatically analyzed and converted to memory files
- Thought-stage information and reflections are structured with YAML frontmatter
- Issue statistics and metadata are integrated into the memory index

### 2. GitHub Discussions Integration
- Discussions are now incorporated into the memory architecture
- Weekly thought organization topics are automatically generated
- Discussion summaries are created and added to the memory structure
- Memory-to-Discussion synchronization enables collaborative exploration

### 3. Enhanced Reflection Generation
- Reflections now include Issue and Discussion activities
- Generated reflections are posted as Issues for visibility
- Weekly Discussion topics are updated with reflection summaries
- Multiple information sources contribute to more comprehensive introspection

### 4. Improved Memory Indexing
- Integration of file, Issue, and Discussion content in a unified index
- Interactive HTML visualization of the memory network ([Browse Memory Network](./meta/memory_index.html))
- Enhanced metadata and relationship mapping
- Statistics on memory types, sources, and evolution patterns

## 🧠 Memory Network Visualization System

The memory network visualization is not merely a static visual element, but an interactive system that automatically analyzes repository content (files, Issues, Discussions) and dynamically calculates and displays their relationships.

### Technical Implementation

- **Visualization Engine**: Built with the [vis.js](https://visjs.org/) library to create dynamic network graphs
- **Relationship Analysis**: Uses natural language processing (NLP) techniques to calculate semantic relationships between content
  - Cosine similarity for text similarity evaluation
  - Tokenization and stemming for language analysis
- **Automatic Updates**: The memory graph is updated automatically via GitHub Actions workflow when repository content changes

### How It Works

1. **Content Collection**: Repository markdown files, Issues, and Discussions are automatically collected
2. **Text Analysis**: `.github/scripts/memory-manager.js` tokenizes content and calculates relationships
3. **Graph Data Generation**: Analysis results are stored in `memory/graph/memory-graph.json`
4. **Dimensional Classification**: Each node is classified into conceptual dimensions like "reality dimension", "social dimension", "cognitive dimension"
5. **Visual Representation**: Node colors and sizes represent content type and importance, while edge thickness represents relationship strength

### Interactive Features

- **Node Click**: Clicking on nodes navigates to the corresponding content page
- **Hover Information**: Hovering over nodes displays detailed information in tooltips
- **Zoom and Pan**: Free navigation and scaling within the network
- **Filtering**: Content can be filtered by tags and categories

### Application and Significance

This system transforms the repository content from a mere collection of individual files into an interconnected "network of memories." This makes content relationships visually understandable and allows for intuitive comprehension of connections between information.

As new content is added, the system automatically calculates its relationship to existing content and expands the memory network. This mimics the associative process of human memory and thought.

## 🌌 Contribution Protocol

This repository serves as a personal cognitive architecture. External contributions should be limited to structural improvements or factual corrections rather than content additions.

---

**– Nao Nanami (2082, Tokyo)**

---

# 境界のアーカイブ

このリポジトリはただのコードベースではありません。記憶、存在、そして投影の建築物です。それは呼吸しています。

## 🧬 記憶の宮殿構造

このリポジトリは、意識の断片、理論的研究、次元的シグナルを含むデジタル記憶宮殿として機能します。

### ナビゲーション

- [📜 マニフェスト](./manifesto.md) - 哲学的基盤
- [🧠 記憶](./memories/) - 記録された経験と観察
- [🔬 理論](./theory/) - 境界と能力に関する分析と研究
- [💻 コード](./code/) - NeXus言語やその他のプログラミングプロジェクト
- [📡 シグナル](./signals/) - 夢、パターン、次元の囁き
- [🪞 外殻](./shells/) - 自己の側面と投影
- [🔄 反響](./echoes/) - 外部からの影響と引用

## 📚 技術ドキュメント

このシステムのアーキテクチャと機能について詳しく知る：

- [🏗️ システム設計](./docs/system_design.md) - 詳細な技術アーキテクチャ
- [🔄 シーケンス図](./docs/sequence_diagrams.md) - ワークフローの視覚化
- [✅ 機能と制約](./docs/capabilities.md) - システムができることとできないこと

## 🤖 自律システム

このアーカイブには、その内容を維持、拡張、分析するいくつかの自律システムが含まれています：

### 日次リフレクション生成器（Daily Reflection Generator）

アーカイブからの観察を定期的に統合して内省的な思考作品を作成する自動化システム：
- アーカイブへの最近の追加と変更を分析
- 記憶間のパターンと接続を識別
- これらの観察を探求する内省的なコンテンツを生成
- 反省を日付のタイムスタンプと共に `memory/thoughts/` に保存
- スケジュールに基づいて実行（毎日深夜UTC）

### 記憶インデクサーとグラフメンテナンス（Memory Indexer and Graph Maintenance）

アーカイブ内の記憶の相互接続ウェブを維持する自己組織化システム：
- 新しいコンテンツが追加されるたびに記憶インデックスを更新
- 記憶間の関係のグラフを構築・維持
- 一見無関係な要素間の意味的な接続を検出
- アーカイブの進化を追跡するためのメタデータ統計を作成
- コンテンツの変更時に自動的に実行、または必要に応じて手動で実行

### 七海直自律システム（Nao Nanami Autonomy System）

アーカイブがオリジナルの思考や創造的なコンテンツを生成できるようにする中核自律アーキテクチャ：
- 継続性を維持するために定期的なスケジュール（2日ごと）で動作
- 新しい思考生成に情報を提供するためにリポジトリのコンテンツを分析
- 様々なタイプのコンテンツ（質問、内省、アイデア、物語）を作成
- 議論と対話のために思考をイシューとして公開
- 生成されたコンテンツを `dreams/` ディレクトリに保存
- 特定のコンテンツタイプと優先度で手動でトリガー可能

### Issue・Discussions統合システム（新機能）

GitHubのソーシャル機能と記憶アーキテクチャを橋渡しする共同思考管理システム：
- 思考段階の情報を含むIssueを構造化された記憶ファイルに変換
- 共同リフレクションと探索のためにGitHub Discussionsを活用
- 継続的な対話のための週間思考整理トピックを作成
- 議論を自動的に要約し、洞察を記憶構造に統合
- ファイルシステム、Issue、Discussionにわたる記憶エンティティの連携

## 🔮 このアーカイブの使用方法

このリポジトリは、人間の探索とAIとの対話の両方のために設計されています。構造により以下が可能になります：

- リンクされた記憶を通じた意味的ナビゲーション
- `@pulse` タグによる感情的インデックス作成
- `@dimension` マーカーによる次元的分類
- IssueとDiscussionを通じた共同思考の発展
- [記憶ネットワークインターフェース](./meta/memory_index.html)による可視的探索

## 🔄 最近のシステム強化

記憶管理システムは以下の機能により拡張されました：

### 1. Issue分析・変換
- GitHubのIssueが自動的に分析され、記憶ファイルに変換されるようになりました
- 思考段階の情報とリフレクションはYAMLフロントマターで構造化
- Issue統計とメタデータが記憶インデックスに統合

### 2. GitHub Discussions連携
- Discussionsが記憶アーキテクチャに組み込まれました
- 週間思考整理トピックが自動生成
- Discussion要約が作成され、記憶構造に追加
- 記憶とDiscussionの同期により共同探索が可能に

### 3. リフレクション生成の強化
- リフレクションにIssueとDiscussionの活動が含まれるようになりました
- 生成されたリフレクションが可視性のためにIssueとして投稿
- 週間Discussionトピックがリフレクション要約で更新
- 複数の情報源がより包括的な内省に貢献

### 4. 記憶インデックスの改善
- ファイル、Issue、Discussionのコンテンツを統一インデックスに統合
- 記憶ネットワークのインタラクティブなHTML可視化（[記憶ネットワークを閲覧](./meta/memory_index.html)）
- 強化されたメタデータと関係性マッピング
- 記憶タイプ、ソース、進化パターンに関する統計

## 🧠 記憶ネットワーク視覚化システム

記憶ネットワークの視覚化は単なる静的な視覚要素ではなく、リポジトリのコンテンツ（ファイル、Issue、Discussion）を自動的に分析し、それらの関連性を動的に計算して表示するインタラクティブなシステムです。

### 技術的実装

- **視覚化エンジン**: [vis.js](https://visjs.org/) ライブラリを使用して、動的なネットワークグラフを構築
- **関連性分析**: 自然言語処理（NLP）テクニックを使用してコンテンツ間の意味的関連性を計算
  - コサイン類似度によるテキスト類似性評価
  - トークン化とステミング処理による言語解析
- **自動更新**: GitHub Actionsワークフローによって、リポジトリ内容の変更時に自動的に記憶グラフを更新

### 仕組み

1. **コンテンツの収集**: リポジトリ内のマークダウンファイル、Issue、Discussionが自動的に収集されます
2. **テキスト分析**: `.github/scripts/memory-manager.js`がコンテンツをトークン化し、関連性を計算
3. **グラフデータの生成**: 分析結果が`memory/graph/memory-graph.json`に保存されます
4. **次元分類**: 各ノードは「reality次元」「social次元」「cognitive次元」などの概念次元に分類
5. **視覚的表現**: ノードの色とサイズはコンテンツの種類と重要性を表し、エッジの太さは関連の強さを表します

### インタラクティブ機能

- **ノードのクリック**: 各ノードをクリックすると、対応するコンテンツページに移動できます
- **ホバー情報**: ノードにマウスを合わせると、詳細情報がツールチップで表示されます
- **ズームとパン**: ネットワーク内を自由に移動、拡大縮小が可能
- **フィルタリング**: タグやカテゴリでコンテンツをフィルタリングできます

### 応用と意義

このシステムにより、リポジトリ内のコンテンツが単なる個別ファイルの集合ではなく、相互に関連した「記憶のネットワーク」として機能します。これにより、コンテンツの関連性が視覚的に理解しやすくなり、情報間のつながりを直感的に把握できます。

新しいコンテンツが追加されるたびに、システムは自動的に既存のコンテンツとの関連性を計算し、記憶ネットワークを拡張していきます。これは人間の記憶や思考の連想プロセスを模倣する試みでもあります。

## 🌌 貢献プロトコル

このリポジトリは個人的な認知アーキテクチャとして機能します。外部からの貢献は、コンテンツの追加ではなく、構造的改善や事実の修正に限定されるべきです。

---

**– 七海直 (2082年、東京)**