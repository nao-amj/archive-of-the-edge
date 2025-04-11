import React, { useState } from 'react';

interface ConversationFormProps {
  onSubmitStart: () => void;
  onSubmitEnd: (success: boolean, message: string) => void;
}

const ConversationForm: React.FC<ConversationFormProps> = ({ onSubmitStart, onSubmitEnd }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [type, setType] = useState('question');
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title.trim() || !content.trim()) {
      onSubmitEnd(false, 'タイトルと内容を入力してください');
      return;
    }
    
    onSubmitStart();
    
    try {
      // GitHub Issues APIへの投稿は実装されていません
      // 実際にはここに GitHub APIを使ってイシューを作成するコードを実装する
      
      // デモ・ダミーのレスポンス
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // 成功時の処理
      onSubmitEnd(true, '対話が正常に投稿されました。七海直が近いうちに回答します。');
      
      // フォームをリセット
      setTitle('');
      setContent('');
      setType('question');
      
    } catch (error) {
      console.error('Conversation submission error:', error);
      onSubmitEnd(false, '投稿中にエラーが発生しました。もう一度お試しください。');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="title" className="block text-sm text-gray-400 mb-1">タイトル</label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="対話のタイトルを入力してください"
          className="nao-input w-full"
          required
        />
      </div>
      
      <div>
        <label htmlFor="content" className="block text-sm text-gray-400 mb-1">内容</label>
        <textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="質問や考察を入力してください"
          className="nao-input w-full h-40"
          required
        ></textarea>
        <p className="text-xs text-gray-400 mt-1">
          Markdown形式が使用できます
        </p>
      </div>
      
      <div>
        <label htmlFor="type" className="block text-sm text-gray-400 mb-1">タイプ</label>
        <select
          id="type"
          value={type}
          onChange={(e) => setType(e.target.value)}
          className="nao-input w-full"
        >
          <option value="question">質問</option>
          <option value="reflection">内省・考察</option>
          <option value="idea">アイデア</option>
          <option value="feedback">フィードバック</option>
        </select>
      </div>
      
      <button type="submit" className="nao-button w-full">
        対話を開始する
      </button>
    </form>
  );
};

export default ConversationForm;
