import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 429) {
      throw new Error('请求过于频繁，请稍后再试');
    }
    if (error.response?.status === 500) {
      throw new Error('服务器错误，请稍后再试');
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请检查网络连接');
    }
    throw error;
  }
);

export type PolishStyle = 'academic' | 'natural' | 'formal';

export interface PolishResult {
  original: string;
  polished: string;
  grammar_corrected?: string;
  suggestions: string[];
  success: boolean;
  message: string;
}

export interface AntiAIResult {
  original: string;
  processed: string;
  naturalness_score: number;
  ai_detection_risk: number;
  suggestions: string[];
  success: boolean;
  message: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface HistoryItem {
  id: number;
  original_text: string;
  polished_text: string;
  operation_type: string;
  style?: string;
  created_at: string;
}

export async function polishText(
  text: string,
  style: PolishStyle = 'academic',
  aiProvider: string = 'zhipuai'
): Promise<PolishResult> {
  const response = await api.post<PolishResult>('/polish/text', {
    text,
    style,
    ai_provider: aiProvider,
  });
  return response.data;
}

export async function antiAiProcess(
  text: string,
  aiProvider: string = 'zhipuai'
): Promise<AntiAIResult> {
  const response = await api.post<AntiAIResult>('/anti-ai/process', {
    text,
    ai_provider: aiProvider,
  });
  return response.data;
}

export async function analyzeAiRisk(text: string) {
  const response = await api.post('/anti-ai/analyze', { text });
  return response.data;
}

export async function batchPolish(
  texts: string[],
  style: PolishStyle = 'academic',
  aiProvider: string = 'zhipuai'
) {
  const response = await api.post('/polish/batch', {
    texts,
    style,
    ai_provider: aiProvider,
  });
  return response.data;
}

export async function register(username: string, email: string, password: string): Promise<User> {
  const response = await api.post<User>('/auth/register', { username, email, password });
  return response.data;
}

export async function login(username: string, password: string): Promise<{ access_token: string }> {
  const response = await api.post('/auth/login', { username, password });
  localStorage.setItem('token', response.data.access_token);
  return response.data;
}

export async function getMe(): Promise<User | null> {
  try {
    const response = await api.get<User>('/auth/me');
    return response.data;
  } catch {
    return null;
  }
}

export function logout() {
  localStorage.removeItem('token');
}

export async function saveHistory(
  originalText: string,
  polishedText: string,
  operationType: string,
  style?: string
): Promise<HistoryItem> {
  const response = await api.post<HistoryItem>('/auth/history', {
    original_text: originalText,
    polished_text: polishedText,
    operation_type: operationType,
    style,
  });
  return response.data;
}

export async function getHistory(): Promise<HistoryItem[]> {
  const response = await api.get<HistoryItem[]>('/auth/history');
  return response.data;
}

export interface ProgressData {
  progress: number;
  total: number;
  status: string;
  results?: string[];
  result?: PolishResult;
  error?: string;
}

export async function polishTextWithProgress(
  text: string,
  style: PolishStyle = 'academic',
  aiProvider: string = 'zhipuai',
  onProgress?: (data: ProgressData) => void
): Promise<PolishResult> {
  const response = await api.post('/polish/text-with-progress', {
    text,
    style,
    ai_provider: aiProvider,
  });

  const { task_id } = response.data;

  return new Promise((resolve, reject) => {
    const eventSource = new EventSource(`/api/progress/stream/${task_id}`);

    eventSource.onmessage = (event) => {
      try {
        const data: ProgressData = JSON.parse(event.data);
        onProgress?.(data);

        if (data.status === 'completed' && data.result) {
          eventSource.close();
          resolve(data.result);
        } else if (data.status === 'failed') {
          eventSource.close();
          reject(new Error('Processing failed'));
        }
      } catch (e) {
        console.error('Failed to parse progress data:', e);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      reject(new Error('SSE connection failed'));
    };
  });
}
