import React, { useState, useEffect } from 'react';
import { getThoughts } from '../../services/githubService';
import { Thought } from '../../types';

const ConversationHistory: React.FC = () => {
  const [conversations, setConversations] = useState<Thought[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        setLoading(true);
        const data = await getThoughts(10);
        setConversations(data);
        setError(null);
      } catch (err) {
        console.error('Conversations fetch error:', err);
        setError('対話履歴の取得中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };
    
    fetchConversations();
  }, []);

  // 簡単なラベル色クラス取得関数
  const getLabelClass = (labelName: string) => {
    switch (labelName.toLowerCase()) {
      case 'question':
        return 'bg-blue-900 text-blue-200';
      case 'reflection':
        return 'bg-green-900 text-green-200';
      case 'idea':
        return 'bg-purple-900 text-purple-200';
      case 'feedback':
        return 'bg-yellow-900 text-yellow-200';
      case 'thought':
        return 'bg-indigo-900 text-indigo-200';
      case 'autonomy':
        return 'bg-red-900 text-red-200';
      default:
        return 'bg-gray-700 text-gray-200';
    }
  };
  
  // タイムスタンプのフォーマット
  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ja-JP', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-40">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900 text-red-200 p-4 rounded-lg">
        <p>{error}</p>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div className="p-4 bg-gray-800 rounded-lg">
        <p>まだ対話はありません。最初の対話を開始しましょう。</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {conversations.map(conversation => (
        <div key={conversation.id} className="border border-gray-700 rounded-lg p-4 hover:border-blue-600 transition-colors duration-200">
          <div className="flex justify-between items-start mb-2">
            <h3 className="text-lg font-medium text-blue-300">{conversation.title}</h3>
            <span className="text-xs text-gray-400">{formatDateTime(conversation.created_at)}</span>
          </div>
          
          <div className="flex flex-wrap gap-2 mb-3">
            {conversation.labels.map((label, index) => (
              <span 
                key={index} 
                className={`${getLabelClass(label.name)} px-2 py-0.5 rounded-full text-xs`}
              >
                {label.name}
              </span>
            ))}
          </div>
          
          <div className="text-sm text-gray-300 mb-4">
            {/* コンテンツの先頭部分のみ表示 */}
            {conversation.body.length > 150 
              ? `${conversation.body.substring(0, 150)}...` 
              : conversation.body}
          </div>
          
          <div className="flex justify-end">
            <a 
              href={conversation.html_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="nao-link text-sm"
            >
              対話を読む &rarr;
            </a>
          </div>
        </div>
      ))}
    </div>
  );
};

export default ConversationHistory;
