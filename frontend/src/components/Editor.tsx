import React, { useState, useMemo, useRef } from 'react';
import { polishText, polishTextWithProgress, antiAiProcess, uploadFile, PolishResult, AntiAIResult, PolishStyle, ProgressData } from '../services/api';

interface EditorProps {
  onResult: (result: PolishResult | AntiAIResult) => void;
}

export const Editor: React.FC<EditorProps> = ({ onResult }) => {
  const [text, setText] = useState('');
  const [mode, setMode] = useState<'polish' | 'anti-ai'>('polish');
  const [style, setStyle] = useState<PolishStyle>('academic');
  const [aiProvider, setAiProvider] = useState('zhipuai');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusText, setStatusText] = useState('');
  const [processedChunks, setProcessedChunks] = useState(0);
  const [totalChunks, setTotalChunks] = useState(0);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const textChunks = useMemo(() => {
    const paragraphs = text.split(/\n\s*\n/).filter(p => p.trim());
    return paragraphs.length || (text.trim() ? 1 : 0);
  }, [text]);

  const progress = totalChunks > 0 ? Math.round((processedChunks / totalChunks) * 100) : 0;

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedTypes = ['.docx', '.pdf', '.txt'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();

    if (!allowedTypes.includes(fileExt)) {
      setError(`不支持的文件类型。支持: ${allowedTypes.join(', ')}`);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setError('文件大小不能超过10MB');
      return;
    }

    setIsUploading(true);
    setError(null);
    setStatusText('正在解析文件...');

    try {
      const data = await uploadFile(file);
      setText(data.text);
      setUploadedFile(data.filename);
      setStatusText(`已加载: ${data.filename} (${data.char_count} 字符)`);
    } catch (err) {
      setError(err instanceof Error ? err.message : '文件上传失败');
    } finally {
      setIsUploading(false);
      setTimeout(() => setStatusText(''), 3000);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleProcess = async () => {
    if (!text.trim()) return;

    setIsLoading(true);
    setError(null);
    setProcessedChunks(0);
    setTotalChunks(textChunks);
    setStatusText('正在连接AI服务...');

    try {
      let result;
      if (mode === 'polish' && textChunks > 1) {
        setStatusText('正在并行润色处理...');
        result = await polishTextWithProgress(
          text,
          style,
          aiProvider,
          (data: ProgressData) => {
            setProcessedChunks(data.progress);
            setTotalChunks(data.total);
            if (data.total > 1) {
              setStatusText(`正在处理第 ${data.progress}/${data.total} 段...`);
            }
          }
        );
      } else if (mode === 'polish') {
        setStatusText('正在润色处理...');
        result = await polishText(text, style, aiProvider);
      } else {
        setStatusText('正在进行去AI化处理...');
        result = await antiAiProcess(text, aiProvider);
      }

      setProcessedChunks(totalChunks);
      setStatusText('处理完成!');
      onResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : '处理失败');
      setStatusText('处理失败');
    } finally {
      setTimeout(() => {
        setIsLoading(false);
        setStatusText('');
        setProcessedChunks(0);
        setTotalChunks(0);
      }, 2000);
    }
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
            <option value="local" disabled>本地模型 (暂未开放)</option>
          </select>
        </div>
      </div>

      <div className="mb-4 p-4 border-2 border-dashed border-gray-300 rounded-xl hover:border-blue-400 transition-colors">
        <input
          ref={fileInputRef}
          type="file"
          accept=".docx,.pdf,.txt"
          onChange={handleFileUpload}
          className="hidden"
          id="file-upload"
        />
        <label
          htmlFor="file-upload"
          className="flex items-center justify-center gap-2 cursor-pointer"
        >
          {isUploading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
              <span className="text-sm text-blue-600">{statusText}</span>
            </>
          ) : (
            <>
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <span className="text-sm text-gray-600">
                {uploadedFile ? `已加载: ${uploadedFile}` : '点击上传文件 (.docx, .pdf, .txt)'}
              </span>
            </>
          )}
        </label>
      </div>

      <div className="relative">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="请粘贴需要处理的论文文本...&#10;&#10;或上传 .docx / .pdf / .txt 文件&#10;&#10;支持自动分段并行处理，大文本会按段落拆分同时处理！"
          disabled={isLoading}
          className="w-full h-64 p-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm disabled:bg-gray-50 resize-none"
        />
        <div className="absolute bottom-2 right-2 text-xs text-gray-400">
          {charCount} 字符 | {wordCount} 词 | {textChunks} 段
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="mt-4 p-4 bg-blue-50 rounded-xl">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
              <span className="text-sm font-medium text-blue-700">{statusText}</span>
            </div>
            {totalChunks > 1 && (
              <span className="text-xs text-blue-600 bg-blue-100 px-2 py-1 rounded">
                并行处理 {totalChunks} 段
              </span>
            )}
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-2">
            <span>{totalChunks > 1 ? `已处理 ${processedChunks}/${totalChunks} 段` : '处理进度'}</span>
            <span>{progress}%</span>
          </div>
        </div>
      )}

      <div className="mt-4 flex justify-between items-center">
        <button
          onClick={() => {
            setText('');
            setUploadedFile(null);
          }}
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
