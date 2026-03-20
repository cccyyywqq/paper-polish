import React, { useState, useCallback } from 'react';
import { polishText, antiAiProcess, PolishResult, AntiAIResult } from '../services/api';

interface EditorProps {
  onResult: (result: PolishResult | AntiAIResult) => void;
}

export const Editor: React.FC<EditorProps> = ({ onResult }) => {
  const [text, setText] = useState('');
  const [mode, setMode] = useState<'polish' | 'anti-ai'>('polish');
  const [style, setStyle] = useState('academic');
  const [aiProvider, setAiProvider] = useState('zhipuai');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');

  const handleProcess = useCallback(async () => {
    if (!text.trim()) return;

    setIsLoading(true);
    setProgress(10);
    setStatusText('正在连接AI服务...');

    try {
      setProgress(30);
      setStatusText('AI正在分析文本...');

      let result;
      if (mode === 'polish') {
        setProgress(50);
        setStatusText('正在进行润色处理...');
        result = await polishText(text, style, aiProvider);
      } else {
        setProgress(50);
        setStatusText('正在进行去AI化处理...');
        result = await antiAiProcess(text, aiProvider);
      }

      setProgress(90);
      setStatusText('正在生成结果...');
      
      await new Promise(resolve => setTimeout(resolve, 500));
      
      setProgress(100);
      setStatusText('处理完成!');
      
      onResult(result);
    } catch (error) {
      console.error('处理失败:', error);
      setStatusText('处理失败');
      alert('处理失败，请检查网络连接或API配置');
    } finally {
      setTimeout(() => {
        setIsLoading(false);
        setProgress(0);
        setStatusText('');
      }, 1000);
    }
  }, [text, mode, style, aiProvider, onResult]);

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-wrap gap-4 mb-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">模式:</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as 'polish' | 'anti-ai')}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="polish">论文润色</option>
            <option value="anti-ai">去AI化处理</option>
          </select>
        </div>

        {mode === 'polish' && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-700">风格:</label>
            <select
              value={style}
              onChange={(e) => setStyle(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="academic">学术严谨</option>
              <option value="natural">自然流畅</option>
              <option value="formal">正式规范</option>
            </select>
          </div>
        )}

        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">AI服务:</label>
          <select
            value={aiProvider}
            onChange={(e) => setAiProvider(e.target.value)}
            className="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="zhipuai">智谱GLM-4</option>
            <option value="local">本地模型</option>
          </select>
        </div>
      </div>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="请粘贴需要处理的论文文本..."
        disabled={isLoading}
        className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-100"
      />

      {isLoading && (
        <div className="mt-4 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
            <span className="text-sm font-medium text-blue-700">{statusText}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="text-right text-xs text-gray-500 mt-1">{progress}%</div>
        </div>
      )}

      <div className="mt-4 flex justify-end">
        <button
          onClick={handleProcess}
          disabled={isLoading || !text.trim()}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          {isLoading && (
            <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
          )}
          {isLoading ? '处理中...' : '开始处理'}
        </button>
      </div>
    </div>
  );
};
