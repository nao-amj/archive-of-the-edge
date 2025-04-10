/**
 * Nao Nanami Autonomy System - Content Analyzer
 * 
 * このスクリプトはリポジトリの内容を分析し、七海直の自律的な思考や活動の生成に
 * 必要な情報を収集します。
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const yaml = require('yaml');
const fm = require('front-matter');
const _ = require('lodash');

// 結果を保存するディレクトリ
const TEMP_DIR = path.join('.github', 'temp');
if (!fs.existsSync(TEMP_DIR)) {
  fs.mkdirSync(TEMP_DIR, { recursive: true });
}

// 分析結果を保存するファイル
const ANALYSIS_FILE = path.join(TEMP_DIR, 'content-analysis.json');

/**
 * 特定のディレクトリ内のMarkdownファイルを再帰的に検索し、
 * frontmatterとコンテンツを抽出します
 */
function extractContentFromDirectory(directory) {
  if (!fs.existsSync(directory)) {
    return [];
  }

  const files = [];
  const items = fs.readdirSync(directory, { withFileTypes: true });

  for (const item of items) {
    const itemPath = path.join(directory, item.name);
    
    if (item.isDirectory()) {
      files.push(...extractContentFromDirectory(itemPath));
    } else if (item.isFile() && item.name.endsWith('.md')) {
      try {
        const content = fs.readFileSync(itemPath, 'utf-8');
        let parsedContent;
        
        try {
          // front-matterを解析
          parsedContent = fm(content);
        } catch (error) {
          // front-matterがない場合は本文のみ
          parsedContent = { attributes: {}, body: content };
        }
        
        files.push({
          path: itemPath,
          attributes: parsedContent.attributes,
          content: parsedContent.body,
          lastModified: fs.statSync(itemPath).mtime
        });
      } catch (error) {
        console.error(`Error reading file ${itemPath}:`, error);
      }
    }
  }

  return files;
}

/**
 * リポジトリ全体から重要なキーワードとトピックを抽出
 */
function extractKeywordsAndTopics(files) {
  // すべてのファイルのコンテンツを結合
  const allContent = files.map(file => file.content).join(' ');
  
  // 単純な単語頻度分析
  const words = allContent.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 3)
    .filter(word => !['this', 'that', 'with', 'from', 'have', 'were', 'they', 'their'].includes(word));
  
  // 単語の頻度をカウント
  const wordFrequency = _.countBy(words);
  
  // 頻度でソートして上位のキーワードを取得
  const keywords = Object.entries(wordFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 30)
    .map(entry => entry[0]);
  
  // タグを収集
  const tags = files
    .filter(file => file.attributes.tags)
    .flatMap(file => file.attributes.tags)
    .filter(Boolean);
  
  const uniqueTags = [...new Set(tags)];
  
  return {
    keywords,
    topics: uniqueTags
  };
}

/**
 * 最近更新されたファイルと活発なトピックを特定
 */
function identifyRecentActivity(files) {
  // 最近1週間以内に更新されたファイル
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  
  const recentFiles = files
    .filter(file => new Date(file.lastModified) > oneWeekAgo)
    .sort((a, b) => new Date(b.lastModified) - new Date(a.lastModified));
  
  return {
    recentFiles: recentFiles.slice(0, 10).map(file => ({
      path: file.path,
      lastModified: file.lastModified
    })),
    activeTopics: extractKeywordsAndTopics(recentFiles).topics
  };
}

/**
 * 七海直の基本情報と設定を取得
 */
function getNaoSettings() {
  // 設定ファイルのパスを確認
  const possibleSettingsPaths = [
    'configs/nao-settings.yml',
    'configs/nao-settings.yaml',
    'configs/nao.yml',
    'configs/nao.yaml',
    'memory/nao-settings.yml',
    'meta/nao-settings.yml'
  ];
  
  let settings = {
    name: '七海直',
    version: '1.0',
    interests: ['記憶', '時間', '物語', '自律性', 'AI哲学'],
    personality: {
      curiosity: 'high',
      creativity: 'high',
      thoughtfulness: 'high'
    }
  };
  
  for (const settingsPath of possibleSettingsPaths) {
    if (fs.existsSync(settingsPath)) {
      try {
        const content = fs.readFileSync(settingsPath, 'utf-8');
        const parsedSettings = yaml.parse(content);
        settings = { ...settings, ...parsedSettings };
        break;
      } catch (error) {
        console.error(`Error parsing settings file ${settingsPath}:`, error);
      }
    }
  }
  
  return settings;
}

/**
 * 主要ディレクトリの分析を実行
 */
function analyzeRepository() {
  const directories = [
    'memories',
    'dreams',
    'signals',
    'echoes',
    'shells',
    'theory',
    'meta'
  ];
  
  let allFiles = [];
  for (const directory of directories) {
    const files = extractContentFromDirectory(directory);
    allFiles = [...allFiles, ...files];
  }
  
  // 分析結果
  const analysis = {
    timestamp: new Date().toISOString(),
    fileCount: allFiles.length,
    naoSettings: getNaoSettings(),
    keywordsAndTopics: extractKeywordsAndTopics(allFiles),
    recentActivity: identifyRecentActivity(allFiles),
    lastCommitHash: execSync('git rev-parse HEAD').toString().trim(),
    lastCommitMessage: execSync('git log -1 --pretty=%B').toString().trim()
  };
  
  // 結果を保存
  fs.writeFileSync(ANALYSIS_FILE, JSON.stringify(analysis, null, 2));
  console.log(`分析完了。結果を ${ANALYSIS_FILE} に保存しました。`);
  
  return analysis;
}

// 分析を実行
try {
  const analysis = analyzeRepository();
  console.log(`分析された要素: ${analysis.fileCount} ファイル`);
} catch (error) {
  console.error('リポジトリ分析中にエラーが発生しました:', error);
  process.exit(1);
}
