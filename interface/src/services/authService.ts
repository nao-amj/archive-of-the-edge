// GitHub OAuth認証を安全に処理するためのサービス

// GitHub OAuth設定
const CLIENT_ID = process.env.REACT_APP_GITHUB_CLIENT_ID || '';
const REDIRECT_URI = `${window.location.origin}/callback`;
const SCOPES = ['repo', 'read:user'];

// GitHub OAuth認証のためのURL生成
export const getAuthorizationUrl = (): string => {
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    scope: SCOPES.join(' '),
    state: generateRandomState(),
  });
  
  return `https://github.com/login/oauth/authorize?${params.toString()}`;
};

// ランダムな状態文字列の生成（CSRFトークンとして機能）
const generateRandomState = (): string => {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
};

// 認証コールバックの処理
export const handleAuthCallback = async (code: string, state: string): Promise<string> => {
  // セキュリティのため、トークン交換は実際のプロダクションではサーバーサイドで行うべき
  // ここでは、GitHub Actions経由でトークンを取得し、サーバーレス関数を使用することを想定
  
  // NOTE: このコードはプレースホルダーです
  // 実際の実装はバックエンド関数またはプロキシサーバーで処理する必要がある
  const response = await fetch('/.netlify/functions/github-oauth', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code, state })
  });
  
  if (!response.ok) {
    throw new Error('認証処理中にエラーが発生しました');
  }
  
  const data = await response.json();
  return data.access_token;
};

// トークンのセッションストレージへの保存
export const saveToken = (token: string): void => {
  sessionStorage.setItem('github_token', token);
};

// トークンの取得
export const getToken = (): string | null => {
  return sessionStorage.getItem('github_token');
};

// トークンのクリア
export const clearToken = (): void => {
  sessionStorage.removeItem('github_token');
};

// 認証状態のチェック
export const isAuthenticated = (): boolean => {
  return !!getToken();
};
