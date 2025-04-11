import React from 'react';

interface TagFilterProps {
  tags: string[];
  selectedTags: string[];
  onTagSelect: (tag: string) => void;
  type: 'pulse' | 'dimension';
}

const TagFilter: React.FC<TagFilterProps> = ({ tags, selectedTags, onTagSelect, type }) => {
  const getTagClass = (tag: string) => {
    const baseClass = type === 'pulse' ? 'nao-pulse-tag' : 'nao-dimension-tag';
    const selected = selectedTags.includes(tag);
    return selected ? `${baseClass} opacity-100 ring-2 ring-offset-2 ring-offset-gray-900` : `${baseClass} opacity-70`;
  };

  return (
    <div className="flex flex-wrap gap-1 mt-2">
      {tags.map((tag, index) => (
        <button
          key={index}
          onClick={() => onTagSelect(tag)}
          className={getTagClass(tag)}
        >
          {tag}
        </button>
      ))}
    </div>
  );
};

export default TagFilter;
