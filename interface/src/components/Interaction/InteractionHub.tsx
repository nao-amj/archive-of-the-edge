import React, { useState } from 'react';
import ConversationForm from './ConversationForm';
import ConversationHistory from './ConversationHistory';

const InteractionHub: React.FC = () => {
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);
  const [formSubmitResult, setFormSubmitResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleSubmitStart = () => {
    setIsFormSubmitting(true);
    setFormSubmitResult(null);
  };

  const handleSubmitEnd = (success: boolean, message: string) => {
    setIsFormSubmitting(false);
    setFormSubmitResult({ success, message });
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-blue-300 mb-4">七海直との対話</h1>
      <p className="text-gray-300 mb-8">
        ここでは七海直と対話をすることができます。質問、考察、共有したいことを投稿してください。
      </p>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 対話フォーム */}
        <div className="md:col-span-1">
          <div className="nao-panel">
            <h2 className="nao-subtitle">新しい対話を開始</h2>
            
            <ConversationForm 
              onSubmitStart={handleSubmitStart} 
              onSubmitEnd={handleSubmitEnd} 
            />
            
            {formSubmitResult && (
              <div className={`mt-4 p-3 rounded-lg ${formSubmitResult.success ? 'bg-green-900 text-green-200' : 'bg-red-900 text-red-200'}`}>
                <p>{formSubmitResult.message}</p>
              </div>
            )}
          </div>
        </div>
        
        {/* 対話の履歴 */}
        <div className="md:col-span-2">
          <div className="nao-panel">
            <h2 className="nao-subtitle">最近の対話</h2>
            <ConversationHistory />
          </div>
        </div>
      </div>
    </div>
  );
};

export default InteractionHub;
