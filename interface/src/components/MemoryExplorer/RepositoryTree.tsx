import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRepositoryContents, getFileContents, extractPulseTags, extractMetadata } from '../../services/githubService';
import { GitHubFileInfo } from '../../types';

interface RepositoryTreeProps {
  path: string;
  searchTerm?: string;
  selectedTags?: string[];
  onPathChange: (path: string) => void;
}

const RepositoryTree: React.FC<RepositoryTreeProps> = ({ 
  path, 
  searchTerm = '', 
  selectedTags = [],
  onPathChange 
}) => {
  const [contents, setContents] = useState<GitHubFileInfo[]>([]);
  const [filteredContents, setFilteredContents] = useState<GitHubFileInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // ファイルとディレクトリの取得
  useEffect(() => {
    const fetchContents = async () => {
      try {
        setLoading(true);
        const data = await getRepositoryContents(path);
        setContents(data);
        setFilteredContents(data);
        setError(null);
      } catch (err) {
        console.error('Repository contents fetch error:', err);
        setError('リポジトリの内容を取得中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };
    
    fetchContents();
  }, [path]);
  
  // 検索とタグフィルターの適用
  useEffect(() => {
    const applyFilters = async () => {
      if (!contents.length) return;
      
      // 検索語がなくタグも選択されていない場合はフィルタリングしない
      if (!searchTerm && selectedTags.length === 0) {
        setFilteredContents(contents);
        return;
      }
      
      setLoading(true);
      
      try {
        // 名前でのフィルタリングは簡単
        let filtered = contents.filter(item => {
          const nameMatch = item.name.toLowerCase().includes(searchTerm.toLowerCase());
          return nameMatch || item.type === 'dir'; // ディレクトリは常に表示
        });
        
        // タグフィルターがある場合はファイルの内容を確認する必要がある
        if (selectedTags.length > 0) {
          // ファイルのみを対象に、MDファイルのみをフィルタリング
          const fileResults = await Promise.all(
            filtered
              .filter(item => item.type === 'file' && item.name.endsWith('.md'))
              .map(async file => {
                try {
                  const fullPath = path ? `${path}/${file.name}` : file.name;
                  const content = await getFileContents(fullPath);
                  const metadata = extractMetadata(content);
                  
                  // パルスタグに基づくフィルタリング
                  const pulseTags = metadata.pulse || [];
                  const dimension = metadata.dimension || '';
                  
                  // 選択されたタグがすべて含まれているかチェック
                  const matchesTags = selectedTags.every(tag => {
                    if (tag.startsWith('#')) {
                      return pulseTags.includes(tag);
                    } else {
                      return dimension === tag;
                    }
                  });
                  
                  return { file, matches: matchesTags };
                } catch (error) {
                  console.error(`Error processing file ${file.name}:`, error);
                  return { file, matches: false };
                }
              })
          );
          
          // 一致するファイルのみを取得
          const matchingFiles = fileResults
            .filter(result => result.matches)
            .map(result => result.file);
          
          // ディレクトリと一致するファイルを結合
          filtered = [
            ...filtered.filter(item => item.type === 'dir'),
            ...matchingFiles
          ];
        }
        
        setFilteredContents(filtered);
      } catch (err) {
        console.error('Filter application error:', err);
        setError('フィルターの適用中にエラーが発生しました');
      } finally {
        setLoading(false);
      }
    };
    
    applyFilters();
  }, [contents, searchTerm, selectedTags, path]);
  
  // ディレクトリの移動ハンドラー
  const handleDirectoryClick = (dirPath: string) => {
    onPathChange(dirPath);
  };
  
  // ファイルタイプに基づいてアイコンを返す
  const getFileIcon = (fileName: string) => {
    if (fileName.endsWith('.md')) return '📄';
    if (fileName.endsWith('.json')) return '🔧';
    if (fileName.endsWith('.yml') || fileName.endsWith('.yaml')) return '⚙️';
    if (fileName.endsWith('.txt')) return '📝';
    if (fileName.endsWith('.nxs')) return '🧩';
    if (fileName.endsWith('.signal')) return '📡';
    if (fileName.endsWith('.thought')) return '💭';
    return '📄';
  };

  if (loading && contents.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
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

  return (
    <div>
      {loading && (
        <div className="mb-4 p-2 bg-blue-900 bg-opacity-20 text-blue-300 rounded">
          フィルターを適用中...
        </div>
      )}
      
      {filteredContents.length === 0 ? (
        <div className="p-4 bg-gray-800 rounded-lg">
          <p>一致するファイルが見つかりません。</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2">
          {filteredContents.map((item, index) => (
            <div key={index} className="p-2 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors duration-200">
              {item.type === 'dir' ? (
                <button 
                  onClick={() => handleDirectoryClick(item.path)}
                  className="w-full text-left flex items-center p-2"
                >
                  <span className="text-2xl mr-2">📁</span>
                  <span className="text-blue-300">{item.name}</span>
                </button>
              ) : (
                <Link 
                  to={`/explore/${item.path}`}
                  className="w-full text-left flex items-center p-2"
                >
                  <span className="text-2xl mr-2">{getFileIcon(item.name)}</span>
                  <span>{item.name}</span>
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default RepositoryTree;
