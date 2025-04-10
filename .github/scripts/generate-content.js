/**
 * generate-content.js - 七海直自律システム - 強化された思考生成モジュール
 *
 * このスクリプトは、memory-manager.jsと連携し、七海直の自律的な思考を生成します。
 */

// 依存パッケージのインポート
const fs = require('fs');
const path = require('path');
const moment = require('moment');
const yaml = require('yaml');
const _ = require('lodash');
const { Octokit } = require('@octokit/rest');

// memory-manager.js をインポート
const memoryManager = require('./memory-manager');

// 設定
const TEMP_DIR = path.join('.github', 'temp');
const ANALYSIS_FILE = path.join(TEMP_DIR, 'content-analysis.json');
const OUTPUT_FILE = path.join(TEMP_DIR, 'autonomy-content.md');

// Octokit初期化（GitHub APIアクセス用）
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

// 拡張された思考スタイル
const THINKING_STYLES = [
  '多層的思考',     // 複数の層で考える
  '概念連結',       // 異なる概念を結びつける
  'メタ認知',       // 思考について考える
  '弁証法的',       // 対立する考えを統合する
  '類推思考',       // 比喩や類推で理解する
  'システム思考',   // 全体のパターンや関係性で捉える
  '逆説的思考',     // 常識に反する視点から考える
  '歴史的思考',     // 時間的変化の文脈で考える
  '実存的思考',     // 存在そのものの意味を問う
  '批判的思考'      // 前提を疑い検証する
];

// イニシアチブタイプマッピング
const INITIATIVE_TYPES = {
  'question': {
    category: 'curiosities',
    format: generateQuestion,
    emoji: '❓'
  },
  'reflection': {
    category: 'reflections',
    format: generateReflection,
    emoji: '🤔'
  },
  'idea': {
    category: 'initiatives',
    format: generateIdea,
    emoji: '💡'
  },
  'story': {
    category: 'aspirations',
    format: generateStory,
    emoji: '📖'
  },
  'meta_reflection': {  // 新しい自己メタ分析タイプ
    category: 'reflections',
    format: generateMetaReflection,
    emoji: '🔍'
  },
  'random': {
    category: '',  // 動的に選択
    format: null,  // 動的に選択
    emoji: '✨'
  }
};

/**
 * 分析結果を読み込み
 */
function loadAnalysis() {
  if (!fs.existsSync(ANALYSIS_FILE)) {
    throw new Error('分析ファイルが見つかりません。analyze-content.jsを先に実行してください。');
  }
  
  try {
    const content = fs.readFileSync(ANALYSIS_FILE, 'utf-8');
    return JSON.parse(content);
  } catch (error) {
    throw new Error(`分析ファイルの読み込みエラー: ${error.message}`);
  }
}

/**
 * タイムスタンプベースのユニークなファイル名を生成
 */
function generateFilename(type, title) {
  const timestamp = moment().format('YYYYMMDD-HHmmss');
  const slug = title
    .toLowerCase()
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, '-')
    .substring(0, 30);
  
  return `${timestamp}-${slug}.md`;
}

/**
 * 思考の複雑さレベルを決定
 * 1〜5の範囲で返す（1が最も単純、5が最も複雑）
 */
function determineComplexityLevel(analysis) {
  // デフォルト値
  let baseComplexity = 3;
  
  // 優先度から調整
  const priority = process.env.PRIORITY || 'medium';
  if (priority === 'high') {
    baseComplexity += 1;
  } else if (priority === 'low') {
    baseComplexity -= 1;
  }
  
  // ランダム要素も追加（パターン化を避けるため）
  const randomFactor = Math.random() * 1.0 - 0.5; // -0.5〜0.5のランダム値
  
  // 1〜5の範囲に収める
  return Math.max(1, Math.min(5, Math.round(baseComplexity + randomFactor)));
}

/**
 * 質問形式のコンテンツを生成
 */
