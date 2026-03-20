import axios, { AxiosError } from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
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

export interface ApiError {
  error: string;
  retry_after?: number;
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
