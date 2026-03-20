import React from 'react';

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
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <span className="w-3 h-3 bg-gray-400 rounded-full mr-2"></span>
            原文
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg border border-gray-200 min-h-[200px] text-sm leading-relaxed">
            {original || '暂无内容'}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
            处理后
          </h3>
          <div className="bg-green-50 p-4 rounded-lg border border-green-200 min-h-[200px] text-sm leading-relaxed">
            {processed || '暂无内容'}
          </div>
        </div>
      </div>

      {metrics && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h4 className="text-md font-semibold text-gray-800 mb-3">处理结果分析</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {metrics.naturalness_score !== undefined && (
              <div className="flex items-center justify-between p-3 bg-white rounded-lg">
                <span className="text-sm text-gray-600">自然度评分</span>
                <div className="flex items-center">
                  <div className="w-32 h-2 bg-gray-200 rounded-full mr-3">
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
                  <div className="w-32 h-2 bg-gray-200 rounded-full mr-3">
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
              <ul className="list-disc list-inside space-y-1">
                {metrics.suggestions.map((suggestion, index) => (
                  <li key={index} className="text-sm text-gray-600">
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
