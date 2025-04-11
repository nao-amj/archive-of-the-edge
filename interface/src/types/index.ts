// GitHub APIのレスポンス型
export interface GitHubFileInfo {
  name: string;
  path: string;
  sha: string;
  size: number;
  url: string;
  html_url: string;
  git_url: string;
  download_url: string | null;
  type: 'file' | 'dir';
  content?: string;
  encoding?: string;
}

// メモリーファイルのメタデータ
export interface MemoryMetadata {
  id?: string;
  birth?: string;
  pulse?: string[];
  dimension?: string;
  links?: string[];
  context?: string;
}

// 記憶ノード型（グラフ表示用）
export interface MemoryNode {
  id: string;
  path: string;
  title: string;
  type: string;
  pulse?: string[];
  dimension?: string;
  size?: number;
}

// 記憶間の関連性（グラフのエッジ）
export interface MemoryEdge {
  source: string;
  target: string;
  type: string;
  strength?: number;
}

// 記憶グラフ全体
export interface MemoryGraph {
  nodes: MemoryNode[];
  edges: MemoryEdge[];
}

// 七海直の思考（GitHub Issue）
export interface Thought {
  id: number;
  number: number;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
  html_url: string;
  labels: {
    name: string;
    color: string;
  }[];
}

// 感情状態
export interface EmotionalState {
  timestamp: string;
  pulse_tags: string[];
  description: string;
  emotional_valence: number;  // -1.0 (negative) to 1.0 (positive)
  emotional_arousal: number;  // 0.0 (calm) to 1.0 (excited)
}
