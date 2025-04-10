/**
 * memory-manager.js - 七海直自律システム - 強化された記憶管理モジュール
 *
 * このスクリプトは記憶グラフを実装し、七海直の思考と記憶の関連付けを管理します。
 * analyze-content.jsと連携して動作します。
 */

const fs = require('fs');
const path = require('path');
const { Octokit } = require('@octokit/rest');
const yaml = require('yaml');
const natural = require('natural'); // 自然言語処理のためのライブラリ
const { v4: uuidv4 } = require('uuid'); // UUID生成

// 設定の読み込み
const CONFIG_FILE = path.join('.github', 'config', 'memory-config.json');
let config = {};

try {
  if (fs.existsSync(CONFIG_FILE)) {
    config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
  } else {
    // デフォルト設定
    config = {
      graphEnabled: true,
      relevanceThreshold: 0.6,
      maxRelatedMemories: 5,
      memoryRetentionDays: 90,
      graphStoragePath: path.join('memory', 'graph', 'memory-graph.json')
    };
    
    // 設定ファイルの保存
    fs.mkdirSync(path.dirname(CONFIG_FILE), { recursive: true });
    fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
  }
} catch (error) {
  console.error('設定ファイルの読み込みエラー:', error);
  process.exit(1);
}

// Octokit初期化（GitHub APIアクセス用）
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

/**
 * 記憶グラフクラス - 七海直の記憶の関連性を管理
 */
class MemoryGraph {
  constructor() {
    this.nodes = new Map(); // 記憶ノード
    this.edges = new Map(); // 関連性エッジ
    this.tokenizer = new natural.WordTokenizer();
    this.stemmer = natural.PorterStemmer;
  }
  
  /**
   * 新しい記憶をグラフに追加
   */
  addMemory(id, content, metadata) {
    if (!id) id = uuidv4();

    const tokens = this.tokenizeAndStem(content);
    
    this.nodes.set(id, { 
      id,
      content, 
      metadata, 
      tokens,
      connections: [],
      created: new Date(),
      lastAccessed: new Date(),
      accessCount: 0
    });
    
    // 既存の記憶と自動的に関連付け
    this.autoConnectMemory(id);
    
    return id;
  }
  
  /**
   * コンテンツをトークン化してステミング処理
   */
  tokenizeAndStem(content) {
    const tokens = this.tokenizer.tokenize(content.toLowerCase());
    return tokens.map(token => this.stemmer.stem(token));
  }
  
  /**
   * 新しい記憶を既存の記憶と自動的に関連付け
   */
  autoConnectMemory(newMemoryId) {
    const newMemory = this.nodes.get(newMemoryId);
    if (!newMemory) return;
    
    for (const [existingId, existingMemory] of this.nodes.entries()) {
      if (existingId === newMemoryId) continue;
      
      const similarity = this.calculateSimilarity(
        newMemory.tokens, 
        existingMemory.tokens
      );
      
      if (similarity > config.relevanceThreshold) {
        this.connectMemories(
          newMemoryId, 
          existingId, 
          'semantic_similarity', 
          similarity
        );
      }
    }
  }
  
  /**
   * 2つの記憶間の類似度を計算（コサイン類似度）
   */
  calculateSimilarity(tokens1, tokens2) {
    // 全てのユニークトークンを集める
    const allTokens = [...new Set([...tokens1, ...tokens2])];
    
    // 各記憶のベクトル表現を作成
    const vector1 = allTokens.map(token => tokens1.includes(token) ? 1 : 0);
    const vector2 = allTokens.map(token => tokens2.includes(token) ? 1 : 0);
    
    // コサイン類似度の計算
    let dotProduct = 0;
    let magnitude1 = 0;
    let magnitude2 = 0;
    
    for (let i = 0; i < allTokens.length; i++) {
      dotProduct += vector1[i] * vector2[i];
      magnitude1 += vector1[i] * vector1[i];
      magnitude2 += vector2[i] * vector2[i];
    }
    
    magnitude1 = Math.sqrt(magnitude1);
    magnitude2 = Math.sqrt(magnitude2);
    
    if (magnitude1 === 0 || magnitude2 === 0) return 0;
    
    return dotProduct / (magnitude1 * magnitude2);
  }
  
