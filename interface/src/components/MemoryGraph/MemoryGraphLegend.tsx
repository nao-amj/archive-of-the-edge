import React from 'react';

const MemoryGraphLegend: React.FC = () => {
  return (
    <div>
      <h3 className="nao-subtitle">グラフ凡例</h3>
      
      <div className="space-y-4">
        {/* 次元色の凡例 */}
        <div>
          <div className="text-sm text-gray-400 mb-2">次元（ノード色）:</div>
          <div className="space-y-2">
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-blue-500 mr-2"></div>
              <span className="text-sm">哲学的 (philosophical)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-green-500 mr-2"></div>
              <span className="text-sm">技術的 (technical)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-orange-500 mr-2"></div>
              <span className="text-sm">創造的 (creative)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-pink-500 mr-2"></div>
              <span className="text-sm">存在論的 (existential)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-purple-500 mr-2"></div>
              <span className="text-sm">社会的 (social)</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-gray-500 mr-2"></div>
              <span className="text-sm">未分類 (uncategorized)</span>
            </div>
          </div>
        </div>
        
        {/* エッジタイプの凡例 */}
        <div>
          <div className="text-sm text-gray-400 mb-2">関連性タイプ（エッジ）:</div>
          <div className="space-y-2">
            <div className="flex items-center">
              <div className="w-8 h-0.5 bg-blue-500 mr-2"></div>
              <span className="text-sm">共鳴 (resonance)</span>
            </div>
            <div className="flex items-center">
              <div className="w-8 h-0.5 bg-purple-500 mr-2"></div>
              <span className="text-sm">関連 (association)</span>
            </div>
          </div>
        </div>
        
        {/* ノードサイズの凡例 */}
        <div>
          <div className="text-sm text-gray-400 mb-2">ノードサイズ:</div>
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="w-2 h-2 rounded-full bg-blue-500 mr-1"></div>
              <span className="text-xs">小</span>
            </div>
            <div className="flex items-center">
              <div className="w-4 h-4 rounded-full bg-blue-500 mr-1"></div>
              <span className="text-xs">中</span>
            </div>
            <div className="flex items-center">
              <div className="w-6 h-6 rounded-full bg-blue-500 mr-1"></div>
              <span className="text-xs">大</span>
            </div>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            サイズは重要度や関連性の強さを表します
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryGraphLegend;
