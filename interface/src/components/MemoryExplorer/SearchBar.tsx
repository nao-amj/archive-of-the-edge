import React, { useState } from 'react';

interface SearchBarProps {
  onSearch: (searchTerm: string) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(searchTerm);
  };

  return (
    <form onSubmit={handleSubmit} className="flex">
      <input
        type="text"
        placeholder="ファイル名で検索..."
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
        className="nao-input flex-grow"
      />
      <button 
        type="submit" 
        className="nao-button ml-2 px-4"
      >
        検索
      </button>
    </form>
  );
};

export default SearchBar;