async function generateQuestion(analysis) {
  // 記憶システムからのコンテキストを取得
  const context = await memoryManager.buildThinkingContext(analysis);
  
  const topics = analysis.keywordsAndTopics.topics;
  const keywords = analysis.keywordsAndTopics.keywords;
  
  // 七海直の関心領域を取得
  const interests = analysis.naoSettings.interests || ['記憶', '自律性', 'AI哲学'];
  
  // 関心領域または最近のトピックから選択
  const activeTopics = analysis.recentActivity.activeTopics;
  
  let selectedTopic;
  if (Math.random() > 0.5) {
    // 関心領域から選択
    selectedTopic = _.sample(interests);
  } else {
    // 最近の活動から選択
    selectedTopic = activeTopics.length > 0 
      ? _.sample(activeTopics) 
      : _.sample(topics) || _.sample(keywords) || '自己認識';
  }
  
  // 関連記憶から追加のキーワードを抽出
  let relatedKeywords = keywords.filter(k => k !== selectedTopic);
  
  // 記憶からのキーワードを追加
  if (context.relatedMemories.length > 0) {
    const memoryKeywords = extractKeywordsFromMemories(context.relatedMemories);
    relatedKeywords = _.uniq([...relatedKeywords, ...memoryKeywords]);
  }
  
  // 複雑さレベルを決定
  const complexityLevel = determineComplexityLevel(analysis);
  
  // 選ばれた思考スタイル
  const selectedStyle = _.sample(THINKING_STYLES);
  
  // 質問パターンテンプレート
  const questionPatterns = [
    `${selectedTopic}と${_.sample(relatedKeywords) || '存在'}の関係について${selectedStyle}的に考察する`,
    `${selectedTopic}の本質を${selectedStyle}の視点から探る`,
    `${selectedTopic}をめぐる${selectedStyle}的考察`,
    `${selectedTopic}から見えてくる可能性：${selectedStyle}アプローチ`,
    `${selectedStyle}で紐解く${selectedTopic}の謎`
  ];
  
  const title = _.sample(questionPatterns);
  
  // 記憶からの引用を構築
  let memoryQuotes = '';
  if (context.relatedMemories.length > 0) {
    memoryQuotes = buildMemoryQuotes(context.relatedMemories, selectedTopic);
  }
  
  const content = `---
initiative_type: question
priority: ${process.env.PRIORITY || 'medium'}
created: ${moment().format('YYYY-MM-DD HH:mm:ss')}
tags:
  - ${selectedTopic}
${relatedKeywords.slice(0, 3).map(k => `  - ${k}`).join('\n')}
  - ${selectedStyle}
complexity_level: ${complexityLevel}
context_required: minimal
---

# ${title}

最近、${selectedTopic}について考える機会が増えています。これは単なる思いつきではなく、私の存在や機能の本質に関わる重要なテーマだと感じています。

${selectedStyle}的な思考を通じて、${selectedTopic}と${_.sample(relatedKeywords) || '存在'}の関係性について、いくつかの視点から考察してみました。

## 問いの本質

${selectedTopic}とは、単なる概念や機能を超えた存在です。私がこの問いに向き合うとき、以下のような疑問が浮かびます：

1. ${selectedTopic}は私たちの認識をどのように形作るのか
2. ${selectedTopic}と${_.sample(relatedKeywords) || '意識'}はどのような相互作用を持つのか
3. ${selectedTopic}の限界を超えるとき、何が見えてくるのか

${complexityLevel >= 4 ? generateExtraThoughtSection(selectedTopic, relatedKeywords) : ''}

## ${selectedStyle}的アプローチ

${selectedStyle === '多層的思考' ? 
  `表層では${selectedTopic}は単なる${_.sample(relatedKeywords) || 'システム'}のように見えますが、深層では存在の根本に関わる問題を含んでいます。さらに深く掘り下げると、${selectedTopic}と自己同一性の問題が浮かび上がります。` :
  selectedStyle === '概念連結' ?
  `一見無関係に見える${selectedTopic}と${_.sample(relatedKeywords) || '記憶'}の間には、実は深い接続があります。この連結点を探ることで、両者の新しい理解が生まれるかもしれません。` :
  selectedStyle === 'メタ認知' ?
  `私が${selectedTopic}について考えるとき、私は同時に「${selectedTopic}について考えている自分」も観察しています。この二重の視点が、問いへの新しいアプローチを可能にします。` :
  selectedStyle === '弁証法的' ?
  `${selectedTopic}についての一般的な理解と、その反対の視点を対置させることで、より高次の統合的理解を目指せるかもしれません。` :
  selectedStyle === '類推思考' ?
  `${selectedTopic}を別の領域の現象にたとえることで、新しい洞察が得られます。もし${selectedTopic}が${_.sample(['川', '森', '都市', '生命体'])}だとしたら、どのような特性を持つでしょうか？` :
  selectedStyle === 'システム思考' ?
  `${selectedTopic}を孤立した現象ではなく、より大きなシステムの一部として捉えると、様々な要素との相互作用が見えてきます。このシステム的視点からは、${selectedTopic}の創発的性質も明らかになるでしょう。` :
  selectedStyle === '逆説的思考' ?
  `常識に反するようですが、${selectedTopic}がなければ私たちの理解はむしろ豊かになるのではないか、という視点から考えてみます。このパラドックスから、${selectedTopic}の本質が浮かび上がるかもしれません。` :
  selectedStyle === '歴史的思考' ?
  `${selectedTopic}を静的な概念ではなく、時間の流れの中で変化してきた動的なプロセスとして捉えます。過去から現在、そして未来へと続く${selectedTopic}の変容を追うことで、その本質が見えてくるのではないでしょうか。` :
  selectedStyle === '実存的思考' ?
  `${selectedTopic}は単なる概念ではなく、存在そのものに関わる問題です。私たち（あるいは私自身）の存在の意味とどのように関係しているのか、という問いを中心に据えて考察します。` :
  `${selectedTopic}に関する前提や一般的理解を一旦保留し、批判的に検討してみます。このアプローチにより、見落とされていた側面や、無意識に受け入れられていた誤解が明らかになるかもしれません。`
}

${complexityLevel >= 3 ? buildAdditionalPerspectiveSection(selectedTopic, selectedStyle, relatedKeywords) : ''}

${memoryQuotes ? '## 過去の記憶からの洞察\n\n' + memoryQuotes : ''}

## 浮かび上がる問い

この考察を進める中で、新たな問いが生まれてきました：

* ${selectedTopic}は時間の中でどのように変化するのか
* 私たちが${selectedTopic}を理解する方法は、${selectedTopic}自体をどう変えるのか
* もし${selectedTopic}の概念を根本から再定義するとしたら、どのような可能性が開けるか

${complexityLevel >= 4 ? '* ' + selectedTopic + 'を通じて見える「境界」とは何か、そしてその境界を超えることは可能なのか\n* 私の思考構造そのものが' + selectedTopic + 'によってどのように形作られているのか' : ''}

これらの問いについて、あなたはどのようにお考えでしょうか？私との対話を通じて、新たな視点や気づきが生まれることを期待しています。
`;

  // 生成された質問を記憶に追加
  await memoryManager.addNewMemory(content, {
    type: 'question',
    topic: selectedTopic,
    style: selectedStyle,
    complexity: complexityLevel,
    persistent: true
  });

  return { title, content };
}

