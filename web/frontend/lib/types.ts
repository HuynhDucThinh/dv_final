/**
 * Shared TypeScript interfaces cho toàn bộ frontend.
 * Tách từ các component để tránh circular imports và dễ tái sử dụng.
 */

// --- Chat Message ---
export interface DocumentChunk {
  content: string;
  metadata: {
    id?: string;
    source?: string;
    dieu?: string;
    khoan?: string;
    diem?: string;
    law?: string;
  };
}

// --- Chat Message Attachment (displayed as card in chat, text hidden from user) ---
export interface MessageAttachment {
  id: string;
  name: string;
  mimeType: string;
  publicUrl?: string;
  previewUrl?: string; // blob URL for images
  sizeBytes?: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;              // full content sent to LLM (may include extracted text)
  displayContent?: string;      // what user sees in the chat bubble
  attachments?: MessageAttachment[]; // file cards shown above the bubble
  contextUsed?: DocumentChunk[];
  feedback?: 1 | -1;
  processingStage?: 'idle' | 'analyzing' | 'searching' | 'selecting' | 'generating' | 'completed' | 'cancelled' | 'error';
}

// --- Chat Session ---
export interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: number;
  is_pinned?: boolean;
}

// --- Model ---
export interface AIModel {
  id: string;
  name: string;
  fullName: string;
  provider: InferenceProviderId;
}

export type InferenceProviderId = 'google' | 'huggingface' | 'ollama' | 'groq' | 'openai';
export type InferenceRoleId = 'answer' | 'rewriter' | 'summarizer';

export interface InferenceProvider {
  id: InferenceProviderId;
  name: string;
  requiresApiKey: boolean;
  deploymentSupported: boolean;
}

export interface InferenceRoleSetting {
  provider: InferenceProviderId;
  model: string;
}

export interface ProviderCredentialSetting {
  apiKey: string;
  remember: boolean;
}

export type ProviderCredentialSettings = Partial<Record<InferenceProviderId, ProviderCredentialSetting>>;
export type InferenceRoleSettings = Record<InferenceRoleId, InferenceRoleSetting>;

// --- API ---
export interface ChatApiRequest {
  messages: { role: string; content: string }[];
  model: string;
  category: string;
  temperature?: number;
  maxTokens?: number;
  topK?: number;
  candidateK?: number;
  cacheThreshold?: number;
  maxSubqueries?: number;
  historyMessages?: number;
  contextTokenBudget?: number;
  maxCitations?: number;
  llmTimeout?: number;
  streaming?: boolean;
  useHistoryForRewriter?: boolean;
  enableQueryRewriter?: boolean;
  enableReranker?: boolean;
  enableSemanticCache?: boolean;
  enableMemory?: boolean;
  inferenceConfig?: {
    credentials?: Partial<Record<InferenceProviderId, { apiKey?: string }>>;
    roles?: Partial<Record<InferenceRoleId, InferenceRoleSetting>>;
    useServerFallbacks?: boolean;
  };
}

export interface ChatApiResponse {
  text: string;
  contextUsed: DocumentChunk[];
}

// --- Feedback ---
export interface FeedbackPayload {
  message_id: string;
  session_id: string;
  user_query?: string;
  ai_response?: string;
  context_used?: DocumentChunk[];
  feedback_type: 1 | -1;
  reason?: string;
  comment?: string;
  model_used?: string;
  user_id?: string; // Better Auth user ID (optional, gắn nếu đã đăng nhập)
}

// --- Auth & User ---
export interface AuthUser {
  id: string;
  name: string | null;
  email: string;
  image?: string | null;
  avatarUrl?: string | null;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// --- User File (Supabase Storage) ---
export interface UserFile {
  id: string;
  userId: string;
  filename: string;
  storagePath: string;
  publicUrl: string;
  size: number;
  mimeType: string;
  createdAt: string;
}
