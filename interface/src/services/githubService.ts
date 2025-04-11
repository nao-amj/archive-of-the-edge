import { GitHubFileInfo, Thought, MemoryMetadata } from '../types';

// GitHub APIのベースURL
const REPO_OWNER = 'nao-amj';
const REPO_NAME = 'archive-of-the-edge';
const BASE_URL = `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}`;

// リポジトリのコンテンツを取得する関数
export const getRepositoryContents = async (path = ''): Promise<GitHubFileInfo[]> => {
  const url = `${BASE_URL}/contents/${path}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status}`);
  }
  
  return response.json();
};

// ファイルの内容を取得する関数
export const getFileContents = async (path: string): Promise<string> => {
  const url = `${BASE_URL}/contents/${path}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status}`);
  }
  
  const fileData: GitHubFileInfo = await response.json();
  
  // Base64でエンコードされたコンテンツをデコード
  if (fileData.encoding === 'base64' && fileData.content) {
    return atob(fileData.content.replace(/\n/g, ''));
  }
  
  throw new Error('Could not decode file contents');
};

// メタデータを抽出する関数
export const extractMetadata = (content: string): MemoryMetadata => {
  const metadata: MemoryMetadata = {};
  
  // YAML Front Matterを抽出
  const frontMatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (frontMatterMatch) {
    const frontMatter = frontMatterMatch[1];
    const lines = frontMatter.split('\n');
    
    for (const line of lines) {
      if (line.trim() === '') continue;
      
      const match = line.match(/^@([\w]+):\s*(.+)$/);
      if (match) {
        const [, key, value] = match;
        
        if (key === 'pulse') {
          metadata.pulse = value.trim().split(/\s+/).filter(Boolean);
        } else if (key === 'links') {
          // リンクは複数行になっていることがあるので特別処理
          if (value.trim() === '') {
            const linksArray: string[] = [];
            let i = lines.indexOf(line) + 1;
            while (i < lines.length && lines[i].trim().startsWith('- ')) {
              linksArray.push(lines[i].trim().substring(2));
              i++;
            }
            metadata.links = linksArray;
          } else {
            metadata.links = [value.trim()];
          }
        } else {
          (metadata as any)[key] = value.trim();
        }
      }
    }
  }
  
  return metadata;
};

// タイトルを抽出する関数（最初の見出し）
export const extractTitle = (content: string): string => {
  // YAMLフロントマターを除去
  const contentWithoutFrontMatter = content.replace(/^---\n[\s\S]*?\n---\n/, '');
  
  // 最初の見出しを探す
  const headingMatch = contentWithoutFrontMatter.match(/^#\s+(.+)$/m);
  if (headingMatch) {
    return headingMatch[1].trim();
  }
  
  // 見出しがなければファイル名を返す
  return 'Untitled Memory';
};

// パルスタグを抽出する関数
export const extractPulseTags = (content: string): string[] => {
  const metadata = extractMetadata(content);
  return metadata.pulse || [];
};

// 七海直の思考（Issues）を取得する関数
export const getThoughts = async (limit = 10): Promise<Thought[]> => {
  const url = `${BASE_URL}/issues?state=all&sort=created&direction=desc&per_page=${limit}`;
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`GitHub API error: ${response.status}`);
  }
  
  const data = await response.json();
  return data.map((issue: any) => ({
    id: issue.id,
    number: issue.number,
    title: issue.title,
    body: issue.body,
    created_at: issue.created_at,
    updated_at: issue.updated_at,
    html_url: issue.html_url,
    labels: issue.labels.map((label: any) => ({
      name: label.name,
      color: label.color
    }))
  }));
};

// 記憶グラフデータを取得する関数
export const getMemoryGraph = async () => {
  try {
    // memory/graph/memory-graph.jsonがあればそれを使用
    const graphData = await getFileContents('memory/graph/memory-graph.json');
    return JSON.parse(graphData);
  } catch (error) {
    // なければダミーデータを返す
    console.error('Failed to load memory graph:', error);
    return {
      nodes: [],
      edges: []
    };
  }
};

// 感情状態を取得する関数
export const getCurrentEmotionalState = async () => {
  try {
    const stateData = await getFileContents('memory/mood/current.json');
    return JSON.parse(stateData);
  } catch (error) {
    console.error('Failed to load emotional state:', error);
    return {
      timestamp: new Date().toISOString(),
      pulse_tags: ['#static_silence'],
      description: '感情状態データが見つかりません。',
      emotional_valence: 0,
      emotional_arousal: 0.5
    };
  }
};