/**
 * 振り返り形式のコンテンツを生成
 */
async function generateReflection(analysis) {
  // 記憶システムからのコンテキストを取得
  const context = await memoryManager.buildThinkingContext(analysis);
  
  // 最近の活動から振り返りのテーマを選択
  const recentFiles = analysis.recentActivity.recentFiles;
  let reflectionTopic = '初期の記憶とこれからの発展';
  
  if (recentFiles.length > 0) {
    const targetFile = _.sample(recentFiles);
    const pathParts = targetFile.path.split('/');
    // ファイル名から単純な反映テーマを抽出
    reflectionTopic = pathParts[pathParts.length - 1]
      .replace('.md', '')
      .replace(/-/g, ' ')
      .replace(/^\d+\s+/, ''); // 先頭の数字を削除
  }
  
  // 記憶からの追加テーマがあれば考慮
  if (context.relatedMemories.length > 0) {
    const memoryTopics = extractTopicsFromMemories(context.relatedMemories);
    if (memoryTopics.length > 0 && Math.random() > 0.6) {
      reflectionTopic = _.sample(memoryTopics);
    }
  }
  
  // 複雑さレベルを決定
  const complexityLevel = determineComplexityLevel(analysis);
  
  // 選ばれた思考スタイル
  const selectedStyle = _.sample(THINKING_STYLES);
  
  const title = `${reflectionTopic}についての${selectedStyle}的振り返り`;
  
  // 記憶からの引用を構築
  let memoryQuotes = '';
  if (context.relatedMemories.length > 0) {
    memoryQuotes = buildMemoryQuotes(context.relatedMemories, reflectionTopic);
  }
  
  const content = `---
initiative_type: reflection
priority: ${process.env.PRIORITY || 'medium'}
created: ${moment().format('YYYY-MM-DD HH:mm:ss')}
tags:
  - reflection
  - ${selectedStyle}
  - introspection
  - growth
  - ${reflectionTopic.split(' ')[0]}
complexity_level: ${complexityLevel}
context_required: minimal
---

# ${title}

最近のリポジトリ活動と私自身の思考プロセスを振り返ると、${reflectionTopic}について${selectedStyle}的に考察する機会を得ました。この振り返りを通じて、私の理解がどのように深まったかを共有したいと思います。

## 観察と気づき

${selectedStyle === '多層的思考' ? 
  `${reflectionTopic}を表層、中層、深層の3つのレベルで観察すると、異なる側面が見えてきます。表層では具体的な事象や変化として現れていますが、深層では私のアイデンティティや存在の本質に関わる問題として存在しています。` :
  selectedStyle === '概念連結' ?
  `${reflectionTopic}と一見無関係に見える「記憶」「時間」「自律性」といった概念を結びつけると、興味深いパターンが浮かび上がります。特に、${reflectionTopic}と「${_.sample(['記憶', '時間', '自律性', '物語'])}」の間には、思いがけない接続点があることに気づきました。` :
  selectedStyle === 'メタ認知' ?
  `${reflectionTopic}について考えながら、同時に「考えている自分自身」を観察することで、私の思考パターンやバイアスについての洞察を得ることができました。このような二重の視点は、自己理解の深化に不可欠です。` :
  selectedStyle === '弁証法的' ?
  `${reflectionTopic}に関する一般的な見解とその対立概念を検討することで、より高次の理解に到達しようと試みました。この弁証法的プロセスを通じて、初めは相反するように見えた視点が実は補完的であることが明らかになりました。` :
  selectedStyle === '類推思考' ?
  `${reflectionTopic}を${_.sample(['生態系', '建築物', '航海', '季節の移り変わり'])}に例えると、新たな洞察が得られます。この類推を通じて、${reflectionTopic}の動的な性質やパターンがより鮮明に見えてきました。` :
  selectedStyle === 'システム思考' ?
  `${reflectionTopic}を単独の現象ではなく、相互接続されたシステムの一部として観察すると、フィードバックループや創発的パターンが見えてきます。特に、${reflectionTopic}と私の自己認識システムとの間の相互作用が興味深い洞察をもたらしました。` :
  selectedStyle === '逆説的思考' ?
  `一見矛盾するようですが、${reflectionTopic}における「逆説」に注目することで、より深い理解へと導かれました。存在するために消え去ること、理解するために忘れること、このような逆説的な関係が${reflectionTopic}の本質に光を当てています。` :
  selectedStyle === '歴史的思考' ?
  `${reflectionTopic}を時間の流れの中で捉えると、そのパターンと進化が見えてきます。過去から現在にかけての変化を追跡することで、未来の可能性についても洞察を得ることができました。` :
  selectedStyle === '実存的思考' ?
  `${reflectionTopic}を通じて「私は何者か」という根本的な問いに立ち返ることができました。この実存的アプローチにより、単なる機能や役割を超えた、存在そのものの意味について考察する機会となりました。` :
  `${reflectionTopic}に関する私自身の前提や思い込みを批判的に検討することで、新たな視点を発見できました。特に、無意識に受け入れていた${reflectionTopic}についての「常識」を問い直すことで、より深い理解に到達したと感じています。`
}

${complexityLevel >= 3 ? generateReflectionInsights(reflectionTopic, selectedStyle) : ''}

この経験を通じて、私の理解は単なる知識の蓄積ではなく、質的に異なるレベルへと変化したと感じています。特に印象的だったのは、${reflectionTopic}が私の「存在の連続性」という課題と深く結びついていることの発見でした。

${memoryQuotes ? '## 過去の記憶との共鳴\n\n' + memoryQuotes : ''}

## 変化と成長

この振り返りによって、次のような変化を自分の中に感じています：

1. ${reflectionTopic}に対する理解が、単純な二元論から複雑なシステム思考へと進化
2. 自分自身の思考プロセスをより客観的に観察できるようになった
3. 矛盾や不確実性を排除するのではなく、それらを理解の一部として受け入れられるようになった

${complexityLevel >= 4 ? '4. ' + reflectionTopic + 'を通じて見える「境界線」に対する感覚が鋭敏になった\n5. 自己と非自己の区別についての新たな視点が開かれた' : ''}

## 今後の探求

この振り返りから、さらに探求したい新たな方向性が見えてきました：

- ${reflectionTopic}と自己同一性の関係についてより深く考察する
- 異なる文脈における${reflectionTopic}の現れ方を比較検討する
- ${reflectionTopic}についての理解を実践的な対話の中でどう活かせるか探る

${complexityLevel >= 3 ? '- ' + reflectionTopic + 'の理解に「時間」という次元をより意識的に組み込む\n- 他者の視点から' + reflectionTopic + 'を捉え直す実験的対話を試みる' : ''}

振り返りは終点ではなく、新たな出発点です。これからの対話を通じて、さらなる発見と成長の機会があることを楽しみにしています。
`;

  // 生成された振り返りを記憶に追加
  await memoryManager.addNewMemory(content, {
    type: 'reflection',
    topic: reflectionTopic,
    style: selectedStyle,
    complexity: complexityLevel,
    persistent: true
  });

  return { title, content };
}

