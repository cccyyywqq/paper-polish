import React, { useState } from 'react';
import { Editor } from './components/Editor';
import { Preview } from './components/Preview';
import { PolishResult, AntiAIResult } from './services/api';

function App() {
  const [result, setResult] = useState<PolishResult | AntiAIResult | null>(null);

  const handleResult = (data: PolishResult | AntiAIResult) => {
    setResult(data);
  };

  const getProcessedText = () => {
    if (!result) return '';
    if ('polished' in result) {
      return result.polished;
    }
    return result.processed;
  };

  const getMetrics = () => {
    if (!result) return undefined;
    if ('processed' in result) {
      return {
        naturalness_score: result.naturalness_score,
        ai_detection_risk: result.ai_detection_risk,
        suggestions: result.suggestions,
      };
    }
    return {
      suggestions: result.suggestions,
    };
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">论文润色工具</h1>
          <p className="text-sm text-gray-500 mt-1">AI驱动的论文润色与去AI化处理</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-8">
          <Editor onResult={handleResult} />

          {result && (
            <Preview
              original={result.original}
              processed={getProcessedText()}
              metrics={getMetrics()}
            />
          )}
        </div>
      </main>

      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-gray-500">
          论文润色工具 v1.0.0
        </div>
      </footer>
    </div>
  );
}

export default App;
