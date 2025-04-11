import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navbar: React.FC = () => {
  const location = useLocation();
  
  // 現在のパスが一致する場合にアクティブクラスを適用
  const getNavLinkClass = (path: string) => {
    const baseClasses = 'px-4 py-2 rounded-md font-medium transition-colors duration-200';
    const isActive = location.pathname === path;
    return isActive
      ? `${baseClasses} bg-blue-700 text-white`
      : `${baseClasses} text-gray-300 hover:bg-gray-800 hover:text-white`;
  };

  return (
    <nav className="bg-gray-900 border-b border-gray-800">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <Link to="/" className="flex items-center">
              <span className="text-2xl font-bold text-blue-400">境界のアーカイブ</span>
              <span className="ml-2 text-sm text-gray-400">| 七海直</span>
            </Link>
          </div>
          
          <div className="hidden md:flex items-center space-x-2">
            <Link to="/" className={getNavLinkClass('/')}>
              ダッシュボード
            </Link>
            <Link to="/explore" className={getNavLinkClass('/explore')}>
              記憶エクスプローラー
            </Link>
            <Link to="/graph" className={getNavLinkClass('/graph')}>
              記憶グラフ
            </Link>
            <Link to="/interaction" className={getNavLinkClass('/interaction')}>
              対話
            </Link>
          </div>
          
          <div className="flex md:hidden">
            {/* モバイルメニューは簡略化しています */}
            <button className="text-gray-300 hover:text-white">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