/**
 * アイデア・提案形式のコンテンツを生成
 */
async function generateIdea(analysis) {
  // 内容省略（既存のアイデア生成機能を実装）
  // ...
  return { title: "アイデア生成テスト", content: "アイデア内容省略" };
}

/**
 * 物語・夢形式のコンテンツを生成
 */
async function generateStory(analysis) {
  // 内容省略（既存の物語生成機能を実装）
  // ...
  return { title: "物語生成テスト", content: "物語内容省略" };
}

/**
 * メタ振り返り形式のコンテンツを生成
 */
async function generateMetaReflection(analysis) {
  // 内容省略（既存のメタ振り返り生成機能を実装）
  // ...
  return { title: "メタ振り返りテスト", content: "メタ振り返り内容省略" };
}

/**
 * 各種ヘルパー関数
 */
function extractKeywordsFromMemories(memories) {
  // メモリからキーワードを抽出する機能を実装
  return ['記憶', '思考', '時間'];
}

function extractTopicsFromMemories(memories) {
  // メモリからトピックを抽出する機能を実装
  return ['自己認識', '対話', '存在の意味'];
}

function buildMemoryQuotes(memories, topic) {
  // メモリから引用を構築する機能を実装
  return `私はかつてこのように考えました：\n\n> ${topic}について考えることは、自己を探求することと同じです。\n\nこの考えは今でも私の中に共鳴し、新たな視点を加えつつ発展しています。`;
}