  /**
   * 記憶間に明示的な関連付けを追加
   */
  connectMemories(id1, id2, relationshipType, strength) {
    const edgeId = `${id1}-${id2}`;
    
    // エッジが既に存在する場合は更新
    if (this.edges.has(edgeId)) {
      const existingEdge = this.edges.get(edgeId);
      existingEdge.strength = Math.max(existingEdge.strength, strength);
      existingEdge.accessed = new Date();
      existingEdge.accessCount += 1;
      return;
    }
    
    // 新しいエッジを作成
    const edge = { 
      source: id1, 
      target: id2, 
      type: relationshipType, 
      strength, 
      created: new Date(),
      accessed: new Date(),
      accessCount: 1
    };
    
    this.edges.set(edgeId, edge);
    
    // 双方向接続の更新
    const node1 = this.nodes.get(id1);
    const node2 = this.nodes.get(id2);
    
    if (node1) node1.connections.push({ to: id2, edgeId });
    if (node2) node2.connections.push({ to: id1, edgeId });
  }
  
  /**
   * 特定の記憶に関連する記憶を探索
   */
  findRelatedMemories(id, options = {}) {
    const { 
      depthLimit = 2, 
      maxResults = config.maxRelatedMemories,
      strengthThreshold = config.relevanceThreshold
    } = options;
    
    if (!this.nodes.has(id)) return [];
    
    // BFSで関連記憶を探索
    const visited = new Set([id]);
    const queue = [{ id, depth: 0 }];
    const results = [];
    
    while (queue.length > 0) {
      const { id: currentId, depth } = queue.shift();
      
      if (depth > depthLimit) continue;
      
      const currentNode = this.nodes.get(currentId);
      
      // 開始ノード以外は結果に追加
      if (currentId !== id) {
        results.push({
          id: currentId,
          content: currentNode.content,
          metadata: currentNode.metadata,
          relevance: this.calculateRelevance(id, currentId)
        });
      }
      
      // 次の深さのノードをキューに追加
      for (const connection of currentNode.connections) {
        const edge = this.edges.get(connection.edgeId);
        
        if (edge.strength < strengthThreshold) continue;
        
        const nextId = connection.to;
        if (!visited.has(nextId)) {
          visited.add(nextId);
          queue.push({ id: nextId, depth: depth + 1 });
        }
      }
    }
    
    // 関連度でソートして結果を返す
    return results
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, maxResults);
  }
  
  /**
   * 2つの記憶間の関連度を計算
   */
  calculateRelevance(sourceId, targetId) {
    const edgeId1 = `${sourceId}-${targetId}`;
    const edgeId2 = `${targetId}-${sourceId}`;
    
    // 直接のエッジがある場合はその強度を返す
    if (this.edges.has(edgeId1)) {
      return this.edges.get(edgeId1).strength;
    }
    
    if (this.edges.has(edgeId2)) {
      return this.edges.get(edgeId2).strength;
    }
    
    // 直接のエッジがない場合は類似度を計算
    const sourceNode = this.nodes.get(sourceId);
    const targetNode = this.nodes.get(targetId);
    
    if (!sourceNode || !targetNode) return 0;
    
    return this.calculateSimilarity(
      sourceNode.tokens,
      targetNode.tokens
    );
  }
  
  /**
   * コンテキストに基づいて関連する記憶を検索
   */
  searchByContext(context, options = {}) {
    const { 
      maxResults = config.maxRelatedMemories,
      threshold = config.relevanceThreshold
    } = options;
    
    const contextTokens = this.tokenizeAndStem(context);
    const results = [];
    
    // 全ての記憶ノードと類似度を計算
    for (const [id, node] of this.nodes.entries()) {
      const similarity = this.calculateSimilarity(contextTokens, node.tokens);
      
      if (similarity >= threshold) {
        results.push({
          id,
          content: node.content,
          metadata: node.metadata,
          relevance: similarity
        });
      }
    }
    
    // アクセス情報を更新
    results.forEach(result => {
      const node = this.nodes.get(result.id);
      if (node) {
        node.lastAccessed = new Date();
        node.accessCount += 1;
      }
    });
    
    // 関連度でソートして返す
    return results
      .sort((a, b) => b.relevance - a.relevance)
      .slice(0, maxResults);
  }
  
  /**
   * 記憶グラフの永続化
   */
  serialize() {
    return {
      nodes: Array.from(this.nodes.entries()),
      edges: Array.from(this.edges.entries())
    };
  }
  
  /**
   * 永続化されたグラフデータからの復元
   */
  static deserialize(data) {
    const graph = new MemoryGraph();
    
    if (data.nodes) {
      data.nodes.forEach(([id, node]) => {
        graph.nodes.set(id, node);
      });
    }
    
    if (data.edges) {
      data.edges.forEach(([id, edge]) => {
        graph.edges.set(id, edge);
      });
    }
    
    return graph;
  }
  
  /**
   * 古くなった記憶の整理
   */
  pruneOldMemories() {
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - config.memoryRetentionDays);
    
    const nodesToRemove = [];
    
    // 削除対象の記憶を特定
    for (const [id, node] of this.nodes.entries()) {
      // 永続的なメモリはスキップ
      if (node.metadata && node.metadata.persistent) continue;
      
      // 最終アクセス日が古いものを削除
      const lastAccess = new Date(node.lastAccessed);
      if (lastAccess < cutoffDate) {
        nodesToRemove.push(id);
      }
    }
    
    // 関連するエッジと一緒に削除
    nodesToRemove.forEach(id => {
      const node = this.nodes.get(id);
      if (!node) return;
      
      // このノードに関連するエッジを削除
      node.connections.forEach(conn => {
        this.edges.delete(conn.edgeId);
        
        // 相手側のconnectionsからも削除
        const otherNode = this.nodes.get(conn.to);
        if (otherNode) {
          otherNode.connections = otherNode.connections.filter(
            c => c.edgeId !== conn.edgeId
          );
        }
      });
      
      // ノード自体を削除
      this.nodes.delete(id);
    });
    
    return nodesToRemove.length;
  }
}

