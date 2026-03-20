import React, { useState } from 'react';
import { polishText, antiAiProcess, PolishResult, AntiAIResult, PolishStyle } from '../services/api';
import { useApi } from '../hooks/useApi';

interface EditorProps {
  onResult: (result: PolishResult | AntiAIResult) => void;
}

export const Editor: React.FC<EditorProps> = ({ onResult }) => {
  const [text, setText] = useState('');
  const [mode, setMode] = useState<'polish' | 'anti-ai'>('polish');
  const [style, setStyle] = useState<PolishStyle>('academic');
  const [aiProvider, setAiProvider] = useState('zhipuai');
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('');

  const { isLoading, error, execute } = useApi(
    mode === 'polish'
      ? () => polishText(text, style, aiProvider)
      : () => antiAiProcess(text, aiProvider),
    {
      retries: 3,
      retryDelay: 1000,
    }
  );

  const handleProcess = async () => {
    if (!text.trim()) return;

    setProgress(10);
    setStatusText('正在连接AI服务...');

    const progressInterval = setInterval(() => {
      setProgress((prev) => Math.min(prev + 10, 90));
    }, 2000);

    setStatusText(mode === 'polish' ? '正在进行润色处理...' : '正在进行去AI化处理...');

    const result = await execute();

    clearInterval(progressInterval);

    if (result) {
      setProgress(100);
      setStatusText('处理完成!');
      onResult(result);
    } else {
      setProgress(0);
      setStatusText('处理失败');
    }

    setTimeout(() => {
      setProgress(0);
      setStatusText('');
    }, 2000);
  };

  const wordCount = text.trim().split(/\s+/).filter(Boolean).length;
  const charCount = text.length;

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
      <div className="flex flex-wrap gap-4 mb-4">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">模式:</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as 'polish' | 'anti-ai')}
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
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
              onChange={(e) => setStyle(e.target.value as PolishStyle)}
              className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
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
            className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="zhipuai">智谱GLM-4</option>
            <option value="local">本地模型</option>
          </select>
        </div>
      </div>

      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="请粘贴需要处理的论文文本..."
          disabled={isLoading}
          className="w-full h-64 p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-50 resize-none"
        />
        <div className="absolute bottom-2 right-2 text-xs text-gray-400">
          {charCount} 字符 | {wordCount} 词
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error.message}
        </div>
      )}

      {isLoading && (
        <div className="mt-4 p-4 bg-blue-50 rounded-xl">
          <div className="flex items-center gap-3 mb-3">
            <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
            <span className="text-sm font-medium text-blue-700">{statusText}</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>处理进度</span>
            <span>{progress}%</span>
          </div>
        </div>
      )}

      <div className="mt-4 flex justify-between items-center">
        <button
          onClick={() => setText('')}
          disabled={isLoading || !text}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 disabled:text-gray-400"
        >
          清空
        </button>
        <button
          onClick={handleProcess}
          disabled={isLoading || !text.trim()}
          className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-md"
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
