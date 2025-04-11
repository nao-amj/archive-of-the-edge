import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import { getFileContents, extractMetadata, extractTitle } from '../../services/githubService';
import { MemoryMetadata } from '../../types';

const FileViewer: React.FC = () => {
  const { path: urlPath } = useParams<{ path: string }>();
  const [content, setContent] = useState<string>('');
  const [metadata, setMetadata] = useState<MemoryMetadata>({});
  const [title, setTitle] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const fetchFile = async () => {
      if (!urlPath) {
        setError('ファイルパスが指定されていません');
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        const filePath = urlPath.replace(/\/+/g, '/');
        const fileContent = await getFileContents(filePath);
        setContent(fileContent);
        
        // メタデータの抽出
        const extractedMetadata = extractMetadata(fileContent);
        setMetadata(extractedMetadata);
        
        // タイトルの抽出
        const extractedTitle = extractTitle(fileContent);
        setTitle(extractedTitle);
        
        setError(null);
      } catch (err) {
        console.error('File fetch error:', err);
        setError('ファイルの読み込み中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };
    
    fetchFile();
  }, [urlPath]);
  
  // YAMLフロントマターを除いたコンテンツを取得
  const getContentWithoutFrontMatter = () => {
    return content.replace(/^---\n[\s\S]*?\n---\n/, '');
  };
  
  // ファイルパスから親ディレクトリを取得
  const getParentDirectory = () => {
    if (!urlPath) return '/explore';
    const parts = urlPath.split('/');
    parts.pop(); // 最後の要素（ファイル名）を取り除く
    const parentPath = parts.join('/');
    return `/explore/${parentPath}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="nao-panel">
        <div className="bg-red-900 text-red-200 p-4 rounded-lg mb-4">
          <p>{error}</p>
        </div>
        <Link to="/explore" className="nao-button">エクスプローラーに戻る</Link>
      </div>
    );
  }

  return (
    <div>
      <div className="mb-4 flex items-center">
        <Link to={getParentDirectory()} className="nao-button mr-4">
          &larr; 戻る
        </Link>
        <h1 className="text-2xl font-bold text-blue-300">{title}</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* メタデータパネル */}
        <div className="md:col-span-1">
          <div className="nao-panel">
            <h3 className="nao-subtitle">メタデータ</h3>
            
            {Object.keys(metadata).length === 0 ? (
              <p className="text-gray-400">メタデータが見つかりません</p>
            ) : (
              <div className="space-y-4">
                {metadata.id && (
                  <div>
                    <div className="text-sm text-gray-400">ID</div>
                    <div className="text-blue-300">{metadata.id}</div>
                  </div>
                )}
                
                {metadata.birth && (
                  <div>
                    <div className="text-sm text-gray-400">作成日時</div>
                    <div className="text-gray-300">{metadata.birth}</div>
                  </div>
                )}
                
                {metadata.pulse && metadata.pulse.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-400">パルスタグ</div>
                    <div className="flex flex-wrap mt-1">
                      {metadata.pulse.map((tag, index) => (
                        <span key={index} className="nao-pulse-tag">{tag}</span>
                      ))}
                    </div>
                  </div>
                )}
                
                {metadata.dimension && (
                  <div>
                    <div className="text-sm text-gray-400">次元</div>
                    <div className="mt-1">
                      <span className="nao-dimension-tag">{metadata.dimension}</span>
                    </div>
                  </div>
                )}
                
                {metadata.links && metadata.links.length > 0 && (
                  <div>
                    <div className="text-sm text-gray-400">リンク</div>
                    <ul className="list-disc list-inside text-blue-400 mt-1">
                      {metadata.links.map((link, index) => (
                        <li key={index} className="text-sm">{link}</li>
                      ))}
                    </ul>
                  </div>
                )}
                
                {metadata.context && (
                  <div>
                    <div className="text-sm text-gray-400">コンテキスト</div>
                    <div className="text-gray-300">{metadata.context}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* コンテンツパネル */}
        <div className="md:col-span-3">
          <div className="nao-panel prose prose-invert prose-blue max-w-none">
            <ReactMarkdown>{getContentWithoutFrontMatter()}</ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileViewer;
