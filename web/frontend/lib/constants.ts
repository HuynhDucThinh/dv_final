/**
 * Hằng số dùng chung cho toàn frontend.
 * Tách từ ChatInterface.tsx và ProviderSelector.tsx.
 */
import type { AIModel, InferenceProvider } from './types';

export interface LawCategory {
  id: string;
  label: string;
}

export const ALL_LAWS_CATEGORY = 'all';

export type ChatStorageMode = 'postgres' | 'browser';

export const CHAT_STORAGE_MODE: ChatStorageMode =
  process.env.NEXT_PUBLIC_CHAT_STORAGE_MODE?.trim().toLowerCase() === 'browser'
    ? 'browser'
    : 'postgres';

// Các danh mục tài liệu phân tích.
export const LAW_CATEGORIES = [
  {
    id: ALL_LAWS_CATEGORY,
    label: 'Tất cả tài liệu',
  },
  {
    id: 'LKDBDS_2023',
    label: 'Dữ liệu Xe hơi',
  },
  {
    id: 'LTTPHS_2025',
    label: 'Phân tích Thị trường',
  },
  {
    id: 'LNO_2023',
    label: 'Báo cáo Bán hàng',
  },
  {
    id: 'LBVMT_2020',
    label: 'Thông số Kỹ thuật',
  },
  {
    id: 'LXD_2014',
    label: 'Đánh giá Xe',
  },
  {
    id: 'LDD_2024',
    label: 'Chính sách Bảo hành',
  },
  {
    id: 'LCC_2024',
    label: 'Hướng dẫn Sử dụng',
  },
  {
    id: 'BLTTDS_2015',
    label: 'Dữ liệu Khách hàng',
  },
] as const satisfies readonly LawCategory[];

// Danh sách model AI hỗ trợ
export const AI_PROVIDERS: InferenceProvider[] = [
  { id: 'google', name: 'Google AI Studio', requiresApiKey: true, deploymentSupported: true },
  { id: 'huggingface', name: 'HuggingFace Router', requiresApiKey: true, deploymentSupported: true },
  { id: 'groq', name: 'Groq Cloud', requiresApiKey: true, deploymentSupported: true },
  { id: 'openai', name: 'OpenAI', requiresApiKey: true, deploymentSupported: true },
  { id: 'ollama', name: 'Ollama', requiresApiKey: false, deploymentSupported: false },
];

export const AI_MODELS: AIModel[] = [
  { id: 'gemini-1.5-pro', provider: 'google', name: 'Gemini 1.5 Pro', fullName: 'Gemini 1.5 Pro' },
  { id: 'gemini-1.5-flash', provider: 'google', name: 'Gemini 1.5', fullName: 'Gemini 1.5 Flash' },
  { id: 'gpt-4o-mini', provider: 'openai', name: 'GPT-4o Mini', fullName: 'GPT-4o Mini' },
  { id: 'gpt-4o', provider: 'openai', name: 'GPT-4o', fullName: 'GPT-4o' },
  { id: 'llama-3.3-70b-versatile', provider: 'groq', name: 'Llama 3.3 70B', fullName: 'Llama 3.3 70B (Groq)' },
  { id: 'llama-3.1-8b-instant', provider: 'groq', name: 'Llama 3.1 8B', fullName: 'Llama 3.1 8B Instant (Groq)' },
  { id: 'llama3.2', provider: 'ollama', name: 'Llama 3.2 Local', fullName: 'Llama 3.2 3B (Ollama)' },
  { id: 'llama3.1', provider: 'ollama', name: 'Llama 3.1 Local', fullName: 'Llama 3.1 8B (Ollama)' },
  { id: 'qwen2.5:7b-instruct', provider: 'ollama', name: 'Qwen Local', fullName: 'Qwen 2.5 7B (Ollama)' },
];

// Model mặc định
export const DEFAULT_MODEL = 'gemini-2.5-flash';

// LocalStorage keys
export const STORAGE_KEYS = {
  sessions: 'vietcar_sessions',
  messages: 'vietcar_messages',
  activeSessionId: 'vietcar_active_session_id',
} as const;
