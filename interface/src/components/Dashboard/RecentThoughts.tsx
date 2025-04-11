import React from 'react';
import { Thought } from '../../types';

interface RecentThoughtsProps {
  thoughts: Thought[];
}

const RecentThoughts: React.FC<RecentThoughtsProps> = ({ thoughts }) => {
  // タイムスタンプをフォーマット
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  };

  // マークダウンの最初の数行を抜粋する
  const extractSummary = (body: string, maxLength = 150) => {
    // コードブロックやリストを除去
    const cleanText = body
      .replace(/```[\s\S]*?```/g, '') // コードブロックを除去
      .replace(/^[\*\-] .*/gm, '')    // リストを除去
      .replace(/^#+\s.*/gm, '')      // 見出しを除去
      .replace(/!?\[.*?\]\(.*?\)/g, '') // リンクと画像を除去
      .trim();
    
    // 空行でない最初のパラグラフを取得
    const firstParagraph = cleanText.split('\n\n')[0].trim();
    
    // 文字数制限
    if (firstParagraph.length <= maxLength) {
      return firstParagraph;
    }
    
    return firstParagraph.substring(0, maxLength) + '...';
  };
  
  // ラベルの色クラスを設定
  const getLabelColorClass = (label: string, color: string) => {
    // ラベル名に基づいたクラスを返すことも可能
    switch (label.toLowerCase()) {
      case 'thought':
        return 'bg-blue-900 text-blue-200';
      case 'question':
        return 'bg-purple-900 text-purple-200';
      case 'reflection':
        return 'bg-green-900 text-green-200';
      case 'high':
        return 'bg-red-900 text-red-200';
      case 'medium':
        return 'bg-yellow-900 text-yellow-200';
      case 'low':
        return 'bg-gray-700 text-gray-200';
      default:
        return 'bg-gray-800 text-gray-200';
    }
  };

  return (
    <div className="space-y-4">
      {thoughts.length === 0 ? (
        <div className="nao-panel">
          <p>思考が見つかりません。</p>
        </div>
      ) : (
        thoughts.map(thought => (
          <div key={thought.id} className="nao-panel hover:border-blue-600 transition-colors duration-200">
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-xl font-semibold text-blue-300">{thought.title}</h3>
              <span className="text-sm text-gray-400">{formatTimestamp(thought.created_at)}</span>
            </div>
            
            <p className="text-gray-300 mb-3">{extractSummary(thought.body)}</p>
            
            <div className="flex flex-wrap items-center justify-between">
              <div className="flex flex-wrap gap-2">
                {thought.labels.map((label, index) => (
                  <span 
                    key={index} 
                    className={`${getLabelColorClass(label.name, label.color)} px-2 py-1 rounded text-xs`}
                  >
                    {label.name}
                  </span>
                ))}
              </div>
              
              <a 
                href={thought.html_url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="nao-link text-sm"
              >
                詳細を見る &rarr;
              </a>
            </div>
          </div>
        ))
      )}
    </div>
  );
};

export default RecentThoughts;
