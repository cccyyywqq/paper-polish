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
  (error: AxiosError<{ message?: string; details?: unknown }>) => {
    const status = error.response?.status;
    const message = error.response?.data?.message || error.message;

    if (status === 429) {
      throw new Error('请求过于频繁，请稍后再试');
    }
    if (status === 401) {
      localStorage.removeItem('token');
      throw new Error('登录已过期，请重新登录');
    }
    if (status === 413) {
      throw new Error('文件大小超过限制');
    }
    if (status === 422) {
      throw new Error(message || '请求参数错误');
    }
    if (status === 500) {
      throw new Error('服务器错误，请稍后再试');
    }
    if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请检查网络连接');
    }
    throw new Error(message || '请求失败');
  }
);

export type PolishStyle = 'academic' | 'natural' | 'formal';

export interface ApiResponse {
  success: boolean;
  message: string;
}

export interface PolishResult extends ApiResponse {
  original: string;
  polished: string;
  grammar_corrected?: string;
  suggestions: string[];
}

export interface AntiAIResult extends ApiResponse {
  original: string;
  processed: string;
  naturalness_score: number;
  ai_detection_risk: number;
  suggestions: string[];
}

export interface AnalyzeResult {
  ai_detection_risk: number;
  naturalness_score: number;
  risk_level: 'low' | 'medium' | 'high';
}

export interface BatchPolishResult extends ApiResponse {
  results: string[];
}

export interface User extends ApiResponse {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

export interface TokenResult extends ApiResponse {
  access_token: string;
  token_type: string;
}

export interface UploadResult extends ApiResponse {
  filename: string;
  text: string;
  char_count: number;
}

export interface HistoryItem {
  id: number;
  original_text: string;
  polished_text: string;
  operation_type: string;
  style?: string;
  created_at: string;
}

export interface HistoryListResult extends ApiResponse {
  data: HistoryItem[];
}

export interface ProgressData {
  progress: number;
  total: number;
  status: string;
  results?: string[];
  result?: PolishResult;
  error?: string;
}

export interface TaskResult {
  task_id: string;
  message: string;
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

export async function analyzeAiRisk(text: string): Promise<AnalyzeResult> {
  const response = await api.post<AnalyzeResult>('/anti-ai/analyze', { text });
  return response.data;
}

export async function batchPolish(
  texts: string[],
  style: PolishStyle = 'academic',
  aiProvider: string = 'zhipuai'
): Promise<BatchPolishResult> {
  const response = await api.post<BatchPolishResult>('/polish/batch', {
    texts,
    style,
    ai_provider: aiProvider,
  });
  return response.data;
}

export async function register(
  username: string,
  email: string,
  password: string
): Promise<User> {
  const response = await api.post<User>('/auth/register', {
    username,
    email,
    password,
  });
  return response.data;
}

export async function login(
  username: string,
  password: string
): Promise<TokenResult> {
  const response = await api.post<TokenResult>('/auth/login', {
    username,
    password,
  });
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

export async function getHistory(): Promise<HistoryListResult> {
  const response = await api.get<HistoryListResult>('/auth/history');
  return response.data;
}

export async function uploadFile(file: File): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<UploadResult>('/upload/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function polishTextWithProgress(
  text: string,
  style: PolishStyle = 'academic',
  aiProvider: string = 'zhipuai',
  onProgress?: (data: ProgressData) => void
): Promise<PolishResult> {
  const response = await api.post<TaskResult>('/polish/text-with-progress', {
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
          reject(new Error(data.error || '处理失败'));
        }
      } catch (e) {
        console.error('Failed to parse progress data:', e);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
      reject(new Error('进度连接失败'));
    };
  });
}
