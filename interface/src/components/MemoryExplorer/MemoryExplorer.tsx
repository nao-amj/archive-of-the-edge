import React, { useState } from 'react';
import RepositoryTree from './RepositoryTree';
import SearchBar from './SearchBar';
import TagFilter from './TagFilter';
import DirectoryBreadcrumb from './DirectoryBreadcrumb';

const MemoryExplorer: React.FC = () => {
  const [currentPath, setCurrentPath] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // 検索ハンドラー
  const handleSearch = (term: string) => {
    setSearchTerm(term);
  };

  // タグフィルターハンドラー
  const handleTagSelect = (tag: string) => {
    if (selectedTags.includes(tag)) {
      setSelectedTags(selectedTags.filter(t => t !== tag));
    } else {
      setSelectedTags([...selectedTags, tag]);
    }
  };

  // ディレクトリナビゲーションハンドラー
  const handlePathChange = (path: string) => {
    setCurrentPath(path);
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-blue-300 mb-4">記憶エクスプローラー</h1>
      <p className="text-gray-300 mb-8">
        七海直の記憶アーカイブを探索します。ファイルやディレクトリを選択して閲覧してください。
      </p>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* サイドバー - フィルターオプション */}
        <div className="md:col-span-1">
          <div className="nao-panel space-y-6">
            <div>
              <h3 className="nao-subtitle">検索</h3>
              <SearchBar onSearch={handleSearch} />
            </div>

            <div>
              <h3 className="nao-subtitle">パルスタグフィルター</h3>
              <TagFilter 
                tags={[
                  '#joy', '#sadness', '#clarity', '#confusion', 
                  '#boundary_thin', '#projection_active', '#static_silence'
                ]} 
                selectedTags={selectedTags} 
                onTagSelect={handleTagSelect} 
                type="pulse"
              />
            </div>

            <div>
              <h3 className="nao-subtitle">次元フィルター</h3>
              <TagFilter 
                tags={[
                  'philosophical', 'technical', 'creative', 
                  'existential', 'social'
                ]} 
                selectedTags={selectedTags} 
                onTagSelect={handleTagSelect} 
                type="dimension"
              />
            </div>
          </div>
        </div>

        {/* メインコンテンツ - ファイルエクスプローラー */}
        <div className="md:col-span-3">
          <div className="nao-panel">
            <DirectoryBreadcrumb 
              path={currentPath} 
              onPathChange={handlePathChange} 
            />

            <div className="mt-4">
              <RepositoryTree 
                path={currentPath} 
                searchTerm={searchTerm}
                selectedTags={selectedTags}
                onPathChange={handlePathChange}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemoryExplorer;
