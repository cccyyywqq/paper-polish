import React, { useRef, useCallback, useState } from 'react';

interface PreviewProps {
  original: string;
  processed: string;
  metrics?: {
    naturalness_score?: number;
    ai_detection_risk?: number;
    suggestions?: string[];
  };
}

export const Preview: React.FC<PreviewProps> = ({ original, processed, metrics }) => {
  const originalRef = useRef<HTMLDivElement>(null);
  const processedRef = useRef<HTMLDivElement>(null);
  const [syncScroll, setSyncScroll] = useState(true);
  const [viewMode, setViewMode] = useState<'side' | 'diff'>('side');

  const handleScroll = useCallback(
    (source: 'original' | 'processed') => {
      if (!syncScroll) return;

      const originalEl = originalRef.current;
      const processedEl = processedRef.current;

      if (!originalEl || !processedEl) return;

      if (source === 'original') {
        processedEl.scrollTop = originalEl.scrollTop;
      } else {
        originalEl.scrollTop = processedEl.scrollTop;
      }
    },
    [syncScroll]
  );

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      alert('已复制到剪贴板');
    } catch (err) {
      console.error('复制失败:', err);
    }
  };

  const originalParagraphs = original.split('\n\n').filter(Boolean);
  const processedParagraphs = processed.split('\n\n').filter(Boolean);

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-100 overflow-hidden">
      {/* 工具栏 */}
      <div className="flex items-center justify-between px-4 py-3 bg-gray-50 border-b">
        <div className="flex items-center gap-4">
          <h3 className="text-sm font-semibold text-gray-700">对比视图</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setViewMode('side')}
              className={`px-3 py-1 text-xs rounded ${
                viewMode === 'side'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              并排对比
            </button>
            <button
              onClick={() => setViewMode('diff')}
              className={`px-3 py-1 text-xs rounded ${
                viewMode === 'diff'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-600 hover:bg-gray-300'
              }`}
            >
              段落对比
            </button>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-gray-600">
            <input
              type="checkbox"
              checked={syncScroll}
              onChange={(e) => setSyncScroll(e.target.checked)}
              className="rounded"
            />
            同步滚动
          </label>
          <button
            onClick={() => copyToClipboard(processed)}
            className="px-3 py-1 text-xs bg-green-600 text-white rounded hover:bg-green-700"
          >
            复制结果
          </button>
        </div>
      </div>

      {/* 内容区域 */}
      {viewMode === 'side' ? (
        <div className="grid grid-cols-2 divide-x">
          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-600 flex items-center">
                <span className="w-2 h-2 bg-gray-400 rounded-full mr-2"></span>
                原文
              </h4>
              <span className="text-xs text-gray-400">{original.length} 字符</span>
            </div>
            <div
              ref={originalRef}
              onScroll={() => handleScroll('original')}
              className="h-80 overflow-y-auto p-3 bg-gray-50 rounded-lg text-sm leading-relaxed whitespace-pre-wrap"
            >
              {original || '暂无内容'}
            </div>
          </div>

          <div className="p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-600 flex items-center">
                <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                润色后
              </h4>
              <span className="text-xs text-gray-400">{processed.length} 字符</span>
            </div>
            <div
              ref={processedRef}
              onScroll={() => handleScroll('processed')}
              className="h-80 overflow-y-auto p-3 bg-green-50 rounded-lg text-sm leading-relaxed whitespace-pre-wrap"
            >
              {processed || '暂无内容'}
            </div>
          </div>
        </div>
      ) : (
        <div className="p-4 max-h-96 overflow-y-auto">
          {originalParagraphs.map((para, index) => (
            <div key={index} className="mb-4 grid grid-cols-2 gap-4">
              <div className="p-3 bg-gray-50 rounded-lg text-sm">
                <span className="text-xs text-gray-400 block mb-1">段落 {index + 1}</span>
                {para}
              </div>
              <div className="p-3 bg-green-50 rounded-lg text-sm">
                <span className="text-xs text-green-600 block mb-1">润色后</span>
                {processedParagraphs[index] || '（无对应段落）'}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 指标区域 */}
      {metrics && (
        <div className="p-4 bg-blue-50 border-t">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">处理结果分析</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {metrics.naturalness_score !== undefined && (
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <span className="text-sm text-gray-600">自然度评分</span>
                <div className="flex items-center">
                  <div className="w-24 h-2 bg-gray-200 rounded-full mr-2">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{ width: `${metrics.naturalness_score}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-semibold">{metrics.naturalness_score}/100</span>
                </div>
              </div>
            )}

            {metrics.ai_detection_risk !== undefined && (
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <span className="text-sm text-gray-600">AI检测风险</span>
                <div className="flex items-center">
                  <div className="w-24 h-2 bg-gray-200 rounded-full mr-2">
                    <div
                      className={`h-full rounded-full ${
                        metrics.ai_detection_risk > 60
                          ? 'bg-red-500'
                          : metrics.ai_detection_risk > 30
                          ? 'bg-yellow-500'
                          : 'bg-green-500'
                      }`}
                      style={{ width: `${metrics.ai_detection_risk}%` }}
                    ></div>
                  </div>
                  <span
                    className={`text-sm font-semibold ${
                      metrics.ai_detection_risk > 60
                        ? 'text-red-600'
                        : metrics.ai_detection_risk > 30
                        ? 'text-yellow-600'
                        : 'text-green-600'
                    }`}
                  >
                    {metrics.ai_detection_risk}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {metrics.suggestions && metrics.suggestions.length > 0 && (
            <div className="mt-4">
              <h5 className="text-sm font-semibold text-gray-700 mb-2">改进建议</h5>
              <ul className="space-y-1">
                {metrics.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-gray-600 flex items-start">
                    <span className="text-blue-500 mr-2">{index + 1}.</span>
                    {suggestion}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