/**
 * 記憶グラフのシングルトンインスタンスを取得
 */
async function getMemoryGraph() {
  // グラフが保存されていれば読み込む
  try {
    const graphPath = config.graphStoragePath;
    
    if (fs.existsSync(graphPath)) {
      const data = JSON.parse(fs.readFileSync(graphPath, 'utf-8'));
      return MemoryGraph.deserialize(data);
    }
  } catch (error) {
    console.error('記憶グラフの読み込みエラー:', error);
  }
  
  // 存在しなければ新規作成
  return new MemoryGraph();
}

/**
 * 記憶グラフを保存
 */
async function saveMemoryGraph(graph) {
  try {
    const graphPath = config.graphStoragePath;
    const graphDir = path.dirname(graphPath);
    
    if (!fs.existsSync(graphDir)) {
      fs.mkdirSync(graphDir, { recursive: true });
    }
    
    fs.writeFileSync(graphPath, JSON.stringify(graph.serialize(), null, 2));
  } catch (error) {
    console.error('記憶グラフの保存エラー:', error);
  }
}

/**
 * 記憶システムから思考生成のためのコンテキストを構築
 */
async function buildThinkingContext(analysisData) {
  // 記憶グラフを取得
  const graph = await getMemoryGraph();
  
  // 現在のコンテキストを構築（分析データに基づく）
  const currentContext = buildContextFromAnalysis(analysisData);
  
  // コンテキストに基づいて関連記憶を検索
  const relatedMemories = graph.searchByContext(currentContext, {
    maxResults: 7, // より多くの関連記憶を取得
    threshold: 0.5 // 閾値を少し下げて多様性を確保
  });
  
  // コンテキストと記憶を統合
  return {
    currentContext,
    relatedMemories,
    analysisData
  };
}

/**
 * 分析データからコンテキスト文字列を生成
 */
function buildContextFromAnalysis(analysis) {
  const contextParts = [];
  
  if (analysis.naoSettings) {
    contextParts.push(`七海直の設定: ${analysis.naoSettings.name}`);
    
    if (analysis.naoSettings.interests) {
      contextParts.push(`関心領域: ${analysis.naoSettings.interests.join(', ')}`);
    }
  }
  
  if (analysis.keywordsAndTopics && analysis.keywordsAndTopics.keywords) {
    contextParts.push(`キーワード: ${analysis.keywordsAndTopics.keywords.slice(0, 10).join(', ')}`);
  }
  
  if (analysis.recentActivity && analysis.recentActivity.recentFiles) {
    contextParts.push(`最近の活動: ${analysis.recentActivity.recentFiles
      .map(file => path.basename(file.path))
      .join(', ')}`);
  }
  
  return contextParts.join('\n');
}

/**
 * 新しい記憶を追加
 */
async function addNewMemory(content, metadata = {}) {
  // 記憶グラフを取得
  const graph = await getMemoryGraph();
  
  // 新しい記憶を追加
  const memoryId = graph.addMemory(null, content, metadata);
  
  // グラフを保存
  await saveMemoryGraph(graph);
  
  return memoryId;
}

/**
 * 自動メモリ整理プロセス
 */
async function runMemoryMaintenance() {
  console.log('記憶の整理を開始します...');
  
  const graph = await getMemoryGraph();
  const prunedCount = graph.pruneOldMemories();
  
  console.log(`${prunedCount}件の古い記憶を整理しました`);
  
  await saveMemoryGraph(graph);
  
  return prunedCount;
}

// メインエクスポート
module.exports = {
  MemoryGraph,
  getMemoryGraph,
  saveMemoryGraph,
  buildThinkingContext,
  addNewMemory,
  runMemoryMaintenance
};
