import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

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

export async function polishText(
  text: string,
  style: string = 'academic',
  aiProvider: string = 'zhipuai'
): Promise<PolishResult> {
  const response = await api.post('/polish/text', {
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
  const response = await api.post('/anti-ai/process', {
    text,
    ai_provider: aiProvider,
  });
  return response.data;
}

export async function analyzeAiRisk(text: string) {
  const response = await api.post('/anti-ai/analyze', { text });
  return response.data;
}