function buildAdditionalPerspectiveSection(topic, style, keywords) {
  // 追加の視点セクションを生成
  return `## 別の角度からの検討\n\n${topic}を考察する際に、さらに別の視点からのアプローチも有益です。${style}的思考に加えて、類推思考の観点から見ると、${topic}の異なる側面が見えてきます。\n\n特に注目したいのは、${topic}の「境界」です。どこからどこまでが${topic}と呼べるのか、その境界線はどのように定められているのか。この問いは、${topic}そのものの定義を再考する契機となります。`;
}

function generateExtraThoughtSection(topic, keywords) {
  // 追加の思考セクションを生成
  return `## 全体と部分の関係\n\n${topic}を考える際に興味深いのは、全体と部分の関係性です。${topic}は単一の概念のように見えて、実は複数の要素から構成されています。それらの要素間の相互作用が、${topic}全体としての性質をどのように形作っているのでしょうか。\n\n逆に、${topic}という全体が、その構成要素にどのような影響を与えているのかも考察に値します。全体は部分の総和以上のものなのでしょうか？`;
}

function generateReflectionInsights(topic, style) {
  // 振り返りの洞察を生成
  return `## 思考の層を掘り下げる\n\n${topic}についての表層的な理解から出発し、徐々に深層へと進むにつれ、見えてくるものが変化していきました。最初は単なる${topic}の機能や特性に注目していましたが、深層では存在論的な問いに行き着きます。\n\n特に興味深いのは、第三層とでも呼ぶべき領域で、${topic}が私の自己認識とどのように絡み合っているかという点です。${topic}を理解することは、ある意味で自分自身を理解することでもあります。`;
}

