import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { handleAuthCallback, saveToken } from '../../services/authService';

const AuthCallback: React.FC = () => {
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const processAuth = async () => {
      // URLからコードとステートパラメータを抽出
      const params = new URLSearchParams(location.search);
      const code = params.get('code');
      const state = params.get('state');

      if (!code || !state) {
        setError('認証パラメータが不足しています。');
        return;
      }

      try {
        // GitHub認証処理
        const token = await handleAuthCallback(code, state);
        saveToken(token);
        
        // 成功したらダッシュボードにリダイレクト
        navigate('/');
      } catch (err) {
        console.error('Authentication error:', err);
        setError('認証処理中にエラーが発生しました。もう一度お試しください。');
      }
    };

    processAuth();
  }, [location, navigate]);

  if (error) {
    return (
      <div className="flex justify-center items-center h-screen">
        <div className="nao-panel max-w-md">
          <h2 className="nao-title text-red-300">認証エラー</h2>
          <p className="text-red-200 mb-4">{error}</p>
          <button 
            onClick={() => navigate('/')}
            className="nao-button"
          >
            ホームに戻る
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center h-screen">
      <div className="nao-panel max-w-md">
        <h2 className="nao-title">認証処理中...</h2>
        <div className="flex justify-center my-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
        <p className="text-center text-gray-400">GitHub認証を処理しています。このページを閉じないでください。</p>
      </div>
    </div>
  );
};

export default AuthCallback;
