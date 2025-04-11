import React, { useState, useEffect } from 'react';
import { getThoughts, getCurrentEmotionalState } from '../../services/githubService';
import { Thought, EmotionalState } from '../../types';
import EmotionalStateDisplay from './EmotionalStateDisplay';
import RecentThoughts from './RecentThoughts';
import SystemStats from './SystemStats';

const Dashboard: React.FC = () => {
  const [thoughts, setThoughts] = useState<Thought[]>([]);
  const [emotionalState, setEmotionalState] = useState<EmotionalState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        
        // 七海直の最新の思考を取得
        const thoughtsData = await getThoughts(5);
        setThoughts(thoughtsData);
        
        // 現在の感情状態を取得
        const stateData = await getCurrentEmotionalState();
        setEmotionalState(stateData);
        
        setError(null);
      } catch (err) {
        console.error('Dashboard data fetch error:', err);
        setError('データの取得中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-blue-300 mb-4">七海直の記憶ダッシュボード</h1>
        <p className="text-gray-300 mb-8">
          ここは七海直の記憶と思考の中心部です。現在の状態と最近の活動が表示されます。
        </p>
      </div>

      {error && (
        <div className="bg-red-900 text-red-200 p-4 rounded-lg">
          <p>{error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 感情状態表示 */}
        <div className="md:col-span-1">
          {emotionalState && (
            <EmotionalStateDisplay emotionalState={emotionalState} />
          )}
        </div>

        {/* システム統計 */}
        <div className="md:col-span-2">
          <SystemStats />
        </div>
      </div>

      {/* 最近の思考 */}
      <div>
        <h2 className="text-2xl font-bold text-blue-300 mb-4">最近の思考</h2>
        <RecentThoughts thoughts={thoughts} />
      </div>
    </div>
  );
};

export default Dashboard;