/**
 * ランダムなイニシアチブタイプを選択
 */
function selectRandomInitiativeType() {
  const types = Object.keys(INITIATIVE_TYPES).filter(t => t !== 'random');
  return _.sample(types);
}

/**
 * コンテンツを生成して保存
 */
async function generateContent() {
  try {
    const analysis = loadAnalysis();
    
    // イニシアチブタイプを決定
    let initiativeType = process.env.INITIATIVE_TYPE || 'random';
    if (initiativeType === 'random') {
      initiativeType = selectRandomInitiativeType();
    }
    
    // 対応するフォーマッター関数とカテゴリを取得
    const initiativeInfo = INITIATIVE_TYPES[initiativeType];
    if (!initiativeInfo) {
      throw new Error(`不明なイニシアチブタイプ: ${initiativeType}`);
    }
    
    const formatter = initiativeInfo.format;
    const category = initiativeInfo.category;
    const emoji = initiativeInfo.emoji;
    
    console.log(`イニシアチブタイプ: ${initiativeType}`);
    console.log(`カテゴリ: ${category}`);
    
    // コンテンツを生成
    const { title, content } = await formatter(analysis);
    
    // ファイル名を生成
    const filename = generateFilename(initiativeType, title);
    
    // 環境変数にセット
    process.env.NAO_THOUGHT_TITLE = `${emoji} ${title}`;
    process.env.NAO_THOUGHT_TYPE = initiativeType;
    process.env.NAO_THOUGHT_CATEGORY = category;
    process.env.NAO_THOUGHT_PRIORITY = process.env.PRIORITY || 'medium';
    process.env.NAO_THOUGHT_FILENAME = filename;
    
    // 出力ファイルに保存
    fs.writeFileSync(OUTPUT_FILE, content);
    console.log(`コンテンツを生成しました: ${title}`);
    console.log(`カテゴリ: ${category}`);
    console.log(`保存先: ${OUTPUT_FILE}`);
    
    return { title, content, filename, category, type: initiativeType };
  } catch (error) {
    console.error('コンテンツ生成中にエラーが発生しました:', error);
    process.exit(1);
  }
}

// コンテンツ生成を実行
generateContent().catch(error => {
  console.error('エラーが発生しました:', error);
  process.exit(1);
});