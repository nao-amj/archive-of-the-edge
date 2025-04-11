import React from 'react';

interface DirectoryBreadcrumbProps {
  path: string;
  onPathChange: (path: string) => void;
}

const DirectoryBreadcrumb: React.FC<DirectoryBreadcrumbProps> = ({ path, onPathChange }) => {
  // パスを部分に分割
  const pathParts = path ? path.split('/').filter(Boolean) : [];
  
  // パスの各部分に対応する完全パスを生成
  const getPathForPart = (index: number) => {
    return pathParts.slice(0, index + 1).join('/');
  };
  
  // ルートディレクトリに移動
  const goToRoot = () => {
    onPathChange('');
  };
  
  // 特定のパスに移動
  const goToPath = (index: number) => {
    onPathChange(getPathForPart(index));
  };

  return (
    <div className="flex items-center text-sm flex-wrap">
      <button 
        onClick={goToRoot}
        className="text-blue-400 hover:text-blue-300 transition-colors"
      >
        root
      </button>
      
      {pathParts.map((part, index) => (
        <React.Fragment key={index}>
          <span className="mx-2 text-gray-500">/</span>
          <button 
            onClick={() => goToPath(index)}
            className="text-blue-400 hover:text-blue-300 transition-colors"
          >
            {part}
          </button>
        </React.Fragment>
      ))}
    </div>
  );
};

export default DirectoryBreadcrumb;
