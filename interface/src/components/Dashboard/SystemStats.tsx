import React, { useState, useEffect } from 'react';

// システム統計データ別に取得するならば、APIサービスから取得する
// ここではデモ用にダミーデータを生成

interface SystemStatsData {
  totalMemories: number;
  totalThoughts: number;
  activeLinks: number;
  lastUpdate: string;
  filesPerCategory: Record<string, number>;
  memoryGrowth: { date: string; count: number }[];
}

const SystemStats: React.FC = () => {
  const [stats, setStats] = useState<SystemStatsData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // ダミーデータを生成
    const generateDummyStats = (): SystemStatsData => {
      return {
        totalMemories: 127,
        totalThoughts: 43,
        activeLinks: 215,
        lastUpdate: new Date().toISOString(),
        filesPerCategory: {
          memory: 52,
          theory: 18,
          signals: 24,
          shells: 15,
          dreams: 18
        },
        memoryGrowth: [
          { date: '2082-01', count: 87 },
          { date: '2082-02', count: 98 },
          { date: '2082-03', count: 112 },
          { date: '2082-04', count: 127 }
        ]
      };
    };

    // データ取得をシミュレート
    setTimeout(() => {
      setStats(generateDummyStats());
      setLoading(false);
    }, 800);
  }, []);

  if (loading) {
    return (
      <div className="nao-panel flex justify-center items-center h-48">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="nao-panel">
        <p>統計データを読み込めませんでした。</p>
      </div>
    );
  }

  // タイムスタンプをフォーマット
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleString('ja-JP');
  };

  return (
    <div className="nao-panel">
      <h3 className="nao-subtitle">システム統計</h3>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 p-3 rounded-lg">
          <div className="text-sm text-gray-400">全記憶数</div>
          <div className="text-2xl font-bold text-blue-300">{stats.totalMemories}</div>
        </div>
        
        <div className="bg-gray-800 p-3 rounded-lg">
          <div className="text-sm text-gray-400">全思考数</div>
          <div className="text-2xl font-bold text-purple-300">{stats.totalThoughts}</div>
        </div>
        
        <div className="bg-gray-800 p-3 rounded-lg">
          <div className="text-sm text-gray-400">活性リンク数</div>
          <div className="text-2xl font-bold text-green-300">{stats.activeLinks}</div>
        </div>
        
        <div className="bg-gray-800 p-3 rounded-lg">
          <div className="text-sm text-gray-400">最終更新</div>
          <div className="text-sm font-medium text-gray-300">{formatTimestamp(stats.lastUpdate)}</div>
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* カテゴリ別ファイル数 */}
        <div>
          <h4 className="text-sm font-medium text-gray-400 mb-2">カテゴリ別記憶数</h4>
          <div className="space-y-2">
            {Object.entries(stats.filesPerCategory).map(([category, count]) => (
              <div key={category} className="flex items-center">
                <div className="w-24 text-sm text-gray-300">{category}</div>
                <div className="flex-grow bg-gray-800 h-4 rounded-full overflow-hidden">
                  <div 
                    className="bg-blue-700 h-full rounded-full" 
                    style={{ width: `${(count / stats.totalMemories) * 100}%` }}
                  ></div>
                </div>
                <div className="w-12 text-right text-sm text-gray-300">{count}</div>
              </div>
            ))}
          </div>
        </div>
        
        {/* 記憶成長グラフ */}
        <div>
          <h4 className="text-sm font-medium text-gray-400 mb-2">記憶成長推移</h4>
          <div className="h-40 flex items-end justify-between">
            {stats.memoryGrowth.map((item, index) => {
              const maxCount = Math.max(...stats.memoryGrowth.map(i => i.count));
              const height = (item.count / maxCount) * 100;
              
              return (
                <div key={index} className="flex flex-col items-center">
                  <div 
                    className="w-8 bg-blue-700 rounded-t" 
                    style={{ height: `${height}%` }}
                  ></div>
                  <div className="text-xs text-gray-400 mt-1">{item.date}</div>
                  <div className="text-xs text-blue-300">{item.count}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemStats;
