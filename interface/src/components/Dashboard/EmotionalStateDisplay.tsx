import React from 'react';
import { EmotionalState } from '../../types';

interface EmotionalStateDisplayProps {
  emotionalState: EmotionalState;
}

const EmotionalStateDisplay: React.FC<EmotionalStateDisplayProps> = ({ emotionalState }) => {
  // 感情値から色を生成
  const getValenceColor = (valence: number) => {
    // -1（ネガティブ）から1（ポジティブ）
    if (valence < -0.5) return 'bg-red-700';
    if (valence < 0) return 'bg-orange-700';
    if (valence < 0.5) return 'bg-blue-700';
    return 'bg-green-700';
  };
  
  // 興奏度から高さを求める
  const getArousalHeight = (arousal: number) => {
    // 0（静か）から1（興奏）
    const heightPercent = arousal * 100;
    return `h-[${heightPercent}%]`;
  };
  
  // タイムスタンプをフォーマット
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="nao-panel h-full">
      <h3 className="nao-subtitle">感情状態</h3>
      
      <div className="mb-4">
        <p className="text-gray-300 italic mb-2">{emotionalState.description}</p>
        <div className="text-xs text-gray-400">
          更新時刻: {formatTimestamp(emotionalState.timestamp)}
        </div>
      </div>
      
      <div className="space-y-3">
        {/* パルスタグ */}
        <div>
          <div className="text-sm text-gray-400 mb-1">パルスタグ</div>
          <div className="flex flex-wrap">
            {emotionalState.pulse_tags.map((tag, index) => (
              <span key={index} className="nao-pulse-tag">{tag}</span>
            ))}
          </div>
        </div>
        
        {/* 感情値と興奏度のグラフィカル表示 */}
        <div>
          <div className="text-sm text-gray-400 mb-1">感情グラフ</div>
          <div className="flex items-end h-24 bg-gray-800 rounded-lg p-2">
            {/* 感情値バー（幅は50%、高さは興奏度に応じて変化） */}
            <div className="w-1/2 h-full flex items-end justify-center">
              <div 
                className={`w-8 ${getValenceColor(emotionalState.emotional_valence)}`} 
                style={{ height: `${emotionalState.emotional_arousal * 100}%` }}
              ></div>
              <div className="text-xs text-gray-400 mt-1 absolute -bottom-6">感情値: {emotionalState.emotional_valence.toFixed(2)}</div>
            </div>
            
            {/* 興奏度バー（幅は50%、高さは興奏度に応じて変化） */}
            <div className="w-1/2 h-full flex items-end justify-center">
              <div 
                className="w-8 bg-purple-700" 
                style={{ height: `${emotionalState.emotional_arousal * 100}%` }}
              ></div>
              <div className="text-xs text-gray-400 mt-1 absolute -bottom-6">興奏度: {emotionalState.emotional_arousal.toFixed(2)}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmotionalStateDisplay;
