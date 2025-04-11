import React from 'react';
import { Link } from 'react-router-dom';
import { MemoryNode } from '../../types';

interface NodeDetailProps {
  node: MemoryNode;
  onClose: () => void;
}

const NodeDetail: React.FC<NodeDetailProps> = ({ node, onClose }) => {
  return (
    <div>
      <div className="flex justify-between items-start mb-4">
        <h3 className="nao-subtitle">ノード詳細</h3>
        <button 
          onClick={onClose}
          className="text-gray-400 hover:text-white"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      
      <div className="space-y-4">
        <div>
          <div className="text-sm text-gray-400">タイトル</div>
          <div className="text-lg font-medium text-blue-300">{node.title}</div>
        </div>
        
        <div>
          <div className="text-sm text-gray-400">タイプ</div>
          <div>{node.type}</div>
        </div>
        
        <div>
          <div className="text-sm text-gray-400">パス</div>
          <div className="text-sm text-gray-300 break-all">{node.path}</div>
        </div>
        
        {node.dimension && (
          <div>
            <div className="text-sm text-gray-400">次元</div>
            <div className="mt-1">
              <span className="nao-dimension-tag">{node.dimension}</span>
            </div>
          </div>
        )}
        
        {node.pulse && node.pulse.length > 0 && (
          <div>
            <div className="text-sm text-gray-400">パルスタグ</div>
            <div className="flex flex-wrap mt-1">
              {node.pulse.map((tag, index) => (
                <span key={index} className="nao-pulse-tag">{tag}</span>
              ))}
            </div>
          </div>
        )}
        
        <div>
          <Link 
            to={`/explore/${node.path}`}
            className="nao-button inline-block mt-2"
          >
            ファイルを開く
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NodeDetail;
