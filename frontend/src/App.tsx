import React, { useState, useEffect } from 'react';
import { Editor } from './components/Editor';
import { Preview } from './components/Preview';
import { Auth } from './components/Auth';
import { PolishResult, AntiAIResult, User, getMe, logout, saveHistory } from './services/api';

function App() {
  const [result, setResult] = useState<PolishResult | AntiAIResult | null>(null);
  const [user, setUser] = useState<User | null | undefined>(undefined);
  const [showAuth, setShowAuth] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        const currentUser = await getMe();
        setUser(currentUser);
      } else {
        setUser(null);
      }
    };
    checkAuth();
  }, []);

  const handleLogin = (loggedInUser: User | null) => {
    setUser(loggedInUser);
    setShowAuth(false);
  };

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  const handleResult = async (data: PolishResult | AntiAIResult) => {
    setResult(data);

    if (user) {
      const processedText = 'polished' in data ? data.polished : data.processed;
      const operationType = 'polished' in data ? 'polish' : 'anti_ai';
      try {
        await saveHistory(data.original, processedText, operationType);
      } catch (err) {
        console.error('Failed to save history:', err);
      }
    }
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

  if (user === undefined) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent"></div>
      </div>
    );
  }

  if (showAuth) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <Auth onLogin={handleLogin} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">论文润色工具</h1>
            <p className="text-sm text-gray-500 mt-1">AI驱动的论文润色与去AI化处理</p>
          </div>
          <div className="flex items-center gap-4">
            {user ? (
              <>
                <span className="text-sm text-gray-600">欢迎, {user.username}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  退出登录
                </button>
              </>
            ) : (
              <button
                onClick={() => setShowAuth(true)}
                className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                登录/注册
              </button>
            )}
          </div>
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
          论文润色工具 v2.1.0 | 支持 .docx/.pdf/.txt 上传 | 并行处理 | 历史记录
        </div>
      </footer>
    </div>
  );
}

export default App;
